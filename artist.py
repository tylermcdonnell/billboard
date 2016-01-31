
class Artist(object):

    def __init__(self):
        self.name   = None
        self.albums = []
        self.songs  = []
        self.charts = {}

class Album(object):
    
    def __init__(self):
        self.name   = None
        self.artist = None
        self.songs  = []
        self.charts = {}

class Songs(object):
    
    def __init__(self):
        self.name   = None
        self.artist = None
        self.lyrics = ""
        self.charts = {}
