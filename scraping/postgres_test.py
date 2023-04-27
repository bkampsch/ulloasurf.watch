
import psycopg2

conn = psycopg2.connect("dbname=ulloatest user=bruce password=gundam11")
conn.autocommit = True   # see https://www.psycopg.org/docs/connection.html#connection.autocommit

cur = conn.cursor()

# this will crash b/c i already ran it so the table exists already
cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")  

cur.execute('INSERT INTO test (num, data) VALUES (%s, %s)', (100, "hello world"))
cur.execute("SELECT * FROM test;")
print(cur.fetchone())



