from flask import Flask
import psycopg2 # for database connection and dependent on Flask


dbconn = psycopg2.connect(database="postgres", user="postgres", port=5433, password="securepwd", host="localhost")
myCursor = dbconn.cursor()
myCursor.callproc('add_content', ('Test_lecture','Test_chapter', 'Test_content'))
a_results = myCursor.fetchone()
myCursor.close()
dbconn.close()