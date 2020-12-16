class YamahaTrack(object):

    def __init__(self):
        self.track = ""
        self.album = ""
        self.artist = ""
        self.total_time = 0

    def __init__(self, track: str, album: str, artist: str, total_time: int):
        self.track = track
        self.album = album
        self.artist = artist
        self.total_time = total_time

