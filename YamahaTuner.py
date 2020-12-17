class YamahaTuner(object):
    MIN_DAB_FREQ = 174000
    MAX_DAB_FREQ = 240000

    def __init__(self):
        self._band = "am"  # "am" / "fm" / "dab
        self._frequencies = {
            "am": 1000,
            "fm": 1000,
            "dab": 1000
        }
        self._dab_service_id = 0

    def frequency(self):
        return self._frequencies[self._band]

    def set_frequency(self, freq: int):
        self._frequencies[self._band] = freq

    def next_dab(self):
        self._dab_service_id = min(self._dab_service_id + 1, 65)
        self._frequencies["dab"] = YamahaTuner.MIN_DAB_FREQ + self._dab_service_id * 1000

    def prev_dab(self):
        self._dab_service_id = max(self._dab_service_id - 1, 0)
        self._frequencies["dab"] = YamahaTuner.MIN_DAB_FREQ + self._dab_service_id * 1000

    def play_info(self):
        return {
            "band": self._band,
            "am": {"freq": self._frequencies["am"]},
            "fm": {"freq": self._frequencies["fm"]},
            "dab": {"freq": self._frequencies["dab"]}
        }

