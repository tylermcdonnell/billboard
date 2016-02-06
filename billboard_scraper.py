'''
Created on Oct 2, 2015

Description: This is a script for scraping Billboard Hot 100 and
Billboard 200 data from the online archives. Billboard is an 
entertainment media brand known for maintaining music charts which
track the most popular music in the United States, and has 
maintained charts since the 1950s.

@author: TSM
'''
import cgi
import abc
import requests
import datetime
import pickle
import traceback
from bs4 import BeautifulSoup
from collections import namedtuple, defaultdict

# For Python 2, use this import.
import py2mlstripper as mlstripper

# For Python 3, use this import.
#import py3mlstripper as mlstripper


# Relevant types.
Billboard200Entry = namedtuple('Billboard200Entry', ['date', 'rank', 'album', 'artist'])
Hot100Entry       = namedtuple('Hot100Entry', ['date', 'rank', 'song', 'artist'])

# Sample Usage: Scrape the most recent chart and save it to file.
'''
save("b200", scrape_b200('http://www.billboard.com/charts/billboard-200'))
save("h100", scrape_h100('http://www.billboard.com/charts/hot-100'))
'''

# Sample Usage: Scrape all archived data.
'''
first_h100_chart = datetime.date(1958, 9, 6)
first_b200_chart = datetime.date(1983,11, 5)
today            = datetime.datetime.now()

save("b200", scrape_b200_range(first_b200_chart, today))
save("h100", scrape_h100_range(first_h100_chart, today))
'''

# Sample Usage: Save pickled data after parsing.
'''
save("b200", scrape_b200("http://www.billboard.com/charts/billboard-200"))
save("h100", scrape_h100("http://www.billboard.com/charts/hot-100"))
'''

# Sample Usage: Load archive and print in chronological order.
'''
archive = load('b200')
for date in sorted(archive.keys()):
    print ("\n----- Billboard 200 Chart for %s ---- " % date)
    for entry in archive[date]:
        print (entry)
'''

# Sample Usage: Print chart run of a particular album.
# Note: These types are made for scraping data in the most general
#       sense. They are obviously not optimized for these types of
#       queries. But it is easy to do so.
'''
archive = load('b200')
album  = "1989"
artist = "Taylor Swift" 
for entry in [e for e in archive if e.album == album and e.artist == artist].sort(key=lambda t: t.date):
    print entry
'''

def scrape_b200_range(start, end):
    '''
    Returns a dictionary of ( date : Billboard200Entry ) for
    all chart weeks contained in the date range [start,end].
    '''
    results = []
    for date in _date_range(start, end, 7):
        print ("Scraping Billboard 200 for Week of %s" % date)
        try:
            chart = scrape_b200(date)
        except: 
            print ("Failed to scrape %s" % date)
            chart = []
        results.append(chart)
    return results

def scrape_h100_range(start, end):
    '''
    Returns a dictionary of ( date : Hot100Entry ) for
    all chart weeks contained in the date range [start,end].
    '''
    results = []
    for date in _date_range(start, end, 7):
        print ("Scraping Hot 100 for Week of %s" % date)
        try:
            chart = scrape_h100(date)
        except:
            print ("Failed to scrape %s" % date)
            chart = []
        results.append(chart)
    return results

def scrape_h100(date):
    '''
    Parses this Billboard Hot 100 page and returns scraped entries.
    
    Arguments:
    url -- URL of a Hot 100 page.
    '''
    base_url = 'http://www.billboard.com/charts/hot-100/'
    soup    = BeautifulSoup(_get('%s%s' % (base_url, date)), "lxml")
    
    #print ("Extracting ranks...")
    r_raw   = soup.findAll("span", {"class" : "chart-row__current-week"})
    ranks   = [int(r.contents[0]) for r in r_raw] # tags -> int
    
    #print ("Extracting songs...")
    s_raw   = soup.findAll("h2", {"class" : "chart-row__song"})
    songs  = [_clean(str(s.contents[0])) for s in s_raw]
    
    #print ("Extracting artists...")
    a_raw   = soup.findAll("h3", {"class" : "chart-row__artist"})
    artists = [_clean(mlstripper.strip_tags(str(a))) for a in a_raw]
    
    return [Hot100Entry(date=date,song=z[0],rank=z[1],artist=z[2]) for z in zip(songs, ranks, artists)]

def scrape_b200(date):
    '''
    Parses the Billboard 200 page and returns scraped entries.
    
    Arguments:
    url -- URL of a Billboard 200 page.
    '''
    base_url = 'http://www.billboard.com/charts/billboard-200/'
    soup    = BeautifulSoup(_get('%s%s' % (base_url, date)), "lxml")
    
    #print ("Extracting ranks...")
    r_raw   = soup.findAll("span", {"class" : "chart-row__current-week"})
    ranks   = [int(r.contents[0]) for r in r_raw] # tags -> int
    
    #print ("Extracting albums...")
    a_raw   = soup.findAll("h2", {"class" : "chart-row__song"})
    albums  = [_clean(str(a.contents[0])) for a in a_raw]
    
    #print ("Extracting artists...")
    a_raw   = soup.findAll("h3", {"class" : "chart-row__artist"})
    artists = [_clean(mlstripper.strip_tags(str(a))) for a in a_raw]
    
    return [Billboard200Entry(date=date, album=z[0],rank=z[1],artist=z[2]) for z in zip(albums, ranks, artists)]

def save(filename, chart_data):
    with open('%s.pickle' % filename, 'wb') as handle:
        pickle.dump(chart_data, handle)

def load(filename):
    with open('%s.pickle' % filename, 'rb') as handle:
        return pickle.load(handle)
    
def _get(url):
    '''
    Fetches a URL and returns the html. Returns empty string in case of failure.
    '''
    try:
        return requests.get(url, timeout=3).text
    except:
        return ''        

def _date_range(start, end, delta):
    '''
    Generates a list of dates in the range [start, end] separated by delta days. 
    '''
    for n in [n for n in range(int((end - start).days) + 1) if n % delta == 0]:
        yield start + datetime.timedelta(days=n)

def _clean(s):
    '''
    Have a bunch of \t and \n.
    '''
    return s.replace("\t","").replace("\n","").strip()

def _date_range(start, end, delta):
    '''
    Returns dates in range [start,end] separated by delta days.
    '''
    for n in [n for n in range(int((end - start).days)) if n % delta == 0]:
        yield start + datetime.timedelta(days=n)
