import pymysql
from Crawler.Database import Database


class Movie:

    def __init__(self, row):
        self.title = row[0]
        self.release_date = row[2]
        self.rated = None
        self.run_time = 0
        self.country = None
        self.language = None
        self.opening_weekend = 0
        self.gross = 0
        self.imdb_score = 0
        self.meta_score = row[1]
        self.genres = []
        self.director = None
        self.writer = None
        self.stars = []




    def get_temp_movies(self):
        query = 'Select * from movie_tmp'
        conn = Database().get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()



    def insert_to_temp(self, lst):
        union = ''
        for i in range(len(lst)):
            m = lst[i]
            m.replace('\'', '\\\'')
            union += 'select \'' + m[0] + '\',' + m[1] + ', STR_TO_DATE(\'' + m[2] + '\', \'%d/%m/%Y\') from dual'
            if i + 1 != len(lst):
                union += ' union all \n'

        print(union)
        # Received an error while trying to insert a valid statement. splitted manualy
        # try:
        #     cursor = conn.cursor()
        #     sql = 'INSERT INTO movie_tmp ' + union
        #     cursor.execute(sql)
        #     conn.commit()
        #     result = cursor.fetchone()
        # finally:
        #     conn.close()