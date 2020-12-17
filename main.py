from http.server import HTTPServer, BaseHTTPRequestHandler
from YamahaConfig import YamahaConfig, to_boolean
from YamahaSystem import YamahaSystem

import urllib
import json
import re


def set_playback(yamaha_input, playback):
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


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self._yamahaSystem = YamahaSystem()
        self.config = YamahaConfig("config.json")
        self.inputOrZoneNameRegExp = re.compile("/([^/]+)/[^/]+$")
        super().__init__(request, client_address, server)

    def _get_zone_name(self, path):
        groups = re.findall(self.inputOrZoneNameRegExp, path)
        if groups and len(groups) > 0:
            return groups[0]
        return ""

    def _get_input_type(self, path):
        groups = re.findall(self.inputOrZoneNameRegExp, path)
        if groups and len(groups) > 0:
            return groups[0]
        return ""

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
        query = dict(urllib.parse.parse_qsl(parsed.query))

        if parsed_path.endswith("getLocationInfo"):
            self._send_json(self.config.read_field("location_info"))
        elif parsed_path.endswith("getStatus"):
            zone_name = self._get_zone_name(parsed_path)
            self._send_json(self._yamahaSystem.get_zone(zone_name).status())
        elif parsed_path.endswith("getPlayInfo"):
            input_type = self._get_input_type(parsed_path)
            self._send_json(self._yamahaSystem.get_input(input_type).play_info())

        elif parsed_path.endswith("system/getFeatures"):
            self._send_json(self.config.get_system_features())

        elif parsed_path.endswith("setInput"):
            zone_name = self._get_zone_name(parsed_path)
            self._yamahaSystem.get_zone(zone_name).input_name = query["input"]
            self._send_success()
        elif parsed_path.endswith("setMute"):
            zone_name = self._get_zone_name(parsed_path)
            self._yamahaSystem.get_zone(zone_name).mute = to_boolean(query["enable"])
            self._send_success()
        elif parsed_path.endswith("setVolume"):
            zone_name = self._get_zone_name(parsed_path)
            self._yamahaSystem.get_zone(zone_name).volume = int(query["volume"])
            self._send_success()
        elif parsed_path.endswith("setPower"):
            zone_name = self._get_zone_name(parsed_path)
            self._yamahaSystem.get_zone(zone_name).set_power(query["power"])
            self._send_success()

        elif parsed_path.endswith("toggleRepeat"):
            input_type = self._get_input_type(parsed_path)
            self._yamahaSystem.get_input(input_type).toggle_repeat()
            self._send_success()
        elif parsed_path.endswith("toggleShuffle"):
            input_type = self._get_input_type(parsed_path)
            self._yamahaSystem.get_input(input_type).toggle_shuffle()
            self._send_success()
        elif parsed_path.endswith("setPlayback"):
            if query["playback"] == "track_select":
                self._yamahaSystem.cd().set_track_num(int(query["num"]))
            else:
                input_type = self._get_input_type(parsed_path)
                set_playback(self._yamahaSystem.get_input(input_type), query["playback"])
            self._send_success()
        elif parsed_path.endswith("switchPreset"):
            # TODO: presets
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


def main():
    httpd = HTTPServer(("localhost", 80), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
