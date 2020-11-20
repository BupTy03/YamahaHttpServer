from http.server import HTTPServer, BaseHTTPRequestHandler
from YamahaConfig import YamahaConfig

import urllib
import json
import re


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.config = YamahaConfig("config.json")
        self.getZoneNameRegExp = re.compile("/([^/]+)/getStatus$")
        super().__init__(request, client_address, server)

    def _get_zone_name(self, path):
        groups = re.findall(self.getZoneNameRegExp, path)
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
            self._send_json(self.config.location_info())
        elif parsed_path.path.endswith("getStatus"):
            zone_name = self._get_zone_name(parsed_path.path)
            self._send_json(self.config.zone_info(zone_name))
        elif parsed_path.path.endswith("tuner/getPlayInfo"):
            self._send_json(self.config.tuner_play_info())
        elif parsed_path.path.endswith("netusb/getPlayInfo"):
            self._send_json(self.config.netusb_play_info())
        else:
            self.send_response(404)
            self.end_headers()

def main():
    httpd = HTTPServer(("localhost", 80), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
