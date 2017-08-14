from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib import parse
from Crawler.Movie import MetaCriticMovie
from Crawler.Movie import Movie
import sys
import pickle as fp

#SEARCH_URL = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=all"
SEARCH_URL = "http://www.imdb.com/find?ref_=nv_sr_fn&%s&s=all"
BASE_URL = "http://www.imdb.com"
log = open('logger.txt', 'w')


def parse_movie_page(link, cur_movie):
    try:
        p_req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        page = BeautifulSoup(urlopen(p_req).read(), "html.parser")
        rate_type = page.find("div","title_wrapper").find(itemprop="contentRating")
        if rate_type is not None:
            cur_movie.rated = rate_type.get("content")
        imdb_rating = page.find("div","ratingValue")
        if imdb_rating is not None:
            cur_movie.imdb_score = imdb_rating.span.text

        # Credit summary data
        credits_section = page.find("div", "plot_summary")
        if credits_section is not None:
            # Handling director & writers
            directors = []
            writers = []
            for director in credits_section.find_all(itemprop="director"):
                directors.append(director.span.text)
            for writer in credits_section.find_all(itemprop="creator"):
                writers.append(writer.span.text)
            cur_movie.directors = directors
            cur_movie.writers = writers

        # Main actors
        actors = []
        actors_table = page.find(id="titleCast")
        if actors_table is not None:
            actors_table = actors_table.table.find_all("tr")
            for actor_index in range(1, len(actors_table)):
                if actor_index > 5:
                    break
                tname = actors_table[actor_index].find("span", "itemprop").text
                actors.append(tname)
        cur_movie.stars = actors

        # Box office data
        box_office_section = page.find("h3", text="Box Office")
        ## TODO:: Check if can remove the $ sign from all data

        if box_office_section is not None:

            # Some blocks can be missed
            budget = 0
            gross = 0
            opening_weekend = 0
            div_elem = box_office_section.findNext("div")
            i = 0
            while i < 3:
                if div_elem.h4.text[:-1] is not None and div_elem.h4.text[:-1] == "Budget":
                    budget = div_elem.h4.nextSibling.strip()[1:].replace(',', '')
                elif div_elem.h4.text[:-1] is not None and div_elem.h4.text[:-1] == "Gross":
                    gross = div_elem.h4.nextSibling.strip()[1:].replace(',', '')
                elif div_elem.h4.text[:-1] is not None and div_elem.h4.text[:-1] == "Opening Weekend":
                    num_ending = div_elem.h4.nextSibling.strip().index(" ")
                    opening_weekend = div_elem.h4.nextSibling.strip()[1:num_ending].replace(',', '')
                else:
                    break
                i += 1
                div_elem = div_elem.findNext("div")
            cur_movie.budget = budget
            cur_movie.opening_weekend = opening_weekend
            cur_movie.gross = gross

        languages = []
        for cur_lang in page.find(text="Language:").parent.parent.find_all("a"):
            languages.append(cur_lang.text)
        cur_movie.languages = languages
        counties = []
        for cur_country in page.find(text="Country:").parent.parent.find_all("a"):
            counties.append(cur_country.text)
        cur_movie.countries = counties
    except:
        print(sys.exc_info()[0])
        log.write("Link:" + link + ". \n" + sys.exc_info()[0] + "\n\n")
        raise


def search_and_parse(movies, movie_list):
    for movie in movies:
        q = parse.urlencode({"q": movie.get("title")})
        query = SEARCH_URL % q
        log.write("Starting: " + query + "\n")
        try:
            req = Request(query, headers={'User-Agent': 'Mozilla/5.0'})
            main = BeautifulSoup(urlopen(req).read(), "html.parser")
            for section in main.find_all("div", "findSection"):
                if section.h3 is not None and section.h3.text == 'Titles':
                    try:
                        movie_link = section.find("td", "result_text").find("a", href=True)['href']
                        full_movie = Movie()
                        full_movie.copy_from_meta(movie)
                        parse_movie_page(BASE_URL + movie_link, full_movie)
                        movie_list.append(full_movie)
                        log.write("Done Successfully\n")
                        break
                    except:
                        log.write("Error!\n")
                        break
        except:
            log.write("Error opening a url.\n")
            continue


def create_backup_file():
    rows = MetaCriticMovie.get_all_rows()
    backup = open("backup.txt", "wb")
    fp.dump(rows, backup)
    backup.close()


def extract_backup():
    backup = open("backup.txt", "rb")
    rows = fp.load(backup)
    backup.close()
    return rows


def main():
    try:
        lst = []
        log.write("starting\n")

        # Backup section to save network transportation
        #create_backup_file()
        rows = extract_backup()

        # Handling movies
        o = open("out.txt", "wb")
        search_and_parse(rows[:200], lst)
        print("starting 2:\n")
        search_and_parse(rows[200:400], lst)
        print("starting 3:\n")
        search_and_parse(rows[400:600], lst)
        print("starting 4:\n")
        search_and_parse(rows[600:800], lst)
        print("starting 5:\n")
        search_and_parse(rows[800:1000], lst)
        print("starting 6:\n")
        search_and_parse(rows[1000:], lst)
        Movie.create_insert(lst, o)
        o.close()

    except:
        raise
    finally:
        log.write("ending\n")
        log.close()

main()
