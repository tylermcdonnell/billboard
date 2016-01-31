
import requests
import re
import py2mlstripper as mlstripper
from bs4 import BeautifulSoup

# Fetches song lyrics from the web.
# Requires Python 2 and BeautifulSoup.

def fetch_lyrics(artist_name, song_name):
    f_artist = _format_name(artist_name)
    f_song   = _format_name(song_name)
    return default_source(f_artist, f_song)   

def _fetch_from_lyricsdotcom(artist, song):
    # Format for URL structure.
    artist = artist.replace(' ', '-')
    song   = song.replace(' ', '-')
    page   = requests.get('http://www.lyrics.com/%s-lyrics-%s.html' % (song, artist))

    # Extract and process lyrics from page.
    soup   = BeautifulSoup(page.text, 'lxml')
    lyrics = str(soup.findAll('div', {'id' : 'lyrics'}))
    lyrics = mlstripper.strip_tags(lyrics)
    lyrics = lyrics.replace('\\n', '\n') # Re-encode new lines.
    return lyrics

def _format_name(name):
    # Names should contain only lowercase alphanumeric characters and spaces.
    name = name.replace('-', ' ').lower()
    name = (re.sub(r'[^\w\- ]+', '', name))
    return name

# Configure web source.
default_source = _fetch_from_lyricsdotcom

# Sample Usage
'''
print (fetch_lyrics("The Beatles", "Come Together"))
print (fetch_lyrics("Taylor Swift", "I Knew You Were Trouble."))
print (fetch_lyrics("alt-j", "Taro"))
print (fetch_lyrics("Dr. Dre", "still D.R.E."))
'''
