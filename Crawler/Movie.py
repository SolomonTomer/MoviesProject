import pymysql
from Crawler.Database import Database

class Movie:
    db = Database()


    def insert_to_temp(self, lst):
        union = ''
        for i in range(len(lst)):
            m = lst[i]
            union += 'select \'' + m[0] + '\',' + m[1] + ', STR_TO_DATE(\'' + m[2] + '\', \'%d/%m/%Y\') from dual'
            if i + 1 != len(lst):
                union += ' union all \n'

        print(union)
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            sql = 'INSERT INTO movie_tmp ' + union
            cursor.execute(sql)
            conn.commit()
            result = cursor.fetchone()
        finally:
            conn.close()