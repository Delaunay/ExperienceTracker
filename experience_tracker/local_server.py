from flask_classful import FlaskView, route
from flask import Flask, request
from multiprocessing import Process
from typing import *

from experience_tracker.stats import StatStream


class LocalServer(FlaskView):
    """
        This is a local server that is started when the experience tracker is used to wrap around a script.
        This allow the  wrapped script to send data back to the tracker.
        The user will use the tracker log utility and will not have to deal with the server directly
    """
    route_base = '/'

    def __init__(self):
        self.namespaces: Dict[str, Dict[str, Any]] = {}

    def get_namespace(self, name):
        if name not in self.namespaces:
            self.namespaces[name] = {}

        return self.namespaces[name]

    def get_stream(self, namespace, key, drop_nfirst_obs=0):
        namespace = self.get_namespace(namespace)
        if key not in namespace:
            namespace[key] = StatStream(drop_nfirst_obs)

        return namespace[key]

    @route('/push', methods=['POST'])
    def push(self):
        print('receiving_pushing_key_value')
        json = request.json
        self.get_namespace(json['namespace'])[json['key']] = json['value']

        return '', 204

    @route('/float/stream', methods=['POST'])
    def push_stat_stream(self):
        print('receiving_pushing_to_stream')
        json = request.json
        self.get_namespace(json['namespace'])[json['key']] = json['value']

        try:
            val = float(json['value'])
            stream = self.get_stream(json['namespace'], json['key'], json['drop_obs'])
            stream += val

            return '', 204
        except Exception as e:
            print('push_stat_stream is expecting a float!')
            raise e

    @route('/program', methods=['POST'])
    def set_program(self):
        json = request.json
        return '', 204

    @route('/system', methods=['POST'])
    def set_system(self):
        json = request.json
        return '', 204

    @route('/log/out/:str')
    def log_out(self, str):
        return '', 204

    @route('/log/out/:str')
    def log_err(self, str):
        return '', 204


def start_local_server(port) -> Flask:
    app = Flask('BenchTrackerLocalServer')
    LocalServer.register(app)
    app.run(host='localhost', port=port)
    return app


def make_local_server(port=8123) -> Process:
    proc = Process(target=start_local_server, args=(port,))
    proc.start()
    return proc


if __name__ == '__main__':
    import sys
    flask = make_local_server()

    flask.terminate()
    sys.exit()
