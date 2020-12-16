import random
import time
import unittest
from YamahaTrack import YamahaTrack


class YamahaCD(object):

    def __init__(self, tracks: list):
        self._status = "stop"       # "play" / "stop" / "pause" / "fast_reverse" / "fast_forward"
        self._repeat_mode = "off"   # "off" / "one" / "all" / "folder" / "a-b"
        self._shuffle_mode = "off"  # "off" / "on" / "folder" / "program"

        self._tracks = tracks
        self._tracks_indexes = list(range(len(tracks)))
        self._current_track_index = 0

        self._last_sync_sec = int(time.time())
        self._play_time_sec = 0

    def _sync_watches(self):
        # Сверим часы:
        # 1. Определим какой сейчас играет трек: self._current_track_index
        # 2. Выставим соответствующее время проигрывания: self._play_time
        if self._status != "play":
            return

        current_time = int(time.time())
        elapsed_time_sec = current_time - self._last_sync_sec
        self._last_sync_sec = current_time

        current_track = self._tracks[self._tracks_indexes[self._current_track_index]]
        if self._repeat_mode == "one":
            self._play_time_sec = (self._play_time_sec + elapsed_time_sec) % current_track.total_time
            return

        if self._repeat_mode == "off" and elapsed_time_sec > self.disk_time():
            self._current_track_index = 0
            self._play_time_sec = 0
            return

        # self._repeat_mode == "all" / "folder" / "a-b"
        while elapsed_time_sec > current_track.total_time:
            elapsed_time_sec -= current_track.total_time
            self._current_track_index = (self._current_track_index + 1) % self.count_tracks()
            current_track = self._tracks[self._tracks_indexes[self._current_track_index]]

        self._play_time_sec = elapsed_time_sec

    def stop(self):
        self._sync_watches()
        self._status = "stop"
        self._play_time_sec = 0

    def play(self):
        self._sync_watches()
        self._status = "play"

    def pause(self):
        self._sync_watches()
        self._status = "pause"

    def count_tracks(self):
        return len(self._tracks)

    def toggle_repeat(self):
        next_repeat_mode = {
            "off": "one",
            "one": "all",
            "all": "folder",
            "folder": "a-b",
            "a-b": "off"
        }

        self._repeat_mode = next_repeat_mode[self._repeat_mode]

    def toggle_shuffle(self):
        next_shuffle_mode = {
            "off": "on",
            "on": "folder",
            "folder": "program",
            "program": "off"
        }

        self._shuffle_mode = next_shuffle_mode[self._shuffle_mode]
        if self._shuffle_mode == "off":
            self._tracks_indexes = list(range(self.count_tracks()))
        else:
            random.shuffle(self._tracks_indexes)

    def current_track_num(self):
        return self._tracks_indexes[self._current_track_index] + 1

    def set_track_num(self, num: int):
        assert 0 < num <= self.count_tracks()
        index = num - 1  # переводим номер [1..len(tracks)] в индекс [0..len(tracks))
        self._current_track_index = self._tracks_indexes.index(index)

    def next_track(self):
        self._sync_watches()
        self.set_track_num(min(self._current_track_index + 1 + 1, self.count_tracks()))

    def previous_track(self):
        self._sync_watches()
        self.set_track_num(max(self._current_track_index + 1 - 1, 1))

    def disk_time(self):
        return sum(self._tracks[i].total_time for i in range(len(self._tracks)))

    def play_info(self):
        self._sync_watches()
        current_track = self._tracks[self._tracks_indexes[self._current_track_index]]
        return {
            "playback": self._status,
            "repeat": self._repeat_mode,
            "shuffle": self._shuffle_mode,
            "play_time": self._play_time_sec,
            "total_time": current_track.total_time,
            "album": current_track.album,
            "artist": current_track.artist,
            "track": current_track.track,
            "disc_time": self.disk_time(),
            "track_number": self.current_track_num(),
            "total_tracks": self.count_tracks()
        }


class TestYamahaCD(unittest.TestCase):

    def setUp(self):
        self._yamahaCD = YamahaCD([
            YamahaTrack(track="Ben", album="Ben", artist="Michael Jackson", total_time=164),
            YamahaTrack(track="The Greatest Show on Earth", album="Ben", artist="Michael Jackson", total_time=168),
            YamahaTrack(track="People Make the World Go Round", album="Ben", artist="Michael Jackson", total_time=195),
        ])

    def test_disk_time(self):
        disk_time = 527
        self.assertEqual(disk_time, self._yamahaCD.disk_time())

    def test_set_track_num(self):
        track_num = 2
        self._yamahaCD.set_track_num(track_num)
        self.assertEqual(track_num, self._yamahaCD.current_track_num())

    def test_sync_watches(self):

        # если проигрывание было запущено - время синхронизируется с учётом прошедшего времени
        self._yamahaCD.play()
        play_time = 3
        self._yamahaCD._last_sync_sec -= play_time
        self._yamahaCD._sync_watches()
        self.assertEqual(play_time, self._yamahaCD._play_time_sec)

        # если проигрывание было приостановлено - время проигрывания не изменится
        self._yamahaCD.pause()
        last_play_time = self._yamahaCD._play_time_sec
        self._yamahaCD._last_sync_sec -= 10
        self._yamahaCD._sync_watches()
        self.assertEqual(last_play_time, self._yamahaCD._play_time_sec)

        # если проигрывание было остановлено - время проигрывания равно нулю
        self._yamahaCD.stop()
        play_time = 10
        self._yamahaCD._last_sync_sec -= play_time
        self._yamahaCD._sync_watches()
        self.assertEqual(0, self._yamahaCD._play_time_sec)
