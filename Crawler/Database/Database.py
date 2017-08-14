import pymysql


class Database:

    HOST = "ec2-35-160-78-221.us-west-2.compute.amazonaws.com"

    def get_connection(self):
        connection = pymysql.connect(host=self.HOST,
                                     user='tash',
                                     password='abc123',
                                     db='movies',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
