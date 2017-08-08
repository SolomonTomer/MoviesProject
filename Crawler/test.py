html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

from bs4 import BeautifulSoup
# soup = BeautifulSoup(html_doc, 'html.parser')
#
# print(soup.prettify())
# print('test')

import pymysql
import sshtunnel
#
# with sshtunnel.SSHTunnelForwarder(
#         ('ec2-35-160-78-221.us-west-2.compute.amazonaws.com', 22),
#         ssh_username='ubuntu',
#         shh_pkey ='C:\\Users\\tomer\\OneDrive\\MySqlKey.ppk',
#         remote_bind_address=('ec2-35-160-78-221.us-west-2.compute.amazonaws.com', 3306)) as tunnel:
#
#     connection = pymysql.connector.connect(
#         user='tash',
#         password='abc123',
#         database='movies')

connection = pymysql.connect(host='ec2-35-160-78-221.us-west-2.compute.amazonaws.com',
                             user='tash',
                             password='abc123',
                             db='movies',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
print(connection)
try:
    cursor = connection.cursor()
    # Read a single record
    sql = "insert into movie select 'tommer' from dual"
    cursor.execute(sql)
    connection.commit()
    result = cursor.fetchone()
    print(result)
finally:
    connection.close()