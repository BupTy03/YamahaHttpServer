from YamahaPlaylist import YamahaPlaylist
from YamahaTrack import YamahaTrack


class YamahaCD:
    def __init__(self, playlist: YamahaPlaylist):
        self._repeat_mode = "off"   # "off" / "one" / "all" / "folder" / "a-b"
        self._shuffle_mode = "off"  # "off" / "on" / "folder" / "program"
        self._playlist = playlist

    def play(self):
        self._playlist.play()

    def stop(self):
        self._playlist.stop()

    def pause(self):
        self._playlist.pause()

    def toggle_repeat(self):
        next_repeat_mode = {
            "off": "one",
            "one": "all",
            "all": "folder",
            "folder": "a-b",
            "a-b": "off"
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
            "on": "folder",
            "folder": "program",
            "program": "off"
        }

        self._shuffle_mode = next_shuffle_mode[self._shuffle_mode]
        if self._shuffle_mode == "off":
            self._playlist.shuffle_off()
        else:
            self._playlist.shuffle_on()

    def set_track_num(self, num: int):
        # переводим номер [ 1..len(tracks) ] в индекс [ 0..len(tracks) )
        self._playlist.set_track_index(num - 1)

    def next_track(self):
        self._playlist.next_track()

    def previous_track(self):
        self._playlist.previous_track()

    def fast_reverse_start(self):
        self._playlist.fast_reverse_start()

    def fast_reverse_end(self):
        self._playlist.fast_reverse_end()

    def fast_forward_start(self):
        self._playlist.fast_forward_start()

    def fast_forward_end(self):
        self._playlist.fast_forward_end()

    def play_info(self):
        track_index, play_time = self._playlist.sync()
        current_track = self._playlist.current_track()
        return {
            "playback": self._playlist.play_state(),
            "repeat": self._repeat_mode,
            "shuffle": self._shuffle_mode,
            "play_time": play_time,
            "total_time": current_track.total_time,
            "album": current_track.album,
            "artist": current_track.artist,
            "track": current_track.track,
            "disc_time": self._playlist.summary_time(),
            "track_number": track_index + 1,
            "total_tracks": self._playlist.count_tracks()
        }

