from http.server import HTTPServer, BaseHTTPRequestHandler
from YamahaConfig import YamahaConfig

import urllib
import json
import re


def to_boolean(str):
    return str == "true"


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.config = YamahaConfig("config.json")
        self.zoneNameRegExp = re.compile("/([^/]+)/[^/]+$")
        super().__init__(request, client_address, server)

    def _get_zone_name(self, path, reg_exp):
        groups = re.findall(reg_exp, path)
        if groups and len(groups) > 0:
            return groups[0]
        return "main"

    def _send_json(self, json_answer):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(json_answer).encode('utf-8'))

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path.endswith("getLocationInfo"):
            self._send_json(self.config.read_field("location_info"))
        elif parsed_path.path.endswith("getStatus"):
            zone_name = self._get_zone_name(parsed_path.path, self.zoneNameRegExp)
            self._send_json(self.config.zone_info(zone_name))
        elif parsed_path.path.endswith("tuner/getPlayInfo"):
            self._send_json(self.config.read_field("tuner_play_info"))
        elif parsed_path.path.endswith("netusb/getPlayInfo"):
            self._send_json(self.config.read_field("netusb_play_info"))
        elif parsed_path.path.endswith("setInput"):
            zone_name = self._get_zone_name(parsed_path.path, self.zoneNameRegExp)
            input_name = parsed_path.query.split('=')[1]
            self.config.set_zone_param(zone_name, "input", input_name)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setMute"):
            zone_name = self._get_zone_name(parsed_path.path, self.zoneNameRegExp)
            mute = to_boolean(parsed_path.query.split('=')[1])
            self.config.set_zone_param(zone_name, "mute", mute)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setVolume"):
            zone_name = self._get_zone_name(parsed_path.path, self.zoneNameRegExp)
            volume = int(parsed_path.query.split('=')[1])
            self.config.set_zone_param(zone_name, "volume", volume)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setPower"):
            zone_name = self._get_zone_name(parsed_path.path, self.zoneNameRegExp)
            power_mode = parsed_path.query.split('=')[1]
            self.config.set_zone_param(zone_name, "power", power_mode)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("toggleRepeat"):
            self.config.toggle_repeat()
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("toggleShuffle"):
            self.config.toggle_shuffle()
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setPlayback"):
            playback = parsed_path.query.split('=')[1]
            self.config.set_playback(playback)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("switchPreset"):
            switch_preset = parsed_path.query.split('=')[1]
            self.config.set_switch_preset(switch_preset)
            self._send_json({"response_code": 0})
        else:
            print("Unknown request: {}".format(parsed_path))
            self.send_response(404)
            self.end_headers()


def main():
    httpd = HTTPServer(("localhost", 80), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
