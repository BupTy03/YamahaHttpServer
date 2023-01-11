def is_valid_power_mode(power: str):
    return power in {"on", "standby"}


def is_valid_sound_program(sound_program: str):
    return sound_program in {"munich_a", "munich_b", "munich", "frankfurt", "stuttgart", "vienna", "amsterdam", "usa_a",
                             "usa_b",
                             "tokyo", "freiburg", "royaumont", "chamber", "concert", "village_gate", "village_vanguard",
                             "warehouse_loft", "cellar_club", "jazz_club", "roxy_theatre", "bottom_line", "arena",
                             "sports",
                             "action_game", "roleplaying_game", "game", "music_video", "music", "recital_opera",
                             "pavilion",
                             "disco", "standard", "spectacle", "sci-fi", "adventure", "drama", "talk_show",
                             "tv_program",
                             "mono_movie", "movie", "enhanced", "2ch_stereo", "5ch_stereo", "7ch_stereo", "9ch_stereo",
                             "11ch_stereo", "stereo", "surr_decoder", "my_surround", "target", "straight", "off"}


class YamahaZone:
    def __init__(self, name: str, input_name: str, mute: bool, power: str, volume: int, sound_program: str):
        assert is_valid_power_mode(power), "Invalid power mode"
        self.name = name
        self.input_name = input_name
        self.mute = mute
        self.power = power
        self.volume = volume
        self.sound_program = sound_program

    def set_power(self, power: str):
        assert is_valid_power_mode(power), "Invalid power mode"
        self.power = power

    def set_sound_program(self, sound_program: str):
        assert is_valid_sound_program(sound_program), "Unknown sound program"
        self.sound_program = sound_program

    def status(self):
        return {
            "input": self.input_name,
            "mute": self.mute,
            "power": self.power,
            "volume": self.volume,
            "max_volume": 80,
            "sound_program": self.sound_program
        }
