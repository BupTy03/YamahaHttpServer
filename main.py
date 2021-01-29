import urllib
import json
import threading
import sys
import argparse

from http.server import HTTPServer, BaseHTTPRequestHandler
from YamahaSystem import YamahaSystem, load_yamaha
from YamahaTuner import YamahaTuner, switch_preset
from YamahaNetusb import YamahaNetusb


def to_boolean(value: str):
    assert value in ("true", "false")
    return value == "true"


def set_playback(yamaha_input, playback: str):
    assert playback in ("play", "stop", "pause", "next", "previous",
                        "fast_reverse_start", "fast_reverse_end",
                        "fast_forward_start", "fast_forward_end")

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
    elif playback == "fast_reverse_start":
        yamaha_input.fast_reverse_start()
    elif playback == "fast_reverse_end":
        yamaha_input.fast_reverse_end()
    elif playback == "fast_forward_start":
        yamaha_input.fast_forward_start()
    elif playback == "fast_forward_end":
        yamaha_input.fast_forward_end()


def get_sender_from_path(path: str):
    # пример пути: "/YamahaExtendedControl/v1/main/getStatus"
    # разобьётся на: ['', 'YamahaExtendedControl', 'v1', 'main', 'getStatus']
    # элемент под индексом 3 ('main' - имя зоны) - то что нам нужно
    sender = path.split("/")[3]
    assert sender in ("main", "zone1", "zone2", "zone3", "netusb", "tuner", "cd")
    return sender


def is_feedback(path: str):
    return path.endswith("getStatus") or path.endswith("getPlayInfo") or path.endswith("getListInfo")


def set_list_control(netusb: YamahaNetusb, query_params: dict):
    type_ = query_params["type"]
    assert type_ in ("select", "play", "return")

    if type_ == "return":
        return

    index = int(query_params["index"])
    if type_ == "select":
        netusb.select_track_index(index)
    elif type_ == "play":
        netusb.play_track_index(index)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self._yamahaSystem = YamahaSystem()
        super().__init__(request, client_address, server)

    def _send_json(self, json_answer):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        json_answer["response_code"] = 0
        self.wfile.write(json.dumps(json_answer, indent=4).encode('utf-8'))

    def _send_success(self):
        self._send_json({"response_code": 0})

    def _check_sender(self, sender: str, expected_senders):
        if type(expected_senders) is str:
            assert sender == expected_senders, "Wrong sender, " + expected_senders + " expected"
        else:
            assert sender in expected_senders, "Wrong sender, " + " or ".join(expected_senders) + " expected"

    def _make_response(self):
        parsed = urllib.parse.urlparse(self.path)
        parsed_path = parsed.path
        query_params = dict(urllib.parse.parse_qsl(parsed.query))
        sender = get_sender_from_path(parsed_path)

        if is_feedback(parsed_path):
            self.print_feedback()
        else:
            self.print_command()

        if parsed_path.endswith("getStatus"):
            self._send_json(self._yamahaSystem.get_zone(sender).status())
        elif parsed_path.endswith("getPlayInfo"):
            self._send_json(self._yamahaSystem.get_input(sender).play_info())
        elif parsed_path.endswith("getListInfo"):
            self._check_sender(sender, "netusb")
            input_name = query_params["input"]
            self._send_json(self._yamahaSystem.netusb().list_info(index_from=int(query_params["index"]),
                                                                  chunk_size=int(query_params["size"])))

        elif parsed_path.endswith("setInput"):
            self._yamahaSystem.set_input(zone=sender, input=query_params["input"])
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
                assert sender == "cd", "Wrong sender, cd expected"
                self._yamahaSystem.cd().set_track_num(int(query_params["num"]))
            else:
                set_playback(self._yamahaSystem.get_input(sender), query_params["playback"])
            self._send_success()
        elif parsed_path.endswith("switchPreset"):
            self._check_sender(sender, "tuner")
            switch_preset(self._yamahaSystem.tuner(), query_params["dir"])
            self._send_success()
        elif parsed_path.endswith("setDabService"):
            self._check_sender(sender, "tuner")

            direction = query_params["dir"]
            assert direction in ("previous", "next"), 'Wrong direction, "previous" or "next" expected'

            if direction == "previous":
                self._yamahaSystem.tuner().prev_dab()
            elif direction == "next":
                self._yamahaSystem.tuner().next_dab()

            self._send_success()
        elif parsed_path.endswith("storePreset"):
            self._check_sender(sender, ("tuner", "netusb"))
            self._yamahaSystem.get_input(sender).store_preset(int(query_params["num"]))
            self._send_success()
        elif parsed_path.endswith("setBand"):
            self._check_sender(sender, "tuner")
            self._yamahaSystem.tuner().set_band(query_params["band"])
            self._send_success()
        elif parsed_path.endswith("setFreq"):
            self._check_sender(sender, "tuner")
            assert query_params["band"] in ("am", "fm"), 'Wrong band, "am" or "fm" expected'
            assert query_params["tuning"] == "direct", 'Wrong tuning, only "direct" is supported by emulator'
            self._yamahaSystem.tuner().set_frequency(int(query_params["num"]))
            self._send_success()
        elif parsed_path.endswith("recallPreset"):
            self._check_sender(sender, ("tuner", "netusb"))

            zone = self._yamahaSystem.get_zone(query_params["zone"])
            preset_num = int(query_params["num"])
            if sender == "tuner":
                self._yamahaSystem.tuner().recall_preset(zone=zone, band=query_params["band"], num=preset_num)
            elif sender == "netusb":
                self._yamahaSystem.netusb().recall_preset(zone=zone, num=preset_num)
            self._send_success()
        elif parsed_path.endswith("setListControl"):
            set_list_control(netusb=self._yamahaSystem.netusb(), query_params=query_params)
            self._send_success()
        else:
            print(f"Unknown request: {self.path}")
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

    def print_command(self):
        if self._yamahaSystem._filter not in ("feedbacks", "f", "feed"):
            print(f"\033[33m{self.requestline}\033[0m")

    def print_feedback(self):
        if self._yamahaSystem._filter not in ("commands", "c", "comm"):
            print(f"\033[32m{self.requestline}\033[0m")

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
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filter")
    parsed_args = parser.parse_args(sys.argv[1:])

    with load_yamaha("config.json", parsed_args.filter):
        with start_server():
            input("Press 'Enter' to exit\n")


if __name__ == "__main__":
    main()
