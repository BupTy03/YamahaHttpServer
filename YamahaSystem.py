import json
from YamahaZone import YamahaZone
from YamahaNetusb import YamahaNetusb
from YamahaTuner import YamahaTuner
from YamahaCD import YamahaCD
from YamahaTrack import YamahaTrack
from YamahaPlaylist import YamahaPlaylist


def load_zones(data: dict):
    zones_info = data["zones_info"]
    zones = []
    for key, value in zones_info.items():
        zones.append(YamahaZone(name=key,
                                input_name=value["input"],
                                mute=value["mute"],
                                power=value["power"],
                                volume=value["volume"]))
    return zones


def load_playlist(playlist: list):
    result = []
    for item in playlist:
        result.append(YamahaTrack(track=item["track"],
                                  album=item["album"],
                                  artist=item["artist"],
                                  total_time=item["total_time"]))
    return result


def store_zones_info(zones_list: list):
    result = {}
    for zone in zones_list:
        result[zone.name] = zone.status()
    return result


class YamahaSystem(object):

    def __new__(cls):
        return cls.instance

    @classmethod
    def load(cls, filename):
        if not hasattr(cls, "instance"):
            data = None
            with open(filename, "r") as file:
                data = json.load(file)

            cls.instance = super(YamahaSystem, cls).__new__(cls)
            cls.instance._zones = load_zones(data)
            cls.instance._netusb = YamahaNetusb(YamahaPlaylist(load_playlist(data["playlist"]["netusb"])))
            cls.instance._tuner = YamahaTuner()
            cls.instance._cd = YamahaCD(YamahaPlaylist(load_playlist(data["playlist"]["cd"])))

    @classmethod
    def store(cls, filename):
        data = None
        with open(filename, "r") as file:
            data = json.load(file)

        data["zones_info"] = store_zones_info(cls.instance._zones)
        with open(filename, "w") as file:
            file.write(json.dumps(data, indent=4))

    def get_zone(self, name):
        zones = list(filter(lambda z: z.name == name, self._zones))
        if len(zones) > 0:
            return zones[0]
        else:
            raise Exception(f"Zone with name '{name}' is not found")

    def netusb(self):
        return self._netusb

    def tuner(self):
        return self._tuner

    def cd(self):
        return self._cd

    def get_input(self, name: str):
        assert name in ("netusb", "tuner", "cd")
        if name == "netusb":
            return self.netusb()
        elif name == "tuner":
            return self.tuner()
        elif name == "cd":
            return self.cd()


class load_yamaha:
    def __init__(self, config_file: str):
        self._config_file = config_file

    def __enter__(self):
        YamahaSystem.load(self._config_file)

    def __exit__(self, type, value, traceback):
        YamahaSystem.store(self._config_file)

