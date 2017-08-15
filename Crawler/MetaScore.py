import re
from urllib.request import Request, urlopen
from urllib import parse
from bs4 import BeautifulSoup
from Crawler.Database.Movie import MetaCriticMovie
from Crawler.Database.Person import Person
import pickle as fp
import logging

BASIC_URL = 'http://www.metacritic.com'
MOVIES_LIST = 'http://www.metacritic.com/browse/movies/title/dvd'
SEARCH_PERSON_URL = 'http://www.metacritic.com/search/all/%s/results'
PERSON_FILTER_OPTION = "?filter-options=movies&sort_options=user_score&num_items=100"


MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
STARTING_INDEX = 2
MAX_YEAR = 2016
MIN_YEAR = 2014
PERSON_BACKUP = "../Files/persons_backup.txt"
LOG_FILE = "../Files/logger.txt"
PERSON_INSERT_FILE = "../Files/persons_insert.sql"

log = open(LOG_FILE, 'w')  # backwards compatibility


def extract_movies_from_page(page, lst):
    movies = page.find_all("tr", re.compile("summary_row|details_row"))
    i = 0
    m_len = len(movies)
    while i < m_len:
        movie = movies[i]
        movie_extended = movies[i + 1]
        i += 2
    # for movie in movies:
        try:
            date = movie.find("td", "date_wrapper").span.text.replace(',', '').split(' ')
            date[2] = int(date[2])
            if date[2] > MAX_YEAR or date[2] < MIN_YEAR:
                continue

            # Extracting data
            score = movie.find("td", "score_wrapper").text.strip()
            title = movie.find("td", "title_wrapper").text.strip()
            month_num = MONTHS.index(date[0].lower()) + 1
            date[0] = month_num
            release_date = date[1] + "/" + str(date[0]) + "/" + str(date[2])

            # Extended dataset
            user_score = movie_extended.find("div", "userscore_text").text.strip()
            user_score = user_score[(user_score.index("\n") + 1):]
            run_time = movie_extended.find("div", "runtime").text.strip()
            run_time = run_time[(run_time.index("\n") + 1):-4]
            genres = movie_extended.find("div", "genres").text.split()[1:]
            for j in range(len(genres)):
                genres[j] = genres[j].replace(",", "")
            genres.sort()
            lst.append(MetaCriticMovie(title, release_date, run_time, score, user_score, genres))
           # lst.append((title, score, date[1] + "/" + str(date[0]) + "/" + str(date[2])))
        except:
            try:
                log.write(movie)
            except TypeError:
                log.write("Error")

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


def get_metascore_movies():
    try:
        log.write("Starting process\n")
        lst = parse_metascore()
        log.write("Starting insertion\n")
        MetaCriticMovie.create_insert(lst)
    finally:
        log.write("DONE")


def create_persons_backup_file(actors=True, directors=True, writers=True, missing=False):
    if missing:
        rows = Person.get_missing_values_people()
    else:
        rows = Person.get_persons_in_db(actors, directors, writers)
    backup = open(PERSON_BACKUP, "wb")
    fp.dump(rows, backup)
    backup.close()


def extract_persons_backup():
    backup = open(PERSON_BACKUP, "rb")
    rows = fp.load(backup)
    backup.close()
    return rows


def handle_person_page(person_url, person_name):
    try:
        req = Request(person_url + PERSON_FILTER_OPTION, headers={'User-Agent': 'Mozilla/5.0'})
        person_page = BeautifulSoup(urlopen(req).read(), "html.parser")
        person = Person(person_name)

        # Extracting meta critic data
        summary_table = person_page.find("table", "profile_score_summary personscore_summary")
        person.meta_critic_avg_career = summary_table.find("tr", "review_average").find("span").text
        person.meta_critic_highest = summary_table.find("tr", re.compile("highest_review")).find("td", "summary_score").find("span").text
        person.meta_critic_lowest = summary_table.find("tr", re.compile("lowest_review")).find("td","summary_score").find("span").text

        # Extracting user data
        user_table_rows = person_page.find("table", re.compile("person_credits")).tbody.find_all("tr")
        person.meta_user_highest = user_table_rows[0].find("td", "score").span.text
        last_index = 0
        table_size = len(user_table_rows) - 1
        for i in range(table_size, -1, -1):
            if user_table_rows[i].find("td", "score").span.text != "tbd":
                last_index = i
                break
        person.meta_user_median = user_table_rows[int(last_index/2)].find("td", "score").span.text
        person.meta_user_lowest = user_table_rows[last_index].find("td", "score").span.text
    except:
        log.write("Error handle_person_page: " + person_url + " \n")
        person = None
    finally:
        return person


def query_persons(persons):
    res = []
    for person in persons:
        q = parse.quote(person.name)
        query = SEARCH_PERSON_URL % q
        try:
            req = Request(query, headers={'User-Agent': 'Mozilla/5.0'})
            search_page = BeautifulSoup(urlopen(req).read(), "html.parser")

            # Parsing page - assuming all of the first results are what we are looking for
            best_match = search_page.find("li", "result first_result")
            person_link = best_match.find("a", href=True)['href']
            new_person = handle_person_page(BASIC_URL + person_link, person.name)
            if new_person.name not in res:
                res.append(new_person)
        except:
            logging.exception('Exception query_persons')
            continue
    return res


def get_persons_union_insert(persons_list):
    persons = query_persons(persons_list)
    output = 'INSERT INTO persons\n'
    for p in persons:
        output += p.get_insert_from_select() + " union all\n"
    f = open(PERSON_INSERT_FILE, "wb")
    f.write((output + ";").encode("utf8"))
    f.close()


######### Getting movies #########
# get_metascore_movies()

######### Getting the persons ##########
# create_persons_backup_file()
# create_persons_backup_file(missing=True)
rows = extract_persons_backup()
# rows = Person.get_persons_in_db(True, True, True)
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)
get_persons_union_insert(rows)
