def is_valid_power_mode(power: str):
    return power in ("on", "standby")


class YamahaZone:
    def __init__(self, name: str, input_name: str, mute: bool, power: str, volume: int):
        assert is_valid_power_mode(power)
        self.name = name
        self.input_name = input_name
        self.mute = mute
        self.power = power
        self.volume = volume

    def set_power(self, power: str):
        assert is_valid_power_mode(power)
        self.power = power

    def status(self):
        return {
            "input": self.input_name,
            "mute": self.mute,
            "power": self.power,
            "volume": self.volume,
            "max_volume": 80
        }
