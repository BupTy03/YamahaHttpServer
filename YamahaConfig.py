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

            file.write(json.dumps(self.data))

    def _read_field(self, field):
        self._update_from_file()
        if not self.data:
            return {}

        return self.data[field]

    def location_info(self):
        return self._read_field("location_info")

    def zone_info(self, zone_name):
        zones_info = self._read_field("zones_info")
        if zones_info:
            return zones_info[zone_name]
        return {}

    def tuner_play_info(self):
        return self._read_field("tuner_play_info")

    def netusb_play_info(self):
        return self._read_field("netusb_play_info")
