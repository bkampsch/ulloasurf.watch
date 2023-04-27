
import requests, re, datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


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
    # # plot_buoy = 46237

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
    df.index = df.index.strftime('%a %I %p')

    plt.rcParams['axes.grid'] = True

    def plotit(df, path, halflife=None):
        fig, axs = plt.subplots(3, figsize=(10*2/3,12*2/3))
        if halflife:
            df = df.ewm(halflife=halflife).mean()
        plt.suptitle(f'{buoy_name}, last update: {datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")}')
    #     df[['surf 1','surf 2']].plot(ax=axs[0])
        df[['height 1','height 2']].plot(ax=axs[0])
        df[['dir 1', 'dir 2']].plot(ax=axs[1], ylim=(150, 330))
        df[['period 1','period 2']].plot(ax=axs[2])

        plt.savefig(path)

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

    plotit(df, f'/var/www/ulloasurf.watch/assets/surf_chart_{plot_buoy}.jpeg', halflife=1)
    print(f'done with {buoy_name}')

print('complete.')
