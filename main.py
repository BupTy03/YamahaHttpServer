import urllib
import json
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler
from YamahaSystem import YamahaSystem, load_yamaha
from YamahaTuner import YamahaTuner, switch_preset


def to_boolean(value: str):
    assert value in ("true", "false")
    return value == "true"


def set_playback(yamaha_input, playback: str):
    assert playback in ("play", "stop", "pause", "next", "previous")

    if playback == "play":
        yamaha_input.play()
    elif playback == "stop":
        yamaha_input.stop()
    elif playback == "pause":
        yamaha_input.pause()
    elif playback == "next":
        yamaha_input.next_track()
    elif playback == "previous":
        yamaha_input.previous_track()


def get_sender_from_path(path: str):
    # пример пути: "/YamahaExtendedControl/v1/main/getStatus"
    # разобьётся на: ['', 'YamahaExtendedControl', 'v1', 'main', 'getStatus']
    # элемент под индексом 3 ('main' - имя зоны) - то что нам нужно
    sender = path.split("/")[3]
    assert sender in ("main", "zone1", "zone2", "zone3", "netusb", "tuner", "cd")
    return sender


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self._yamahaSystem = YamahaSystem()
        super().__init__(request, client_address, server)

    def _send_json(self, json_answer):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(json_answer).encode('utf-8'))

    def _send_success(self):
        self._send_json({"response_code": 0})

    def _make_response(self):
        parsed = urllib.parse.urlparse(self.path)
        parsed_path = parsed.path
        query_params = dict(urllib.parse.parse_qsl(parsed.query))
        sender = get_sender_from_path(parsed_path)

        if parsed_path.endswith("getStatus"):
            self._send_json(self._yamahaSystem.get_zone(sender).status())
        elif parsed_path.endswith("getPlayInfo"):
            self._send_json(self._yamahaSystem.get_input(sender).play_info())

        elif parsed_path.endswith("setInput"):
            self._yamahaSystem.get_zone(sender).input_name = query_params["input"]
            self._send_success()
        elif parsed_path.endswith("setMute"):
            self._yamahaSystem.get_zone(sender).mute = to_boolean(query_params["enable"])
            self._send_success()
        elif parsed_path.endswith("setVolume"):
            self._yamahaSystem.get_zone(sender).volume = int(query_params["volume"])
            self._send_success()
        elif parsed_path.endswith("setPower"):
            self._yamahaSystem.get_zone(sender).set_power(query_params["power"])
            self._send_success()

        elif parsed_path.endswith("toggleRepeat"):
            self._yamahaSystem.get_input(sender).toggle_repeat()
            self._send_success()
        elif parsed_path.endswith("toggleShuffle"):
            self._yamahaSystem.get_input(sender).toggle_shuffle()
            self._send_success()
        elif parsed_path.endswith("setPlayback"):
            if query_params["playback"] == "track_select":
                assert sender == "cd"
                self._yamahaSystem.cd().set_track_num(int(query_params["num"]))
            else:
                set_playback(self._yamahaSystem.get_input(sender), query_params["playback"])
            self._send_success()
        elif parsed_path.endswith("switchPreset"):
            assert sender == "tuner"
            switch_preset(self._yamahaSystem.tuner(), query_params["dir"])
            self._send_success()
        elif parsed_path.endswith("setDabService"):
            assert sender == "tuner"

            direction = query_params["dir"]
            assert direction in ("previous", "next")

            if direction == "previous":
                self._yamahaSystem.tuner().prev_dab()
            elif direction == "next":
                self._yamahaSystem.tuner().next_dab()

            self._send_success()
        elif parsed_path.endswith("storePreset"):
            assert sender in ("tuner", "netusb")
            self._yamahaSystem.get_input(sender).store_preset(int(query_params["num"]))
            self._send_success()
        elif parsed_path.endswith("setFreq"):
            assert sender == "tuner"
            assert query_params["band"] in ("am", "fm")
            assert query_params["tuning"] == "direct"
            self._yamahaSystem.tuner().set_frequency(int(query_params["num"]))
            self._send_success()
        elif parsed_path.endswith("recallPreset"):
            assert sender in ("tuner", "netusb")

            zone = self._yamahaSystem.get_zone(query_params["zone"])
            preset_num = int(query_params["num"])
            if sender == "tuner":
                self._yamahaSystem.tuner().recall_preset(zone=zone, band=query_params["band"], num=preset_num)
            elif sender == "netusb":
                self._yamahaSystem.netusb().recall_preset(zone=zone, num=preset_num)
            self._send_success()

        else:
            print(f"Unknown request: {self.path}")
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        try:
            self._make_response()
        except Exception as e:
            print(f"Exception: {e}")
            self.send_response(400)
            self.end_headers()


class start_server:
    def __enter__(self):
        self.httpd = HTTPServer(("", 80), SimpleHTTPRequestHandler)
        self.current_thread = threading.Thread(target=self.httpd.serve_forever)
        self.current_thread.start()

    def __exit__(self, type, value, traceback):
        self.httpd.shutdown()
        self.current_thread.join()


def main():
    with load_yamaha("config.json"):
        with start_server():
            input("Press 'Enter' to exit\n")


if __name__ == "__main__":
    main()
