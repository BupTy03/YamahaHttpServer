from YamahaZone import YamahaZone
from YamahaNetusb import YamahaNetusb
from YamahaTuner import YamahaTuner
from YamahaCD import YamahaCD
from YamahaTrack import YamahaTrack
from YamahaPlaylist import YamahaPlaylist


class YamahaSystem(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(YamahaSystem, cls).__new__(cls)
            cls.instance._zones = [
                YamahaZone(name="main", input_name="spotify", mute=False, power="on", volume=5),
                YamahaZone(name="zone1", input_name="airplay", mute=True, power="standby", volume=0),
                YamahaZone(name="zone2", input_name="juke", mute=False, power="standby", volume=1),
                YamahaZone(name="zone3", input_name="tidal", mute=False, power="standby", volume=100)
            ]

            cls.instance._netusb = YamahaNetusb(YamahaPlaylist([
                YamahaTrack(track="We Will Rock You", album="News of the world", artist="Freddie Mercury",
                            total_time=121),
                YamahaTrack(track="We Are the Champions", album="News of the world", artist="Freddie Mercury",
                            total_time=179),
                YamahaTrack(track="Sheer Heart Attack", album="News of the world", artist="Freddie Mercury",
                            total_time=204)
            ]))
            cls.instance._tuner = YamahaTuner()
            cls.instance._cd = YamahaCD(YamahaPlaylist([
                YamahaTrack(track="Ben", album="Ben", artist="Michael Jackson", total_time=164),
                YamahaTrack(track="The Greatest Show on Earth", album="Ben", artist="Michael Jackson", total_time=168),
                YamahaTrack(track="People Make the World Go Round", album="Ben", artist="Michael Jackson",
                            total_time=195)
            ]))

        return cls.instance

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
