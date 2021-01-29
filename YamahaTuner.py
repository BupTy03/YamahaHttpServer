from YamahaZone import YamahaZone


def is_valid_band(band: str):
    return band in ("am", "fm", "dab", "unknown")


class YamahaTunerPreset:
    def __init__(self, band="unknown", number=0):
        assert is_valid_band(band), "Wrong band"
        assert number >= 0, "Wrong preset number"

        self._band = band
        self._number = number

    def set_band(self, band: str):
        assert is_valid_band(band)
        self._band = band

    def band(self):
        return self._band

    def set_number(self, num: int):
        assert num >= 0, "Invalid freq num, expected >= 0"
        self._number = num

    def number(self):
        return self._number


class YamahaTuner:
    MIN_DAB_FREQ = 174000
    MAX_DAB_FREQ = 240000

    def __init__(self, presets: list):
        self._band = "am"  # "am" / "fm" / "dab
        self._frequencies = {
            "am": 103100,
            "fm": 106200,
            "dab": 235776
        }
        self._dab_service_id = 0
        self._current_preset = 0
        self._presets = presets
        self._no_preset = False

    def _apply_preset(self, preset):
        self._band = preset.band()
        self._frequencies[self._band] = preset.number()

    def frequency(self):
        return self._frequencies[self._band]

    def set_frequency(self, freq: int):
        if self._presets[self._current_preset].number() != freq:
            self._no_preset = True

        self._frequencies[self._band] = freq

    def next_preset(self):
        self._current_preset += 1
        if self._current_preset >= len(self._presets):
            self._current_preset = 0

        self._apply_preset(self._presets[self._current_preset])

    def previous_preset(self):
        self._current_preset -= 1
        if self._current_preset < 0:
            self._current_preset = len(self._presets) - 1

        self._apply_preset(self._presets[self._current_preset])

    def next_dab(self):
        self._dab_service_id = min(self._dab_service_id + 1, 65)
        self._frequencies["dab"] = YamahaTuner.MIN_DAB_FREQ + self._dab_service_id * 1000

        if self._presets[self._current_preset].number() != self.frequency():
            self._no_preset = True

    def prev_dab(self):
        self._dab_service_id = max(self._dab_service_id - 1, 0)
        self._frequencies["dab"] = YamahaTuner.MIN_DAB_FREQ + self._dab_service_id * 1000

        if self._presets[self._current_preset].number() != self.frequency():
            self._no_preset = True

    def play_info(self):
        preset_num = 0 if self._no_preset else int(self._current_preset + 1)
        result = {
            "band": self._band,
            "am": {"freq": self._frequencies["am"], "preset": preset_num},
            "fm": {"freq": self._frequencies["fm"], "preset": preset_num},
            "dab": {"freq": self._frequencies["dab"], "preset": preset_num}
        }

        return result

    def presets_list(self):
        return self._presets

    def store_preset(self, num: int):
        assert 1 <= num <= len(self._presets), f"Preset num is out of range [1, {len(self._presets)}]"
        preset_index = num - 1
        self._no_preset = False
        self._current_preset = preset_index
        self._presets[preset_index] = YamahaTunerPreset(band=self._band, number=self._frequencies[self._band])

    def recall_preset(self, zone: YamahaZone, band: str, num: int):
        assert is_valid_band(band), "Wrong band"
        assert 1 <= num <= len(self._presets), f"Preset num is out of range [1, {len(self._presets)}]"

        if band == "unknown":
            return

        preset_index = num - 1
        preset = self._presets[preset_index]
        zone.input_name = preset.band()
        self._apply_preset(preset)
        self._current_preset = preset_index
        self._no_preset = False

    def set_band(self, band: str):
        assert is_valid_band(band), "Wrong band"
        if self._presets[self._current_preset].band() != band:
            self._no_preset = True

        self._band = band


def switch_preset(tuner: YamahaTuner, direction: str):
    assert direction in ("next", "previous"), "Wrong tuning direction"
    if direction == "next":
        tuner.next_preset()
    elif direction == "previous":
        tuner.previous_preset()
