from YamahaPlaylist import YamahaPlaylist
from YamahaTrack import YamahaTrack


class YamahaNetusb(object):

    def __init__(self, playlist: YamahaPlaylist):
        self._input = "spotify"
        self._repeat_mode = "off"   # "off" / "one" / "all"
        self._shuffle_mode = "off"  # "off" / "on" / "songs" / "albums"
        self._playlist = playlist

    def play(self):
        self._playlist.play()

    def stop(self):
        self._playlist.stop()

    def pause(self):
        self._playlist.pause()

    def next_track(self):
        self._playlist.next_track()

    def previous_track(self):
        self._playlist.previous_track()

    def toggle_repeat(self):
        next_repeat_mode = {
            "off": "one",
            "one": "all",
            "all": "off"
        }

        self._repeat_mode = next_repeat_mode[self._repeat_mode]
        if self._repeat_mode == "off":
            self._playlist.repeat_off()
        elif self._repeat_mode == "one":
            self._playlist.repeat_one()
        else:
            self._playlist.repeat_all()

    def toggle_shuffle(self):
        next_shuffle_mode = {
            "off": "on",
            "on": "songs",
            "songs": "albums",
            "albums": "off"
        }

        self._shuffle_mode = next_shuffle_mode[self._shuffle_mode]
        if self._shuffle_mode == "off":
            self._playlist.shuffle_off()
        else:
            self._playlist.shuffle_on()

    def play_info(self):
        track_index, play_time = self._playlist.sync()
        current_track = self._playlist.current_track()

        return {
            "input": self._input,
            "playback": self._playlist.play_state(),
            "repeat": self._repeat_mode,
            "shuffle": self._shuffle_mode,
            "play_time": play_time,
            "total_time": current_track.total_time,
            "artist": current_track.artist,
            "album": current_track.album,
            "track": current_track.track
        }
