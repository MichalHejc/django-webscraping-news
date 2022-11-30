from django.shortcuts import render

from bs4 import BeautifulSoup
import requests


all_articles = []


class Article:
    """ Signle article object, with title text and hypertext reference """

    def __init__(self, text, href):
        self.text = text
        self.href = href


class Portal:
    """ Class for an article creation from specific news website """

    def __init__(self, homepage):
        self.homepage = homepage

    def get_response(self):
        response = requests.get(self.homepage).text
        return response

    def get_soup(self):
        soup = BeautifulSoup(self.get_response(), "html.parser")
        return soup

    def get_articles(self, article_html_class):
        """ Gets articles from specific website- based on html class, that finds which element is an article """

        articles = self.get_soup().find_all(class_=article_html_class)
        return articles

    def create_article_objects(self, article_list):
        """ Creates article objects from portal article list """

        for article in article_list:
            text = article.getText().strip()
            href = article.get("href")
            new_article = Article(text, href)
            all_articles.append(new_article)


class PortalAktualne(Portal):
    """ Portal subclass with specific methods for website Aktualne.cz """

    def get_articles(self, section_opener_class, article_html_class):
        """ Aktualne.cz has specific html class for first article on each page """

        opener = self.get_soup().find_all(class_=section_opener_class)
        articles = opener + self.get_soup().find_all(class_=article_html_class)
        return articles

    def create_article_objects(self, article_list):
        """ Aktualne.cz has specific class for title text and href without root domain"""

        for article in article_list:
            text = article.get("data-ga4-title")
            href = self.homepage + article.a.get("href")
            new_article = Article(text, href)
            all_articles.append(new_article)


class PortalDenik(Portal):
    """ Portal subclass with specific methods for website Denik.cz """

    def create_article_objects(self, article_list):
        """ Denik.cz has href without root domain and title text in h3 selector """
        
        for article in article_list:
            text = article.h3.text.strip()
            href = self.homepage + article.a.get("href")
            new_article = Article(text, href)
            all_articles.append(new_article)


seznam = Portal("https://www.seznam.cz/")
seznam_articles = seznam.get_articles("article__title")
seznam.create_article_objects(seznam_articles)

idnes = Portal("https://www.idnes.cz/zpravy")
idnes_articles = idnes.get_articles("art-link")
idnes.create_article_objects(idnes_articles)

aktualne = PortalAktualne("https://zpravy.aktualne.cz/")
aktualne_articles = aktualne.get_articles("section-opener", "small-box")
aktualne.create_article_objects(aktualne_articles)

aktualne_second_page = PortalAktualne("https://zpravy.aktualne.cz/?offset=20/")
aktualne_articles = aktualne.get_articles("section-opener", "small-box")
aktualne.create_article_objects(aktualne_articles)

denik = PortalDenik("https://www.denik.cz/zpravy/")
denik_articles = denik.get_articles("box-article")
denik.create_article_objects(denik_articles)


for ind, art in enumerate(all_articles, 1):
    print(str(ind) + " " + art.text)
    print(art.href)