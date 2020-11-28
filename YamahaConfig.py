import json
import time
from pathlib import Path


def to_boolean(str):
    return str == "true"


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

    def _toggle_netusb_repeat(self):
        next_state = {
            "off": "one",
            "one": "all",
            "all": "off"
        }

        self.data["play_info"]["netusb"]["repeat"] = next_state[self.data["play_info"]["netusb"]["repeat"]]

    def _toggle_cd_repeat(self):
        next_state = {
            "off": "one",
            "one": "all",
            "all": "folder",
            "folder": "a-b",
            "a-b": "off"
        }

        self.data["play_info"]["cd"]["repeat"] = next_state[self.data["play_info"]["cd"]["repeat"]]

    def _toggle_netusb_shuffle(self):
        next_state = {
            "off": "on",
            "on": "songs",
            "songs": "albums",
            "albums": "off"
        }

        self.data["play_info"]["netusb"]["shuffle"] = next_state[self.data["play_info"]["netusb"]["shuffle"]]

    def _toggle_cd_shuffle(self):
        next_state = {
            "off": "on",
            "on": "folder",
            "folder": "program",
            "program": "off"
        }

        self.data["play_info"]["cd"]["shuffle"] = next_state[self.data["play_info"]["cd"]["shuffle"]]

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

    def read_play_info(self, play_info_type):
        self._update_from_file()
        return self.data["play_info"][play_info_type]

    def toggle_repeat(self, play_info_type):
        self._update_from_file()

        if "netusb" == play_info_type:
            self._toggle_netusb_repeat()
        elif "cd" == play_info_type:
            self._toggle_cd_repeat()
        else:
            assert False, "Wrong play_info_type {} for toggle_repeat".format(play_info_type)

        self._store_to_file()

    def toggle_shuffle(self, play_info_type):
        self._update_from_file()

        if "netusb" == play_info_type:
            self._toggle_netusb_shuffle()
        elif "cd" == play_info_type:
            self._toggle_cd_shuffle()
        else:
            assert False, "Wrong play_info_type {} for toggle_shuffle".format(play_info_type)

        self._store_to_file()

    def set_playback(self, play_info_type, playback):
        self._update_from_file()
        self.data["play_info"][play_info_type]["playback"] = playback
        self._store_to_file()

    def set_switch_preset(self, switch_preset):
        self._update_from_file()
        self.data["play_info"]["tuner"]["switch_preset"] = switch_preset
        self._store_to_file()

    def get_system_features(self):
        self._update_from_file()
        return self.data["system"]

