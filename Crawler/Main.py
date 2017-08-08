from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from Crawler.Movie import Movie
import re

BASIC_URL = 'http://www.metacritic.com'
MOVIES_LIST = 'http://www.metacritic.com/browse/movies/title/dvd'

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
STARTING_INDEX = 2
MAX_YEAR = 2016
MIN_YEAR = 2014

log = open('logger.txt', 'w')

def extract_movies_from_page(page, lst):
    movies = page.find_all("tr", "summary_row")
    for movie in movies:
        try:
            date = movie.find("td", "date_wrapper").span.text.replace(',', '').split(' ')
            date[2] = int(date[2])
            if date[2] > MAX_YEAR or date[2] < MIN_YEAR:
                continue
            score = movie.find("td", "score_wrapper").text.strip()
            title = movie.find("td", "title_wrapper").text.strip()
            month_num = MONTHS.index(date[0].lower()) + 1
            date[0] = month_num
            print(title, score, date[1] + "/" + str(date[0]) + "/" + str(date[2]))
            lst.append((title, score, date[1] + "/" + str(date[0]) + "/" + str(date[2])))
        except:
            log.write(movie + "\n")

# ALL TITLES - page.find_all("div", "content_after_header")[0].find_all("a", href=re.compile("(?=^/movie/.*)(?=(?!^/movie/.*/.*))"))


def extract_movies_list(url, page_number, lst, max_pages=0):
    req = Request(url + "?page=" + str(page_number), headers={'User-Agent': 'Mozilla/5.0'})
    soup = ''

    if max_pages == 0:
        soup = BeautifulSoup(urlopen(req).read(), "html.parser")
        max_pages = len(soup.find_all("li", "page"))
    if max_pages > page_number:
        if page_number != 0:
            soup = BeautifulSoup(urlopen(req).read(), "html.parser")
        extract_movies_from_page(soup, lst)
        extract_movies_list(url, page_number + 1, lst, max_pages)
    else:
        return


def parse_metascore():
    movies_list = []
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
