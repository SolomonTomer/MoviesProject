import sys
from Crawler.Database.Database import Database

ALL_ACTORS = "select actor as name from movie_stars"
ALL_DIRECTORS = "select director as name from movie_directors"
ALL_WRITERS = "select writer as name from movie_writers"
ALL_DISTINCT_NAMES_WRAPPER = "select distinct tmp.name from (%s) tmp"
INSERT_FROM_SELECT = 'select "{}", "{}","{}","{}","{}","{}","{}" from dual'


class Person:

    def __init__(self, name):
        self.name = name
        self.meta_critic_highest = 0
        self.meta_critic_avg_career = 0
        self.meta_critic_lowest = 0
        self.meta_user_highest = 0
        self.meta_user_median = 0
        self.meta_user_lowest = 0

    def get_insert_from_select(self):
        return INSERT_FROM_SELECT.format(self.name, self.meta_critic_highest, self.meta_critic_avg_career,
                                         self.meta_critic_lowest, self.meta_user_highest, self.meta_user_median,
                                         self.meta_user_lowest)

    @staticmethod
    def get_persons_in_db(actors=True, directors=True, writers=True):
        union_sql = ''
        results = []
        conn = None
        if actors:
            union_sql += ALL_ACTORS
        if directors:
            if union_sql != '':
                union_sql += " union all \n" + ALL_DIRECTORS
            else:
                union_sql += ALL_DIRECTORS
        if writers:
            if union_sql != '':
                union_sql += " union all \n" + ALL_WRITERS
            else:
                union_sql += ALL_WRITERS
        try:
            conn = Database().get_connection()
            cursor = conn.cursor()
            final_sql = ALL_DISTINCT_NAMES_WRAPPER % union_sql
            cursor.execute(final_sql)
            results = cursor.fetchall()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        finally:
            if conn is not None:
                conn.close()
            return [Person(row.get("name")) for row in results]