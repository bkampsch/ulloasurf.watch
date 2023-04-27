
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

scrape_cols_v1 = [
    'time',
    'surf 1', 'height 1', 'period 1', 'dir 1',
    'surf 2', 'height 2', 'period 2', 'dir 2',
    'sea height', 'sea period', 'sea direction',
    'chop height', 'chop direction',
]

scrape_cols_v2 = [
    'time',
    'surf 1', 'height 1', 'period 1', 'dir 1',
    'surf 2', 'height 2', 'period 2', 'dir 2',
    'sig wave height', 'sig wave period',
    'chop height', 'chop direction',
]


# get list of all columns, for making single table
sc_v1_set = set(scrape_cols_v1)
sc_v2_set = set(scrape_cols_v2)
sc_v2_set_unique = sc_v2_set - sc_v1_set
scrape_cols_combined = scrape_cols_v1 + list(sc_v2_set_unique)

def tuple_ify_table_cols(col_list, col_type):
    tuple_list = [];
    col_list = [col.replace(' ','_') for col in col_list]
    tuple_list.append(('buoy_id','INTEGER'))
    for col in col_list:
        if col == 'time':
            tuple_list.append((col,'VARCHAR'))  # what an epic function
        else:
            tuple_list.append((col,col_type))
    return(tuple(tuple_list))

columns_tuple = tuple_ify_table_cols(scrape_cols_combined,'INTEGER')


def create_table(name,columns):
    fields = []
    for col in columns:
        fields.append(sql.SQL("{} {}").format(sql.Identifier(col[0]),sql.SQL(col[1])))
    query = sql.SQL("CREATE TABLE IF NOT EXISTS {table_name} ({fields});").format(
        table_name = sql.Identifier(name),
        fields = sql.SQL(', ').join(fields)
    )
    cur.execute(query)

table_name = "buoy_data"

create_table(table_name,columns_tuple)



#cur.execute(sql.SQL('DROP TABLE {table}').format(
#    table=sql.Identifier(str(table_name))))


def add_rows(name,scrape_cols,df):
    scrape_cols = [col.replace(' ','_') for col in scrape_cols]
    fields = []
    holders = []
    for col in scrape_cols:
        fields.append(sql.SQL("{}").format(sql.Identifier(col)))
        holders.append(sql.SQL("%s"))


    for ii in range(len(df.index)):
        data = []
        data.append(df.index[ii])
        data_list = df.iloc[ii].tolist()
        for jj in range(len(data_list)):
            if not type(data_list[jj]) is int:
                data_list[jj] = None
        data += data_list

        query = sql.SQL("INSERT INTO {table_name} ({fields}) VALUES ({holders}) ON CONFLICT DO NOTHING;").format(
            table_name = sql.Identifier(name),
            fields = sql.SQL(', ').join(fields),
            holders = sql.SQL(', ').join(holders)
        )

        cur.execute(query,tuple(data))



buoysD = {
    46237: ('SF BAR', 'http://www.stormsurfing.com/cgi/display2.cgi?a=t22;b=142', scrape_cols_v1),
    46042: ('W MONTEREY BAY', 'http://www.stormsurfing.com/cgi/display2.cgi?a=t22;b=46042', scrape_cols_v2),
    46218: ('HARVEST', 'http://www.stormsurfing.com/cgi/display2.cgi?a=t22;b=071', scrape_cols_v1),
    46214: ('POINT REYES', 'http://www.stormsurfing.com/cgi/display2.cgi?a=t22;b=029', scrape_cols_v1),
    46232: ('POINT LOMA SOUTH', 'http://www.stormsurfing.com/cgi/display2.cgi?a=t22;b=191', scrape_cols_v1),
    46059: ('CALIFORNIA', 'http://www.stormsurfing.com/cgi/display2.cgi?a=t22;b=46059', scrape_cols_v2),
}


for plot_buoy, tup in buoysD.items():

    # plot_buoy = 46042
    # plot_buoy = 46237

    tup = buoysD[plot_buoy]

    buoy_name, url, scrape_cols = tup
    page = requests.get(url)
    outdir = '/var/www/ulloasurf'
    soup = BeautifulSoup(page.content, "html.parser")

    regex1 = '\d*\.?\d+'

    trs = soup.find_all('tr')
    data2 = []
    for tr in trs:
        tds = [x for x in tr.children if str(x).startswith('<td>')]
        if len(tds) != 7:
            continue
        # try:
        data = []
        dtstr = str(tds[0].string)
        if not dtstr.endswith('Z'):
            dtstr += 'Z'
        data.append(pd.to_datetime(dtstr).tz_convert('America/Los_Angeles'))
        data.append(float(re.match(regex1, tds[1].string).group()))
        data += [float(x) for x in re.findall(regex1, tds[2].string)]
        data.append(float(re.match(regex1, tds[3].string).group()))
        data += [float(x) for x in re.findall(regex1, tds[4].string)]
        data += [float(x) for x in re.findall(regex1, tds[5].string)]
        chop_data = re.findall(regex1, tds[6].string)
        data += [float(x) for x in chop_data]
        if len(chop_data) == 1:     
            data += [np.nan]
        data2.append(data)
        # except:
        #     pass


    df = pd.DataFrame(data2, columns=pd.Index(scrape_cols)).set_index('time')
    # df.index = df.index.strftime('%a %I %p')


    def swap(s, one, two):
        tmp = s[one]
        s[one] = s[two]
        s[two] = tmp

    def run_algo(df):
        s_prev, sL = None, []
        for i, tup in zip(range(len(df)), df.iterrows()):
            dt, s = tup
            debug_str = f'{i} {dt}: INITIAL dir1={s["dir 1"]}, dir2={s["dir 2"]}'
            if s_prev is None:
                sL.append(s)
                s_prev = s
                continue
            ewm1 = df['dir 1'].iloc[:i].ewm(halflife=5).mean().iloc[-1]
            ewm2 = df['dir 2'].iloc[:i].ewm(halflife=5).mean().iloc[-1]
            debug_str += f'\tewm1={ewm1:.3f} ewm2={ewm2:.3f}'
            if abs(s['dir 1']-ewm1) > abs(s['dir 1']-ewm2):
                swap(s, 'dir 1', 'dir 2')
                swap(s, 'surf 1', 'surf 2')
                swap(s, 'height 1', 'height 2')
                swap(s, 'period 1', 'period 2')
            sL.append(s)
            debug_str += f'\tFINAL dir1={s["dir 1"]}, dir2={s["dir 2"]}'
    #         print(debug_str)
            s_prev = s
        return pd.concat(sL, axis=1).T

    df = run_algo(df[::-1])[::-1]


    add_rows(table_name,scrape_cols,df)


    #cur.execute(sql.SQL("SELECT * FROM {table};").format(table=sql.Identifier(str(table_name))))
    #print(cur.fetchone())


    print(f'done with {buoy_name}')




print('complete.')

conn.commit()
cur.close()
conn.close()





























    # To drop the table:

    #cur.execute(sql.SQL('DROP TABLE {table}').format(
    #    table=sql.Identifier(str(table_name))))




    # "full table" columns"
    # surf 1  height 1  period 1  dir 1  surf 2  height 2  period 2  dir 2  sea height  sea period  sea direction  chop height  chop direction
    # (surf_1,height_1,period_1,dir_1,surf_2,height_2,period_2,dir_2,sea_height,sea_period,sea_direction,chop_height,chop_direction)

    # ideally every part of the table is created/named dynamically... right?


    #cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {table} (time_stamp VARCHAR PRIMARY KEY, \
    #    surf_1 INTEGER, height_1 INTEGER, period_1 INTEGER, dir_1 INTEGER, surf_2 INTEGER, \
    #    height_2 INTEGER, period_2 INTEGER, dir_2 INTEGER, sea_height integer, \
    #    sea_period INTEGER, sea_direction INTEGER, chop_height INTEGER, chop_direction INTEGER);").format(
    #    table=sql.Identifier(str(plot_buoy))))



    #for ii in range(len(df.index)):

    #    cur.execute(sql.SQL('INSERT INTO {table} (time_stamp,surf_1,height_1,period_1,dir_1,surf_2,height_2,period_2, \
    #        dir_2,sea_height,sea_period,sea_direction,chop_height,chop_direction) \
    #        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;').format( \
    #        table=sql.Identifier(str(table_name))),  \
    #        (df.index[ii],df.iloc[ii][0],df.iloc[ii][1],df.iloc[ii][2],df.iloc[ii][3],df.iloc[ii][4],df.iloc[ii][5],df.iloc[ii][6], \
    #        df.iloc[ii][7],df.iloc[ii][8],df.iloc[ii][9],df.iloc[ii][10],df.iloc[ii][11],df.iloc[ii][12]))

