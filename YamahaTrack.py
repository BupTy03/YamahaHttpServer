class YamahaTrack(object):
    def __init__(self):
        self.track = ""
        self.album = ""
        self.albumart_url = ""
        self.artist = ""
        self.total_time = 0

    def __init__(self, track: str, album: str, albumart_url: str, artist: str, total_time: int):
        self.track = track
        self.album = album
        self.albumart_url = albumart_url
        self.artist = artist
        self.total_time = total_time

