import sys
from Crawler.Database.Database import Database
import pickle as fp


class TmpMovies:
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
    def create_object_by_row(row):
        tmp_movie = TmpMovies(row.get("title"), row.get("release_date"), row.get("run_time"),
                              row.get("meta_score"), row.get("user_score"), row.get("genres"))
        return tmp_movie

    @staticmethod
    def get_by_title(title):
        try:
            conn = Database().get_connection()
            cursor = conn.cursor()
            cursor.execute(TmpMovies.get_movie_by_title, title)
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
            union += TmpMovies.raw_sql.format(self.title, self.release_date, self.run_time,
                                                    self.meta_score, self.user_score, ', '.join(self.genres))
            if i + 1 != len(lst):
                union += " union all \n"
        print(union)

    @staticmethod
    def get_all_rows():
        results = ''
        conn = None
        try:
            conn = Database().get_connection()
            cursor = conn.cursor()
            cursor.execute(TmpMovies.get_all_sql)
            results = cursor.fetchall()
            return results
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        finally:
            if conn is not None:
                conn.close()
            return [TmpMovies.create_object_by_row(row) for row in results]

    @staticmethod
    def create_backup_file(file_name):
        rows = TmpMovies.get_all_rows()
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
