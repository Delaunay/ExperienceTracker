from tinydb import TinyDB, where
import hashlib
from typing import List, Dict, Set
import experience_tracker.sysinfo as sysinfo
import datetime

TINY_DB = './benchmark.db'

class Program:
    def __init__(self, name: str, arguments: List[str], version: str =''):
        self.name: str = name
        self.arguments: List[str] = arguments
        self.version: str = version
        self.date: str = str(datetime.datetime.now())
        self.uid: str = self.compute_uid()

        # List of system for which the Program has ran
        # This is useful for aggregation
        self.systems: Set[str] = {}

    def compute_uid(self) -> str:
        h = hashlib.sha256()
        h.update(self.name.encode('utf-8'))
        h.update(self.version.encode('utf-8'))
        for arg in self.arguments:
            h.update(arg.encode('utf-8'))
        return h.hexdigest()

    def add_system(self, system_uid):
        self.systems = list(set(self.systems + system_uid))

    @staticmethod
    def get_program(table, name: str, arguments: List[str], version: str ='') -> 'Program':
        self = Program(name, arguments, version)
        results = table.get_program(by='uid', value=self.uid)

        if len(results) != 0:
            self.systems = set(results[0]['systems'])

        return self

    def _insert(self, table):
        results = table.search(where('uid') == self.uid)

        if len(results) == 0:
            table.insert({
                'name': self.name,
                'arguments': self.arguments,
                'version': self.version,
                'date': self.date,
                'systems': list(self.systems),
                'uid': self.uid
            })
        else:
            result = results[0]
            result['systems'] = result['systems'] + self.systems
            table.update(result, doc_ids=[result.doc_id])


class System:
    def __init__(self, cpu, gpus, memory, hostname):
        self.cpu: (str, str, str) = cpu
        self.gpus: List[(int, str)] = gpus
        self.memory: (str, str) = memory
        self.hostname: str = hostname

        #  ID: try to group system with similar hardware
        self.id: str = self.compute_id(uid=False)
        # UID: Unique
        self.uid: str = self.compute_id(uid=True)

    def compute_id(self, uid: bool = False) -> str:
        h = hashlib.sha256()
        for c in self.cpu:
            h.update(c.encode('utf-8'))

        for g in self.gpus:
            h.update(g[0])
            h.update(g[1].encode('utf-8'))

        h.update(self.memory[1])
        if uid:
            h.update(self.hostname.encode('utf-8'))
        return h.hexdigest()

    @staticmethod
    def get_system() -> 'System':
        self = System(
            sysinfo.get_cpu_info(),
            sysinfo.get_gpu_info(),
            sysinfo.get_memory_info(),
            sysinfo.get_hostname()
        )
        return self

    def _insert(self, table):
        results = table.search(where('uid') == self.uid)
        if len(results) == 0:
            table.insert({
                'cpu': self.cpu,
                'gpus': self.gpus,
                'memory': self.memory,
                'hostname': self.hostname,
                'uid': self.uid,
                'id': self.id
            })


class Observation:
    def __init__(self, program_uid: str, system_uid: str, date: str, reports: Dict, out: List[str], err: List[str]):
        self.program_uid: str = program_uid
        self.system_uid: str = system_uid
        self.date:str = date
        self.reports: Dict = reports
        self.stdout: List[str] = out
        self.stderr: List[str] = err

    def _insert(self, table):
        table.insert({
            'program_uid': self.program_uid,
            'system_uid': self.system_uid,
            'date': self.date,
            'reports': self.reports,
            'stdout': self.stdout,
            'stderr': self.stderr
        })


"""
    Keeps Track of experiences:
        - program    : definition of an experiment (usually script name + arguments)
        - observation: results of the jobs ran
        - system     : system description on which the job was ran
"""
class ExperienceDatabase:
    def __init__(self):
        self.db = TinyDB(TINY_DB)
        self._programs = self.db.table('programs')
        self._observations = self.db.table('observations')
        self._systems = self.db.table('systems')

    def insert_program(self, program):
        return program._insert(self._programs)

    def insert_observation(self, observation):
        return observation._insert(self._observations)

    def insert_system(self, system):
        return system._insert(self._systems)

    def programs(self):
        return self._programs.all()

    def systems(self):
        return self._systems.all()

    def get_program(self, by: str, value: str):
        return self._programs.search(where(by) == value)

    def get_system(self, by: str, value: str):
        return self._systems.search(where(by) == value)

    def get_observation(self, by: str, value: str):
        return self._observations.search(where(by) == value)

