import sys
from Crawler.Database.Database import Database
import pickle as fp


class Movie:

    # Constants
    movies_union_sql = 'select "{}", STR_TO_DATE("{}", "%Y-%m-%d"), "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}" ' \
                       'from dual'
    table_connector_union_sql = 'select "{}", "{}" from dual '
    get_all_sql = "select m1.*, dir.director, act.actor, wrt.writer " \
                  "from movies m1, " \
                  "(select m.title, group_concat(d.director SEPARATOR ', ') as director " \
                  " from movies m, movie_directors d where m.title = d.title " \
                  " group by m.title) dir," \
                  "(select m.title, group_concat(d.actor SEPARATOR ', ') as actor " \
                  " from movies m, movie_stars d where m.title = d.title" \
                  " group by m.title) act," \
                  "(select m.title, group_concat(d.writer SEPARATOR ', ') as writer " \
                  " from movies m, movie_writers d where m.title = d.title" \
                  " group by m.title) wrt" \
                  " where m1.title = dir.title and m1.title = act.title and m1.title = wrt.title"

    movie_directors_sql = 'select director from movie_directors where title = %s'
    movie_writers_sql = 'select writer from movie_writers where title = %s'
    movie_actors_sql = 'select actor from movie_stars where title = %s'

    def __init__(self, title=None):
        self.title = title
        self.release_date = None
        self.rated = None
        self.run_time = 0
        self.budget = 0
        self.opening_weekend = 0
        self.gross = 0
        self.imdb_score = 0
        self.meta_score = 0
        self.user_score = 0
        self.genres = []
        self.countries = []
        self.languages = []
        self.directors = []
        self.writers = []
        self.stars = []

    def copy_from_meta(self, meta_movie):
        self.title = meta_movie.get("title")
        self.release_date = meta_movie.get("release_date")
        self.rated = None
        self.run_time = meta_movie.get("run_time")
        self.budget = 0
        self.opening_weekend = 0
        self.gross = 0
        self.imdb_score = 0
        self.meta_score = meta_movie.get("meta_score")
        self.user_score = meta_movie.get("user_score")
        self.genres = meta_movie.get("genres").split(", ")
        self.countries = []
        self.languages = []
        self.directors = []
        self.writers = []
        self.stars = []

    def get_persons_data(self, conn):
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute(Movie.movie_directors_sql, self.title)
        self.directors = [item["director"] for item in cursor.fetchall()]
        cursor.execute(Movie.movie_writers_sql, self.title)
        self.writers = [item["writer"] for item in cursor.fetchall()]
        cursor.execute(Movie.movie_actors_sql, self.title)
        self.stars = [item["actor"] for item in cursor.fetchall()]

    @staticmethod
    def copy_from_row(row):
        self = Movie()
        self.title = row.get("title")
        self.release_date = row.get("release_date")
        self.rated = row.get("rated")
        self.run_time = row.get("run_time")
        self.budget = row.get("budget")
        self.opening_weekend = row.get("opening_weekend")
        self.gross = row.get("gross")
        self.imdb_score = row.get("imdb_score")
        self.meta_score = row.get("meta_score")
        self.user_score = row.get("user_score")
        self.genres = []
        self.countries = []
        self.languages = []
        self.directors = row.get("director").split(', ')
        self.writers = row.get("writer").split(', ')
        self.stars = row.get("actor").split(', ')
        return self

    @staticmethod
    def get_all_rows():
        try:
            conn = Database().get_connection()
            cursor = conn.cursor()
            cursor.execute(Movie.get_all_sql)
            results = cursor.fetchall()
            return [Movie.copy_from_row(row) for row in results]
        except:
            raise
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def create_backup_file(file_name):
        rows = Movie.get_all_rows()
        backup = open(file_name, "wb")
        fp.dump(rows, backup)
        backup.close()

    @staticmethod
    def extract_backup(file_name):
        try:
            backup = open(file_name, "rb")
            rows = fp.load(backup)
            backup.close()
            return rows
        except:
            raise

    @staticmethod
    def generate_union(lst, title, add_union):
        res = ''
        for ind in range(len(lst)):
            # Wasn't checked - change due to some movies with missing values
            if add_union and ind == 0:
                res += " union all \n"
            res += Movie.table_connector_union_sql.format(title, lst[ind])
            if ind + 1 != len(lst):
                res += " union all \n"
        return res

    @staticmethod
    def create_persons_insert(lst, output=None):
        directors_insert = 'insert into movie_directors \n'
        writers_insert = 'insert into movie_writers \n'
        stars_insert = 'insert into movie_stars \n'
        not_first_dir = False
        not_first_writer = False
        not_first_star = False
        for i in range(len(lst)):
            self = lst[i]
            if len(self.directors) != 0:
                directors_insert += Movie.generate_union(self.directors, self.title, not_first_dir)
                not_first_dir = True
            if len(self.writers) != 0:
                writers_insert += Movie.generate_union(self.writers, self.title, not_first_writer)
                not_first_writer = True
            if len(self.stars) != 0:
                stars_insert += Movie.generate_union(self.stars, self.title, not_first_star)
                not_first_star = True

        if output is not None:
            output.write("#DIRECTORS\n".encode("utf8"))
            output.write((directors_insert + ";").encode("utf8"))
            output.write("\n#WRITERS\n".encode("utf8"))
            output.write((writers_insert + ";").encode("utf8"))
            output.write("\n#STARS\n".encode("utf8"))
            output.write((stars_insert + ";").encode("utf8"))
        else:
            print("#DIRECTORS\n")
            print(directors_insert + ";")
            print("#WRITERS\n")
            print(writers_insert + ";")
            print("#STARS\n")
            print(stars_insert + ";")

    @staticmethod
    def create_insert(lst, output=None):
        movies_insert = 'insert into movies \n'
        genres_insert = 'insert into movie_genres \n'
        countries_insert = 'insert into movie_countries \n'
        languages_insert = 'insert into movie_languages \n'
        directors_insert = 'insert into movie_directors \n'
        writers_insert = 'insert into movie_writers \n'
        stars_insert = 'insert into movie_stars \n'
        for i in range(len(lst)):
            self = lst[i]
            movies_insert += Movie.movies_union_sql.format(self.title, self.release_date, self.rated, self.run_time, self.budget,
                                                    self.opening_weekend, self.gross, self.imdb_score,
                                                    self.meta_score, self.user_score)
            genres_insert += Movie.generate_union(self.genres, self.title, False if i == 0 else True)
            countries_insert += Movie.generate_union(self.countries, self.title, False if i == 0 else True)
            languages_insert += Movie.generate_union(self.languages, self.title, False if i == 0 else True)
            directors_insert += Movie.generate_union(self.directors, self.title, False if i == 0 else True)
            writers_insert += Movie.generate_union(self.writers, self.title, False if i == 0 else True)
            stars_insert += Movie.generate_union(self.stars, self.title, False if i == 0 else True)

            if i + 1 != len(lst):
                movies_insert += " union all \n"

        # Removing "None"
        movies_insert = movies_insert.replace('"None"', 'NULL')

        if output is not None:
            output.write("#MOVIES\n".encode("utf8"))
            output.write((movies_insert + ";").encode("utf8"))
            output.write("\n#GENRES\n".encode("utf8"))
            output.write((genres_insert + ";").encode("utf8"))
            output.write("\n#COUNTRIES\n".encode("utf8"))
            output.write((countries_insert + ";").encode("utf8"))
            output.write("\n#LANGUAGES\n".encode("utf8"))
            output.write((languages_insert + ";").encode("utf8"))
            output.write("\n#DIRECTORS\n".encode("utf8"))
            output.write((directors_insert + ";").encode("utf8"))
            output.write("\n#WRITERS\n".encode("utf8"))
            output.write((writers_insert + ";").encode("utf8"))
            output.write("\n#STARS\n".encode("utf8"))
            output.write((stars_insert + ";").encode("utf8"))
        else:
            print("#MOVIES\n")
            print(movies_insert + ";")
            print("#GENRES")
            print(genres_insert+ ";")
            print("#COUNTRIES\n")
            print(countries_insert + ";")
            print("#LANGUAGES\n")
            print(languages_insert + ";")
            print("#DIRECTORS\n")
            print(directors_insert + ";")
            print("#WRITERS\n")
            print(writers_insert + ";")
            print("#STARS\n")
            print(stars_insert + ";")
