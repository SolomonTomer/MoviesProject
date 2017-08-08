from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from Crawler.Movie import Movie
import re

SEARCH_URL = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=all"
log = open('logger.txt', 'w')


def search_and_paras(movies):
    for movie in movies:
        query = movie
        req = Request(MOVIES_LIST, headers={'User-Agent': 'Mozilla/5.0'})
    main_page = BeautifulSoup(urlopen(req).read(), "html.parser")
    links = main_page.find_all("div", "title_bump")[0].find_all("a", "link_tab", href=True)
    for i in range(STARTING_INDEX, len(links)):
        extract_movies_list(BASIC_URL + links[i]['href'], 0, movies_list)
    return movies_list


# Main
log.write("Starting process\n")
lst = parse_metascore()
log.write("Starting insertion\n")
mv = Movie()
mv.insert_to_temp(lst)
log.write("DONE")
