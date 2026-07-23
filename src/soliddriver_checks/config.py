import os
import json
from .version import __VERSION__
from datetime import datetime


def get_version():
    return f"version: {__VERSION__}"


def generate_timestamp():
    return f"timestamp: {datetime.now()}"


class SDCConf:
    def __init__(self):
        pkg_path = os.path.dirname(__file__)
        cfg_path = f"{pkg_path}/config/soliddriver-checks.conf"

        with open(cfg_path, "r") as fp:
            self._conf = json.load(fp)

    def get_valid_licenses(self):
        return self._conf["valid-licenses"]

    def get_km_sig_keys(self):
        return self._conf["km"]["sig-keys"]

    def get_km_html_warning(self):
        return self._conf["km"]["html"]["warning"]

    def get_km_html_error(self):
        return self._conf["km"]["html"]["error"]
