import os

from YamahaPlaylist import YamahaPlaylist
from YamahaTrack import YamahaTrack
from YamahaZone import YamahaZone


class YamahaNetusbPreset:
    def __init__(self, input_name="unknown", text=""):
        self.input = input_name
        self.text = text


class YamahaNetusb:
    def __init__(self, presets: list, playlist: YamahaPlaylist):
        self._input = "spotify"
        self._repeat_mode = "off"   # "off" / "one" / "all"
        self._shuffle_mode = "off"  # "off" / "on" / "songs" / "albums"
        self._playlist = playlist
        self._presets = presets

    def set_input(self, input: str):
        self._input = input

    def play(self):
        self._playlist.play()

    def stop(self):
        self._playlist.stop()

    def pause(self):
        self._playlist.pause()

    def select_track_index(self, index: int):
        self._playlist.stop()
        self._playlist.set_track_index(index)

    def play_track_index(self, index: int):
        self._playlist.play()
        self._playlist.set_track_index(index)

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

    def presets_list(self):
        return self._presets

    def store_preset(self, num: int):
        assert 1 <= num <= len(self._presets)
        preset_index = num - 1
        self._presets[preset_index] = YamahaNetusbPreset(input_name=self._input, text=f"Preset for {self._input}")

    def recall_preset(self, zone: YamahaZone, num: int):
        assert 1 <= num <= len(self._presets)

        preset_index = num - 1
        current_preset = self._presets[preset_index]
        self._input = current_preset.input
        zone.input_name = current_preset.input

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
            "albumart_url": "file:///" + os.path.abspath(current_track.albumart_url).replace('\\', '/'),
            "track": current_track.track
        }

    def list_info(self, index_from: int, chunk_size: int):
        return self._playlist.slice_to_list_info(index_from, chunk_size)
