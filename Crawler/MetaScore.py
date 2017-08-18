import re
from urllib.request import Request, urlopen
from urllib import parse
from bs4 import BeautifulSoup
from Crawler.Database.TmpMovies import TmpMovies
from Crawler.Database.Person import Person
from Crawler.Database.Movie import Movie
import logging
import pickle as pk

# URL Constants
BASIC_URL = 'http://www.metacritic.com'
MOVIES_LIST = 'http://www.metacritic.com/browse/movies/title/dvd'
SEARCH_META_SCORE_URL = 'http://www.metacritic.com/search/all/%s/results'
PERSON_FILTER_OPTION = "?filter-options=movies&sort_options=user_score&num_items=100"

# Files constants
PERSON_BACKUP = "../Files/Backups/persons_backup.txt"
MOVIES_BACKUP = "../Files/Backups/movies_backup.txt"
PERSON_LINKS_BACKUP = "../Files/Backups/persons_links.txt"
LOG_FILE = "../Files/Logs/logger.txt"
PERSON_INSERT_FILE = "../Files/Outputs/persons_insert.sql"
MOVIE_PERSONS_INSERT = "../Files/Outputs/movie_persons_insert.sql"

# Other constants
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
STARTING_INDEX = 2
MAX_YEAR = 2016
MIN_YEAR = 2014

# Starting code
log = open(LOG_FILE, 'w')  # backwards compatibility


#######################################################################################
############################# Creating the TmpMovie table #############################
#######################################################################################
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
            lst.append(TmpMovies(title, release_date, run_time, score, user_score, genres))
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


def get_tmp_movies():
    try:
        log.write("Starting process\n")
        lst = parse_metascore()
        log.write("Starting insertion\n")
        TmpMovies.create_insert(lst)
    finally:
        log.write("DONE")


#######################################################################################
############################# Creating the person table ###############################
#######################################################################################
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
        query = SEARCH_META_SCORE_URL % q
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
            logging.exception('Exception query_persons\n')
            continue
    return res


def get_persons_union_insert(persons_list):
    persons = query_persons(persons_list)
    output = 'INSERT INTO persons\n'
    for p in persons:
        output += p.get_insert_from_select() + " union all\n"
    f = open(PERSON_INSERT_FILE, "wb")
    f.write((output[:-11] + ";").encode("utf8"))
    f.close()


#######################################################################################
####################### Extracting persons data from meta score #######################
## This is a patch since imdb persons and meta critic persons may have different names.
## So, this part will handle the recreation of the persons data
#######################################################################################
persons_links = []


def create_meta_person_insert(output_file, persons_link_file):
    movies = []
    try:
        movies = Movie.extract_backup(MOVIES_BACKUP)
    except:
        Movie.create_backup_file(MOVIES_BACKUP)
        try:
            movies = Movie.extract_backup(MOVIES_BACKUP)
        except:
            raise
    
    # Scanning movie pages and extracting from each the persons data
    for movie in movies[1:3]:
        handle_movie_search(movie)

    fp = None
    try:
        fp = open(output_file, "wb")
        Movie.create_persons_insert(movies, fp)
    except:
        logging.exception("Error trying to write movies persons to file")
    finally:
        if fp is not None:
            fp.close()
    extract_persons_links_backup(persons_link_file)


def handle_movie_search(movie):
    try:
        search_url = SEARCH_META_SCORE_URL % parse.quote(movie.title)
        req = Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        search_page = BeautifulSoup(urlopen(req).read(), "html.parser")

        # Parsing page - assuming all of the first results are what we are looking for
        best_match_li = search_page.find("li", "result first_result")
        # if best_match_li.find("div", "result_type").text.strip().lower() != "movie":
        #     print("x")
        movie_link = best_match_li.find("a", href=True)['href']
        handle_movie_page(BASIC_URL + movie_link, movie)
    except:
        logging.exception(("Exception in parsing movie: " + movie.title + " url: " + search_url).encode("utf8"))


def handle_movie_page(movie_url, cur_movie):
    try:
        req = Request(movie_url + "/details", headers={'User-Agent': 'Mozilla/5.0'})
        movie_page = BeautifulSoup(urlopen(req).read(), "html.parser")

        # Parsing page - assuming all of the first results are what we are looking for
        movie_credits = movie_page.find("div", "credits_list")

        # Getting persons lists
        cur_movie.directors = extract_persons(movie_credits, "director")
        cur_movie.writers = extract_persons(movie_credits, "writer")
        cur_movie.stars = extract_persons(movie_credits, "principal")
    except:
        logging.exception(("Exception in parsing movie url: " + movie_url + "").encode("utf8"))


def extract_persons(credits_div, regexp_search):
    lst = []
    cur_tbl = credits_div.find(summary=re.compile(regexp_search, re.IGNORECASE))
    for cur_row in cur_tbl.tbody.find_all("tr"):
        person_link = cur_row.find("a", href=True)
        lst.append(person_link.text.strip())
        persons_links.append((person_link.text.strip(), person_link['href'][:person_link['href'].index("?")]))
    return lst


def persons_links_backup(file_name):
    # Trying to write persons_links to file
    fp = None
    try:
        fp = open(file_name, "wb")
        pk.dump(persons_links, fp)
    except:
        logging.exception("Error trying to write person_links")
    finally:
        if fp is not None:
            fp.close()


def extract_persons_links_backup(file_name):
    try:
        backup = open(file_name, "rb")
        rows = pk.load(backup)
        backup.close()
        return rows
    except:
        raise


# "Main"
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)


######### Getting movies #########
# get_tmp_movies()

######### Getting the persons ##########
#Person.create_persons_backup_file(PERSON_BACKUP)
#Person.create_persons_backup_file(PERSON_BACKUP, missing=True)
#rows = Person.extract_persons_backup(PERSON_BACKUP)
#get_persons_union_insert(rows)

#create_meta_person_insert(MOVIE_PERSONS_INSERT, PERSON_LINKS_BACKUP)
print(extract_persons_links_backup(PERSON_LINKS_BACKUP))
