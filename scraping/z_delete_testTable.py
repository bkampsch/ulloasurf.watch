import requests, re, datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import psycopg2
from psycopg2 import sql

conn = psycopg2.connect("dbname=ulloatest user=bruce password=gundam11")
conn.autocommit = True   # see https://www.psycopg.org/docs/connection.html#connection.autocommit
cur = conn.cursor()

plot_buoy = 46237


cur.execute(sql.SQL('DROP TABLE {table}').format(
    table=sql.Identifier(str(plot_buoy))))