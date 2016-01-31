'''
Created on Oct 2, 2015

@author: TSM
'''

import cgi
import abc
import requests
from bs4 import BeautifulSoup

# For Python 2, use this import.
import py2mlstripper as mlstripper

# For Python 3, use this import.
#import py3mlstripper as mlstripper


class ParsableWebPage(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, url):
        self._url = url

    @staticmethod
    def fix_html(s):
        '''
        Resolves common HTML quirks that make parsing a bit annoying.
        '''
        s = cgi.escape(s)

    def read_page(self):
        return requests.get(self._url).text

    @abc.abstractmethod
    def parse(self):
        '''
        Derived classes should implement some parsing scheme for the web page.
        '''
        pass

class BB100Page(ParsableWebPage):
    '''
    Scrapes data from Billboard Hot 100 page as of chart week 02/06/2016.
    '''
    def __init__(self, url, date):
        self._url  = url
        self._date = date

    @staticmethod
    def clean(s):
        '''
        Have a bunch of \t and \n
        '''
        return s.replace("\t","").replace("\n","").strip()

    def parse(self):
        '''
        Parses this Billboard 200 page and returns scraped tuples of form:
        
        (album, artist, date, position)
        '''
        soup    = BeautifulSoup(self.read_page(), "lxml")

        print ("Extracting ranks...")
        r_raw   = soup.findAll("span", {"class" : "chart-row__current-week"})
        ranks   = [int(r.contents[0]) for r in r_raw] # tags -> int
        
        print ("Extracting songs...")
        s_raw   = soup.findAll("h2", {"class" : "chart-row__song"})
        songs  = [self.clean(str(s.contents[0])) for s in s_raw]

        print ("Extracting artists...")
        a_raw   = soup.findAll("h3", {"class" : "chart-row__artist"})
        artists = [self.clean(mlstripper.strip_tags(str(a))) for a in a_raw]

        return [(self._date, z[0], z[1], z[2]) for z in zip(ranks, songs, artists)]

class BB200Page(ParsableWebPage):
    '''
    Scrapes data from Billboard 200 web pages as of 10/2/2015.
    '''    

    def __init__(self, url, date):
        self._url  = url
        self._date = date

    @staticmethod
    def clean(s):
        '''
        Have a bunch of \t and \n
        '''
        return s.replace("\t","").replace("\n","").strip()

    def parse(self):
        '''
        Parses this Billboard 200 page and returns scraped tuples of form:
        
        (album, artist, date, position)
        '''
        soup    = BeautifulSoup(self.read_page(), "lxml")

        print ("Extracting ranks...")
        r_raw   = soup.findAll("span", {"class" : "chart-row__current-week"})
        ranks   = [int(r.contents[0]) for r in r_raw] # tags -> int
        
        print ("Extracting albums...")
        a_raw   = soup.findAll("h2", {"class" : "chart-row__song"})
        albums  = [self.clean(str(a.contents[0])) for a in a_raw]

        print ("Extracting artists...")
        a_raw   = soup.findAll("h3", {"class" : "chart-row__artist"})
        artists = [self.clean(mlstripper.strip_tags(str(a))) for a in a_raw]

        return [(self._date, z[0], z[1], z[2]) for z in zip(ranks, albums, artists)]

p = BB200Page("http://www.billboard.com/charts/billboard-200", "")
for e in p.parse():
    print (e)

p = BB100Page("http://www.billboard.com/charts/hot-100", "")
for e in p.parse():
    print (e)
