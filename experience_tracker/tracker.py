import os
import sys
import subprocess
import tempfile
import glob

import datetime
import argparse
import hashlib

import experience_tracker.database as database
from experience_tracker.local_server import make_local_server


def make_nvprof_folder(dry_run=False, folder=None):
    # NVPROF can create multiple reports for a single program (one per process)
    # we create a temporary folder for that reason
    if dry_run:
        return folder

    pid = os.getpid()
    return tempfile.mkdtemp('_tracker_' + str(pid))


def make_job_uid(name, args, version=None):
    hash = hashlib.sha256()
    hash.update(name.encode('utf-8'))
    for arg in args:
        hash.update(arg.encode('utf-8'))
    return hash.hexdigest()


def make_command_line(program, arguments, nvprof=False, report_name=None):
    if nvprof and report_name:
        return ['nvprof',
                '--normalized-time-unit', 'ms',
                '--log-file', report_name,
                '--csv', '--profile-child-processes', 'time', program] + arguments
    else:
        return ['time', program] + arguments


def main():
    parser = argparse.ArgumentParser(description='Save the experiment result in a local db to keep track of the results')
    parser.add_argument('--nvprof', action='store_true', default=False, help='Wrap the run script inside a nvprof call')
    parser.add_argument('program')

    local = make_local_server(8123)

    #
    #   Parse arguments
    #

    args, unknown = parser.parse_known_args()

    #
    #   Configure environment
    #
    date = str(datetime.datetime.now())
    program_name = args.program
    arguments = unknown

    db = database.ExperienceDatabase()
    system = database.System.get_system()
    program = database.Program(program_name, arguments)

    tmp_dir = '/tmp/'
    report_file_name_format = None

    if args.nvprof:
        tmp_dir = make_nvprof_folder(folder='/tmp/tmpykkm1zsatracker_17282_/')
        print('Reports will be generated in {}'.format(tmp_dir))
        report_file_name_format = tmp_dir + '/report_%p.nvprof'

    #
    #   Launch Job
    #
    try:
        cmd = make_command_line(program_name, arguments, report_name=report_file_name_format, nvprof=args.nvprof)

        sub_env = os.environ.copy()
        sub_env['PYTHONUNBUFFERED'] = 'True'

        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sub_env)
        out = []
        # Still print the stdout to user so they can follow the process' progress
        for line in pipe.stdout:
            line_utf8 = line.decode('utf-8')
            print(line_utf8, end='')
            out.append(line_utf8)

        pipe.wait()

        if pipe.returncode != 0:
            print('Was not able to execute PIPE successfully')
            for line in pipe.stderr:
                line_utf8 = line.decode('utf-8')
                print(line_utf8, end='')

            sys.exit(pipe.returncode)

        err = [str(l.decode('utf-8')) for l in list(pipe.stderr.readlines())]

        #
        #   Extract nvprof report
        #
        reports = {}
        if args.nvprof:
            nvprof_reports = glob.glob(tmp_dir + '/*', recursive=True)
            for report in nvprof_reports:
                data = open(report, 'r', encoding='utf-8')
                lines = data.readlines()
                data = {
                    # NVPROF adds 3 lines add the beginning of the file starting with ==
                    'nvprof':{
                        'nvprof_header': lines[:3],
                        'csv': lines[3:]
                    }
                }
                reports[report] = data

        # Run finished successfully
        # Push data to DB
        program.add_system(system.uid)
        db.insert_program(program)
        db.insert_system(system)
        observation = database.Observation(
            program.uid,
            system.uid,
            date,
            reports,
            out,
            err
        )
        db.insert_observation(observation)
        local.terminate()
        sys.exit()

    except subprocess.CalledProcessError as e:
        print('Unable to call program')
        print(e)
        sys.exit(-1)


if __name__ == '__main__':
    main()
