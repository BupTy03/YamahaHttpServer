import json
import time
from pathlib import Path


class YamahaConfig(object):

    def __init__(self, file_name):
        self.fileName = file_name
        self.lastUpdateTimeInSeconds = 0.0
        self.data = {}

    def _update_from_file(self):
        p = Path(self.fileName)
        if p.stat().st_mtime > self.lastUpdateTimeInSeconds:
            with open(self.fileName, "r") as file:
                if not file:
                    return

                self.data = json.load(file)

        self.lastUpdateTimeInSeconds = time.time()

    def _store_to_file(self):
        with open(self.fileName, "w") as file:
            if not file:
                return

            file.write(json.dumps(self.data, indent=4))

    def read_field(self, field):
        self._update_from_file()
        if not self.data:
            return {}

        return self.data[field]

    def zone_info(self, zone_name):
        zones_info = self.read_field("zones_info")
        if zones_info:
            return zones_info[zone_name]
        return {}

    def set_zone_param(self, zone_name, param_name, param_value):
        self._update_from_file()
        self.data["zones_info"][zone_name][param_name] = param_value
        self._store_to_file()

    def toggle_repeat(self):
        self._update_from_file()
        repeat = self.data["netusb_play_info"]["repeat"]
        if repeat == "one":
            self.data["netusb_play_info"]["repeat"] = "off"
        elif repeat == "off":
            self.data["netusb_play_info"]["repeat"] = "one"

        self._store_to_file()

    def toggle_shuffle(self):
        self._update_from_file()
        shuffle = self.data["netusb_play_info"]["shuffle"]
        if shuffle == "on":
            self.data["netusb_play_info"]["shuffle"] = "off"
        elif shuffle == "off":
            self.data["netusb_play_info"]["shuffle"] = "on"

        self._store_to_file()

    def set_playback(self, playback):
        self._update_from_file()
        self.data["netusb_play_info"]["playback"] = playback
        self._store_to_file()

    def set_switch_preset(self, switch_preset):
        self._update_from_file()
        self.data["tuner_play_info"]["switch_preset"] = switch_preset
        self._store_to_file()

