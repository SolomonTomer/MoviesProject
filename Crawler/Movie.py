import sys
from Crawler.Database import Database


class MetaCriticMovie:
    raw_sql = 'select "{}", STR_TO_DATE("{}", "%d/%m/%Y"), "{}", "{}", "{}", "{}" from dual'
    get_all_sql = 'select * from movie_tmp'
    get_movie_by_title = "select * from movie_tmp where title= %s"

    def __init__(self, title, release_date, run_time, meta_score, user_score, genres):
        self.title = title
        self.release_date = release_date
        self.run_time = run_time
        self.meta_score = meta_score
        self.user_score = user_score
        self.genres = genres

    @staticmethod
    def get_by_title(title):
        try:
            conn = Database().get_connection()
            cursor = conn.cursor()
            cursor.execute(MetaCriticMovie.get_movie_by_title, title)
            results = cursor.fetchall()
            return results
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    @staticmethod
    def create_insert(lst):
        union = ''
        for i in range(len(lst)):
            self = lst[i]
            union += MetaCriticMovie.raw_sql.format(self.title, self.release_date, self.run_time,
                                                    self.meta_score, self.user_score, ', '.join(self.genres))
            if i + 1 != len(lst):
                union += " union all \n"
        print(union)

    @staticmethod
    def get_all_rows():
        results = ''
        try:
            conn = Database().get_connection()
            cursor = conn.cursor()
            cursor.execute(MetaCriticMovie.get_all_sql)
            results = cursor.fetchall()
            return results
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise


class Movie:

    def __init__(self):
        self.title = None
        self.release_date = None
        self.rated = None
        self.run_time = 0
        self.country = []
        self.language = []
        self.budget = 0
        self.opening_weekend = 0
        self.gross = 0
        self.imdb_score = 0
        self.meta_score = 0
        self.user_score = 0
        self.genres = []
        self.director = []
        self.writer = []
        self.stars = []

    def copy_from_row(self, row):
        self.title = row[0]
        self.release_date = row[2]
        self.rated = None
        self.run_time = 0
        self.country = []
        self.language = []
        self.budget = 0
        self.opening_weekend = 0
        self.gross = 0
        self.imdb_score = 0
        self.meta_score = row[1]
        self.user_score = 0
        self.genres = []
        self.director = []
        self.writer = []
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

    movies_union_sql = 'select "{}", STR_TO_DATE("{}", "%Y-%m-%d"), "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}" ' \
                       'from dual'
    table_connector_union_sql = 'select "{}", "{}" from dual '

    @staticmethod
    def generate_union(lst, title, add_union):
        res = ''
        if add_union:
            res += " union all \n"
        for ind in range(len(lst)):
            res += Movie.table_connector_union_sql.format(title, lst[ind])
            if ind + 1 != len(lst):
                res += " union all \n"
        return res

    @staticmethod
    def create_insert(lst):
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
            #
            # for g in self.genres:
            #     genres_insert += Movie.table_connector_union_sql.format(self.title, g)
            # for g in self.countries:
            #     countries_insert += Movie.table_connector_union_sql.format(self.title, g)
            # for g in self.languages:
            #     languages_insert += Movie.table_connector_union_sql.format(self.title, g)
            # for g in self.directors:
            #     directors_insert += Movie.table_connector_union_sql.format(self.title, g)
            # for g in self.writers:
            #     writers_insert += Movie.table_connector_union_sql.format(self.title, g)
            # for g in self.stars:
            #     stars_insert += Movie.table_connector_union_sql.format(self.title, g)

            if i + 1 != len(lst):
                movies_insert += " union all \n"

        # Removing "None"
        movies_insert = movies_insert.replace('"None"', 'NULL')

        print("#MOVIES\n")
        print(movies_insert + ";")
        print("#GENRES\n")
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
