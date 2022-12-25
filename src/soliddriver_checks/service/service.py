#!/usr/bin/env python3

from threading import Lock, Thread, Timer
from bottle import route, run, response
from ..api.analysis import kms_to_json
import os
import json
import logging


class KMInfo:
    def __init__(self, interval):
        self._data_lock = Lock()
        self._info = json.dumps([])
        self._interval = interval
        t = Thread(target=self._async_refresh_data)
        t.start()

    @property
    def data(self):
        with self._data_lock:
            data = self._info
            return data

    def _async_refresh_data(self):
        while True:
            t = Timer(self._interval * 60 * 60, self._refresh_data)
            t.start()

    def _refresh_data(self):
        logging.info("start to refresh data...")
        new_data = kms_to_json()
        with self._data_lock:
            self._info = new_data
        logging.info("refreshing data is completed!")


def run_as_service(host="0.0.0.0", port=8080):
    interval = os.getenv("REFRESH_INTERVAL")
    interval = interval if interval is not None else 1
    logging.info("refresh interval: %s hour(s)" % interval)
    global kms
    kms = KMInfo(interval)
    run(host=host, port=port)


@route('/kms_info')
def kms_info():
    response.content_type = 'application/json'
    info = kms.data

    return info


if __name__ == "__main__":
    run_as_service()
