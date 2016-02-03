'''
Created on Oct 2, 2015

@author: TSM
'''

import cgi
import abc
import requests
import datetime
from bs4 import BeautifulSoup
from collections import namedtuple

# For Python 2, use this import.
import py2mlstripper as mlstripper

# For Python 3, use this import.
#import py3mlstripper as mlstripper

# Relevant types.
Billboard200Entry = namedtuple('Billboard200Entry', ['rank', 'album', 'artist'])
Hot100Entry       = namedtuple('Hot100Entry', ['rank', 'song', 'artist'])

# See bottom of file for sample usage.

def parse_b200_range(start, end):
    '''
    Returns a dictionary of ( date : Billboard200Entry ) for
    all chart weeks contained in the date range [start,end].
    '''
    results = {}
    base_url = 'http://www.billboard.com/charts/hot-100/'
    for date in _date_range(start, end, 7):
        url = ('%s/%s' % (base_url, date))
        results.update({date : parse_b200(url)})
    return results

def parse_h100_range(start, end):
    '''
    Returns a dictionary of ( date : Hot100Entry ) for
    all chart weeks contained in the date range [start,end].
    '''
    base_url = 'http://www.billboard.com/charts/billboard-200/'
    for date in _date_range(start, end, 7):
        url = ('%s/%s' % (base_url, date))
        results.update({date : parse_h100(url)})
    return results

def parse_h100(url):
    '''
    Parses this Billboard Hot 100 page and returns scraped entries.
    
    Arguments:
    url -- URL of a Hot 100 page.
    '''        
    soup    = BeautifulSoup(_get(url), "lxml")
    
    #print ("Extracting ranks...")
    r_raw   = soup.findAll("span", {"class" : "chart-row__current-week"})
    ranks   = [int(r.contents[0]) for r in r_raw] # tags -> int
    
    #print ("Extracting songs...")
    s_raw   = soup.findAll("h2", {"class" : "chart-row__song"})
    songs  = [_clean(str(s.contents[0])) for s in s_raw]
    
    #print ("Extracting artists...")
    a_raw   = soup.findAll("h3", {"class" : "chart-row__artist"})
    artists = [_clean(mlstripper.strip_tags(str(a))) for a in a_raw]
    
    return [Hot100Entry(song=z[0],rank=z[1],artist=z[2]) for z in zip(songs, ranks, artists)]

def parse_b200(url):
    '''
    Parses the Billboard 200 page and returns scraped entries.
    
    Arguments:
    url -- URL of a Billboard 200 page.
    '''
    soup    = BeautifulSoup(_get(url), "lxml")
    
    #print ("Extracting ranks...")
    r_raw   = soup.findAll("span", {"class" : "chart-row__current-week"})
    ranks   = [int(r.contents[0]) for r in r_raw] # tags -> int
    
    #print ("Extracting albums...")
    a_raw   = soup.findAll("h2", {"class" : "chart-row__song"})
    albums  = [_clean(str(a.contents[0])) for a in a_raw]
    
    #print ("Extracting artists...")
    a_raw   = soup.findAll("h3", {"class" : "chart-row__artist"})
    artists = [_clean(mlstripper.strip_tags(str(a))) for a in a_raw]
    
    return [Billboard200Entry(album=z[0],rank=z[1],artist=z[2]) for z in zip(albums, ranks, artists)]

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

# Sample Usage.
for e in parse_b200("http://www.billboard.com/charts/billboard-200"):
    print (e)
for e in parse_h100("http://www.billboard.com/charts/hot-100"):
    print (e)
