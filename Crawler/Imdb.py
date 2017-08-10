from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from Crawler.Movie import Movie
import re

SEARCH_URL = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=all"
log = open('logger.txt', 'w')


def parse_movie_page(page):

def search_and_parse(movies):
    for movie in movies:
        query = SEARCH_URL.format(movie.title)
        req = Request(query, headers={'User-Agent': 'Mozilla/5.0'})
        main = BeautifulSoup(urlopen(req).read(), "html.parser")
        for section in main.find_all("div", "findSection"):
            if section.h3 is not None and section.h3.text == 'Title':
                movie_link = section.find("td", "result_text").find("a", href=True)['href']


# Main
query = SEARCH_URL.format("Spider-Man")
req = Request(query, headers={'User-Agent': 'Mozilla/5.0'})
main = BeautifulSoup(urlopen(req).read(), "html.parser")
for section in main.find_all("div", "findSection"):
    if section.h3 is not None and section.h3.text == 'Title':
        movie_link = section.find("td", "result_text").find("a", href=True)['href']


print(main)

