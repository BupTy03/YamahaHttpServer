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


class YamahaPlaylist:
    def __init__(self, tracks: list):
        self._tracks = tracks
        self._tracks_indexes = list(range(len(tracks)))
        self._current_track_index = 0
        self._last_sync_sec = int(time.time())
        self._play_time_sec = 0
        self._play_state = PlayState.stop
        self._repeat_mode = RepeatMode.ALL

    def sync(self):
        return self.sync_time(int(time.time()))

    def sync_time(self, current_time_sec: int):
        # Сверим часы:
        # 1. Определим какой сейчас играет трек: self._current_track_index
        # 2. Выставим соответствующее время проигрывания: self._play_time
        elapsed_time_sec = current_time_sec - self._last_sync_sec
        self._last_sync_sec = current_time_sec
        if self._play_state != PlayState.play:
            return self._current_track_index, self._play_time_sec

        current_track = self._tracks[self._tracks_indexes[self._current_track_index]]
        if self._repeat_mode == RepeatMode.ONE:
            self._play_time_sec = (self._play_time_sec + elapsed_time_sec) % current_track.total_time
            return self._current_track_index, self._play_time_sec

        # self._repeat_mode == RepeatMode.OFF и весь список уже проигрался
        if self._repeat_mode == RepeatMode.OFF and (self._play_time_sec + elapsed_time_sec) > self.summary_time():
            self._current_track_index = 0
            self._play_time_sec = 0
            self._play_state = PlayState.stop
            return self._current_track_index, self._play_time_sec

        # self._repeat_mode == RepeatMode.ALL
        self._play_time_sec = (self._play_time_sec + elapsed_time_sec) % self.summary_time()
        while self._play_time_sec > current_track.total_time:
            self._play_time_sec -= current_track.total_time
            self._current_track_index = (self._current_track_index + 1) % self.count_tracks()
            current_track = self._tracks[self._tracks_indexes[self._current_track_index]]

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
        self._current_track_index += 1
        if self._current_track_index >= self.count_tracks():
            self._current_track_index = 0
        self._play_time_sec = 0

    def previous_track(self):
        self.sync()
        self._current_track_index -= 1
        if self._current_track_index < 0:
            self._current_track_index = self.count_tracks() - 1
        self._play_time_sec = 0

    def summary_time(self):
        return sum(self._tracks[i].total_time for i in range(self.count_tracks()))

    def shuffle_on(self):
        random.shuffle(self._tracks_indexes)
        self._current_track_index = self._tracks_indexes.index(self._current_track_index)

    def shuffle_off(self):
        # восстанавливаем порядок следования индексов треков:
        # 1. индекс трека равен порядковому номеру трека
        self._current_track_index = self._tracks_indexes[self._current_track_index]

        # 2. индексы треков в списке воспроизведения расположены друг за другом по возрастанию
        self._tracks_indexes.sort()

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
        self.assertEqual(track_index, self._yamahaPlaylist._current_track_index)
        self.assertEqual(track_index, self._yamahaPlaylist._tracks_indexes[self._yamahaPlaylist._current_track_index])
        self.assertEqual(self._yamahaPlaylist.current_track().track, "People Make the World Go Round")
        self.assertEqual(self._yamahaPlaylist._play_time_sec, 0)

    def test_sync(self):
        # если проигрывание было запущено - время синхронизируется с учётом прошедшего времени
        play_time = 3
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(play_time, self._yamahaPlaylist._play_time_sec)

        # если проигрывание было приостановлено - время проигрывания не изменится
        play_time = 10
        self._yamahaPlaylist.pause()
        last_play_time = self._yamahaPlaylist._play_time_sec
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(last_play_time, self._yamahaPlaylist._play_time_sec)

        # если проигрывание было остановлено - время проигрывания остаётся равным нулю
        play_time = 10
        self._yamahaPlaylist.stop()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(0, self._yamahaPlaylist._play_time_sec)

    def test_sync_after_first_track(self):
        # после проигрывания первого трека - запускается следующий
        play_time = 164 + 3
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(1, self._yamahaPlaylist._current_track_index)
        self.assertEqual(3, self._yamahaPlaylist._play_time_sec)

    def test_sync_after_second_track(self):
        # после проигрывания первого и второго треков - запускается третий
        play_time = 164 + 168 + 5
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self.assertEqual(2, self._yamahaPlaylist._current_track_index)
        self.assertEqual(5, self._yamahaPlaylist._play_time_sec)

    def test_repeat_off(self):
        # после проигрывания всех треков в режиме RepeatMode.OFF:
        # 1. трек переключится на первый
        # 2. время проигрывания станет равным 0
        # 3. воспроизведение закончится (состояние проигрывания станет равным PlayState.stop)
        play_time = 5
        self._yamahaPlaylist.repeat_off()
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec +
                                       self._yamahaPlaylist.summary_time() + play_time)
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)
        self.assertEqual(0, self._yamahaPlaylist._play_time_sec)
        self.assertEqual(PlayState.stop, self._yamahaPlaylist._play_state)

    def test_repeat_one(self):
        # после проигрывания текущего трека в режиме RepeatMode.ONE
        # этот трек начнёт проигрываться снова и так далее
        play_time = 5
        self._yamahaPlaylist.repeat_one()
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec +
                                       self._yamahaPlaylist.current_track().total_time * 3 + play_time)
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)
        self.assertEqual(play_time, self._yamahaPlaylist._play_time_sec)
        self.assertEqual(PlayState.play, self._yamahaPlaylist._play_state)

    def test_repeat_all(self):
        # после проигрывания всех треков в режиме RepeatMode.ALL,
        # воспроизведение начинается циклически - с первого трека
        play_time = 5
        self._yamahaPlaylist.repeat_all()
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec +
                                       self._yamahaPlaylist.summary_time() + play_time)
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)
        self.assertEqual(play_time, self._yamahaPlaylist._play_time_sec)
        self.assertEqual(PlayState.play, self._yamahaPlaylist._play_state)

    def test_previous_track(self):
        # первый трек является текущим
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)

        # при переключении на предыдущий трек - текущим станет последний трек
        self._yamahaPlaylist.previous_track()
        self.assertEqual(2, self._yamahaPlaylist._current_track_index)

        self._yamahaPlaylist.previous_track()
        self.assertEqual(1, self._yamahaPlaylist._current_track_index)

        # при переключении на предыдущий трек - время воспроизведения всегда сбрасывается на 0
        play_time = 5
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self._yamahaPlaylist.previous_track()
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)
        self.assertEqual(0, self._yamahaPlaylist._play_time_sec)

    def test_next_track(self):
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)

        self._yamahaPlaylist.next_track()
        self.assertEqual(1, self._yamahaPlaylist._current_track_index)

        # текущим является последний трек
        self._yamahaPlaylist.next_track()
        self.assertEqual(2, self._yamahaPlaylist._current_track_index)

        # при переключении на следующий трек - текущим станет первый трек
        self._yamahaPlaylist.next_track()
        self.assertEqual(0, self._yamahaPlaylist._current_track_index)

        # при переключении на следующий трек - время воспроизведения всегда сбрасывается на 0
        play_time = 5
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)
        self._yamahaPlaylist.next_track()
        self.assertEqual(1, self._yamahaPlaylist._current_track_index)
        self.assertEqual(0, self._yamahaPlaylist._play_time_sec)

    def test_shuffle_on(self):
        play_time = 5
        self._yamahaPlaylist.set_track_index(1)
        self.assertEqual(1, self._yamahaPlaylist._current_track_index)
        self.assertEqual(1, self._yamahaPlaylist._tracks_indexes[self._yamahaPlaylist._current_track_index])
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)

        # порядковый индекс текущего трека после "перемешивания" не меняется
        # меняется лишь порядок воспроизведения
        self._yamahaPlaylist.shuffle_on()
        self.assertEqual(1, self._yamahaPlaylist._tracks_indexes[self._yamahaPlaylist._current_track_index])

        # также не меняется текущее время воспроизведения и состояние воспроизведения
        self.assertEqual(play_time, self._yamahaPlaylist._play_time_sec)
        self.assertEqual(PlayState.play, self._yamahaPlaylist._play_state)

    def test_shuffle_off(self):
        play_time = 5
        self._yamahaPlaylist.play()
        self._yamahaPlaylist.shuffle_on()
        current_track_index = self._yamahaPlaylist._tracks_indexes[self._yamahaPlaylist._current_track_index]
        self._yamahaPlaylist.sync_time(self._yamahaPlaylist._last_sync_sec + play_time)

        # порядковый индекс текущего трека после восстановления порядка не меняется
        self._yamahaPlaylist.shuffle_off()
        self.assertEqual(current_track_index, self._yamahaPlaylist._current_track_index)

        # после восстановления порядка, индекс текущего трека равен элементу по этому индексу в списке воспроизведения
        self.assertEqual(self._yamahaPlaylist._current_track_index,
                         self._yamahaPlaylist._tracks_indexes[self._yamahaPlaylist._current_track_index])

        # также не меняется текущее время воспроизведения и состояние воспроизведения
        self.assertEqual(play_time, self._yamahaPlaylist._play_time_sec)
        self.assertEqual(PlayState.play, self._yamahaPlaylist._play_state)

