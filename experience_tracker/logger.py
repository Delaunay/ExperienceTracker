import requests
import experience_tracker.sysinfo as sysinfo

#
#   Might be useful to make all the logging be async
#   have another python process sending the messages across
#   and just have the main thread push messages


class Namespace:
    def __init__(self, name):
        self.name = name

    def push(self, key, value):
        pass

    def push_stream(self, key, value):
        pass


class TrackLogger:
    """
        Implement a `print` so output is saved
    """
    pass

    def set_system(self):
        requests.post('localhost:8123/system', json=sysinfo.get_system_json())

    def set_program(self):
        requests.post('localhost:8123/program', json={})

    def namespace(self, name:str):
        return Namespace(name)

    def push(self, key, value, namespace='default'):
        Namespace(namespace).push(key, value)

    def push_stream(self, key, value, namespace='default'):
        Namespace(namespace).push_stream(key, value)

