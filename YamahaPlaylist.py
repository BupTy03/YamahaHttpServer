import random
import time
import unittest
from enum import Enum
from YamahaTrack import YamahaTrack


class RepeatMode(Enum):
    OFF = 0
    ONE = 1
    ALL = 2


# "play" / "stop" / "pause" / "fast_reverse" / "fast_forward"
class PlayState(Enum):
    play = 0
    stop = 1
    pause = 2


class YamahaPlaylist(object):

    def __init__(self, tracks: list):
        self._tracks = tracks
        self._tracks_indexes = list(range(len(tracks)))
        self._current_track_index = 0

        self._last_sync_sec = int(time.time())
        self._play_time_sec = 0
        self._play_state = PlayState.stop
        self._repeat_mode = RepeatMode.ALL

    def sync(self, current_time_sec=int(time.time())):
        # Сверим часы:
        # 1. Определим какой сейчас играет трек: self._current_track_index
        # 2. Выставим соответствующее время проигрывания: self._play_time
        if self._play_state != PlayState.play:
            return self._current_track_index, self._play_time_sec

        elapsed_time_sec = current_time_sec - self._last_sync_sec
        self._last_sync_sec = current_time_sec

        current_track = self._tracks[self._tracks_indexes[self._current_track_index]]
        if self._repeat_mode == RepeatMode.ONE:
            self._play_time_sec = (self._play_time_sec + elapsed_time_sec) % current_track.total_time
            return self._current_track_index, self._play_time_sec

        if self._repeat_mode == RepeatMode.OFF and elapsed_time_sec > self.summary_time():
            self._current_track_index = 0
            self._play_time_sec = 0
            return self._current_track_index, self._play_time_sec

        # self._repeat_mode == RepeatMode.ALL
        while elapsed_time_sec > current_track.total_time:
            elapsed_time_sec -= current_track.total_time
            self._current_track_index = (self._current_track_index + 1) % self.count_tracks()
            current_track = self._tracks[self._tracks_indexes[self._current_track_index]]

        self._play_time_sec = elapsed_time_sec
        return self._current_track_index, self._play_time_sec

    def play_state(self):
        self.sync()
        return self._play_state.name

    def play(self):
        self.sync()
        self._play_state = PlayState.play

    def pause(self):
        self.sync()
        self._play_state = PlayState.pause

    def stop(self):
        self.sync()
        self._play_state = PlayState.stop
        self._play_time_sec = 0

    def count_tracks(self):
        return len(self._tracks)

    def current_track(self):
        self.sync()
        return self._tracks[self._tracks_indexes[self._current_track_index]]

    def set_track_index(self, index: int):
        assert 0 <= index < self.count_tracks()
        self._current_track_index = self._tracks_indexes.index(index)
        self._play_time_sec = 0

    def next_track(self):
        self.sync()
        self.set_track_index(min(self._current_track_index + 1, self.count_tracks() - 1))

    def previous_track(self):
        self.sync()
        self.set_track_index(max(self._current_track_index - 1, 0))

    def summary_time(self):
        return sum(self._tracks[i].total_time for i in range(self.count_tracks()))

    def shuffle_on(self):
        random.shuffle(self._tracks_indexes)

    def shuffle_off(self):
        self._tracks_indexes = list(range(self.count_tracks()))

    def repeat_off(self):
        self._repeat_mode = RepeatMode.OFF

    def repeat_one(self):
        self._repeat_mode = RepeatMode.ONE

    def repeat_all(self):
        self._repeat_mode = RepeatMode.ALL


class TestYamahaPlaylist(unittest.TestCase):

    def setUp(self):
        self._yamahaPlaylist = YamahaPlaylist([
            YamahaTrack(track="Ben", album="Ben", artist="Michael Jackson", total_time=164),
            YamahaTrack(track="The Greatest Show on Earth", album="Ben", artist="Michael Jackson", total_time=168),
            YamahaTrack(track="People Make the World Go Round", album="Ben", artist="Michael Jackson", total_time=195),
        ])

    def test_summary_time(self):
        sum_time = 527
        self.assertEqual(sum_time, self._yamahaPlaylist.summary_time())

    def test_set_track_num(self):
        track_index = 2
        self._yamahaPlaylist.set_track_index(track_index)
        self.assertEqual(track_index, self._yamahaPlaylist._tracks_indexes[self._yamahaPlaylist._current_track_index])
        self.assertEqual(self._yamahaPlaylist.current_track().track, "People Make the World Go Round")
        self.assertEqual(self._yamahaPlaylist._play_time_sec, 0)

    def test_sync(self):
        # если проигрывание было запущено - время синхронизируется с учётом прошедшего времени
        play_time = 3
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(play_time, self._yamahaPlaylist._play_time_sec)

        # если проигрывание было приостановлено - время проигрывания не изменится
        play_time = 10
        self._yamahaPlaylist.pause()
        last_play_time = self._yamahaPlaylist._play_time_sec
        self._yamahaPlaylist.sync(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(last_play_time, self._yamahaPlaylist._play_time_sec)

        # если проигрывание было остановлено - время проигрывания остаётся равным нулю
        play_time = 10
        self._yamahaPlaylist.stop()
        self._yamahaPlaylist.sync(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(0, self._yamahaPlaylist._play_time_sec)

