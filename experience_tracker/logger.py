import requests
import sys
import datetime

from typing import *
from experience_tracker.database import System
from experience_tracker.database import Program
from experience_tracker.database import Observation
from experience_tracker.database import ExperienceDatabase
from experience_tracker.stats import StatStream

#
#   Might be useful to make all the logging be async
#   have another python process sending the messages across
#   and just have the main thread push messages


class RemoteNamespace:
    def __init__(self, name):
        self.name = name

    def push(self, key, value):
        print('pushing_key_value')
        requests.post('http://localhost:8123/push', json={
            'namespace': self.name,
            'key': key,
            'value': value
        })

    def push_stream(self, key, value, drop_obs=0):
        print('pushing_to_stream')
        requests.post('http://localhost:8123/float/stream', json={
            'namespace': self.name,
            'key': key,
            'value': value,
            'drop_obs': drop_obs
        })


class RemoteTrackLogger:
    """
        Implement a `print` so output is saved
    """

    def set_system(self):
        requests.post('http://localhost:8123/system', json=System.get_system().as_json())

    def set_program(self, name: str, args: List[str], version: str):
        requests.post('http://localhost:8123/program', json=Program(name, args, version).as_json())

    def namespace(self, name: str):
        return RemoteNamespace(name)

    def push(self, key, value, namespace='default'):
        RemoteNamespace(namespace).push(key, value)

    def push_stream(self, key, value, namespace='default'):
        RemoteNamespace(namespace).push_stream(key, value)


class LocalNamespace:
    def __init__(self, name, reports):
        self.reports = {}
        reports[name] = self.reports

    def push(self, key, value):
        self.reports[key] = value

    def push_stream(self, key, value, drop_obs=0):
        if key not in self.reports:
            self.reports[key] = StatStream(drop_obs)

        self.reports[key] += value


class LocalTrackLogger:
    system = System.get_system()
    program = Program(sys.argv[0], sys.argv[1:])
    observation = Observation(
        program.uid,
        system.uid,
        str(datetime.datetime.now()),
        {},
        [],
        []
    )

    def set_system(self):
        pass

    def set_program(self, name: str, args: List[str], version: str):
        pass

    def namespace(self, name: str):
        return LocalNamespace(name, self.observation.reports)

    def push(self, key, value, namespace='default'):
        self.namespace(namespace).push(key, value)

    def push_stream(self, key, value, namespace='default'):
        self.namespace(namespace).push_stream(key, value)

    def dump(self):
        self.observation.dump()

    def persist(self):
        db = ExperienceDatabase()
        self.program.add_system(self.system.uid)
        db.insert_program(self.program)
        db.insert_system(self.system)
        db.insert_observation(self.observation)


def make_tracker(mode='local', *args, **kwargs):
    if mode == 'local':
        return LocalTrackLogger()
    return RemoteTrackLogger()
