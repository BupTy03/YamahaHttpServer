import json

from YamahaZone import YamahaZone
from YamahaNetusb import YamahaNetusb, YamahaNetusbPreset
from YamahaTuner import YamahaTuner, YamahaTunerPreset
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


def load_tuner_presets(presets_list: list):
    result = []
    for item in presets_list:
        result.append(YamahaTunerPreset(band=item["band"], number=item["number"]))
    return result


def store_tuner_presets_list(presets: list):
    result = []
    for item in presets:
        result.append({"band": item.band(), "number": item.number()})
    return result


def load_netusb_presets(presets_list: list):
    result = []
    for item in presets_list:
        result.append(YamahaNetusbPreset(input_name=item["input"], text=item["text"]))
    return result


def store_netusb_presets_list(presets: list):
    result = []
    for item in presets:
        result.append({"input": item.input, "text": item.text})
    return result


class YamahaSystem:
    def __new__(cls):
        return cls.instance

    @classmethod
    def load(cls, filename: str):
        data = None
        with open(filename, "r") as file:
            data = json.load(file)

        cls.instance = super(YamahaSystem, cls).__new__(cls)
        cls.instance._zones = load_zones(data)
        cls.instance._netusb = YamahaNetusb(load_netusb_presets(data["presets"]["netusb"]),
                                            YamahaPlaylist(load_playlist(data["playlist"]["netusb"])))

        cls.instance._tuner = YamahaTuner(load_tuner_presets(data["presets"]["tuner"]))
        cls.instance._cd = YamahaCD(YamahaPlaylist(load_playlist(data["playlist"]["cd"])))

    @classmethod
    def store(cls, filename: str):
        data = None
        with open(filename, "r") as file:
            data = json.load(file)

        data["zones_info"] = store_zones_info(cls.instance._zones)
        data["presets"]["tuner"] = store_tuner_presets_list(cls.instance._tuner.presets_list())
        data["presets"]["netusb"] = store_netusb_presets_list(cls.instance._netusb.presets_list())
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

