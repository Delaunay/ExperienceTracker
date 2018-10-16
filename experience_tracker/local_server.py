from flask_classful import FlaskView, route
from flask import Flask
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

    @route('/push/:namespace/:key/:value')
    def push(self, namespace, key, value):
        self.get_namespace(namespace)[key] = value

    @route('/float/stream/:namespace/:key/:value')
    def push_stat_stream(self, namespace, key, value, drop_nfirst_obs=0):
        try:
            val = float(value)
            stream = self.get_stream(namespace, key, drop_nfirst_obs)
            stream += val
        except Exception as e:
            print('push_stat_stream is expecting a float!')
            raise e

    @route('/task/name/:name/:version/:description')
    def set_task(self, name, version, description):
        pass

    @route('/system/:hostname/:ram/:gpu/:cpu')
    def set_system(self):
        pass

    @route('/log/out/:str')
    def log_out(self, str):
        pass


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
