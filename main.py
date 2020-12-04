from http.server import HTTPServer, BaseHTTPRequestHandler
from YamahaConfig import YamahaConfig, to_boolean

import urllib
import json
import re


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.config = YamahaConfig("config.json")
        self.inputOrZoneNameRegExp = re.compile("/([^/]+)/[^/]+$")
        super().__init__(request, client_address, server)

    def _get_zone_name(self, path):
        groups = re.findall(self.inputOrZoneNameRegExp, path)
        if groups and len(groups) > 0:
            return groups[0]
        return "main"

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

    def _make_response(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path.endswith("getLocationInfo"):
            self._send_json(self.config.read_field("location_info"))
        elif parsed_path.path.endswith("getStatus"):
            zone_name = self._get_zone_name(parsed_path.path)
            self._send_json(self.config.zone_info(zone_name))

        elif parsed_path.path.endswith("cd/getPlayInfo"):
            self._send_json(self.config.read_play_info("cd"))
        elif parsed_path.path.endswith("tuner/getPlayInfo"):
            self._send_json(self.config.read_play_info("tuner"))
        elif parsed_path.path.endswith("netusb/getPlayInfo"):
            self._send_json(self.config.read_play_info("netusb"))
        elif parsed_path.path.endswith("system/getFeatures"):
            self._send_json(self.config.get_system_features())

        elif parsed_path.path.endswith("setInput"):
            zone_name = self._get_zone_name(parsed_path.path)
            input_name = parsed_path.query.split('=')[1]
            self.config.set_zone_param(zone_name, "input", input_name)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setMute"):
            zone_name = self._get_zone_name(parsed_path.path)
            mute = to_boolean(parsed_path.query.split('=')[1])
            self.config.set_zone_param(zone_name, "mute", mute)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setVolume"):
            zone_name = self._get_zone_name(parsed_path.path)
            volume = int(parsed_path.query.split('=')[1])
            self.config.set_zone_param(zone_name, "volume", volume)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setPower"):
            zone_name = self._get_zone_name(parsed_path.path)
            power_mode = parsed_path.query.split('=')[1]
            self.config.set_zone_param(zone_name, "power", power_mode)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("toggleRepeat"):
            self.config.toggle_repeat(self._get_input_type(parsed_path.path))
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("toggleShuffle"):
            self.config.toggle_shuffle(self._get_input_type(parsed_path.path))
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("setPlayback"):
            playback = parsed_path.query.split('=')[1]
            self.config.set_playback(self._get_input_type(parsed_path.path), playback)
            self._send_json({"response_code": 0})
        elif parsed_path.path.endswith("switchPreset"):
            switch_preset = parsed_path.query.split('=')[1]
            self.config.set_switch_preset(switch_preset)
            self._send_json({"response_code": 0})
        else:
            print(f"Unknown request: {parsed_path}")
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
