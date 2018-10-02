import os
import sys
import subprocess
import tempfile
import glob

import experience_tracker.database as database
import datetime
import argparse
import hashlib


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
    parser.add_argument('program')

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

    tmp_dir = make_nvprof_folder(folder='/tmp/tmpykkm1zsatracker_17282_/')
    report_file_name_format = tmp_dir + '/report_%p.nvprof'

    print('Reports will be generated in {}'.format(tmp_dir))
    #
    #   Launch Job
    #
    try:
        cmd = make_command_line(program_name, arguments, True, report_file_name_format)
        #out = subprocess.check_output(cmd, stderr=subprocess.STDOUT )

        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        nvprof_reports = glob.glob(tmp_dir + '/*', recursive=True)
        reports = {}

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

    except subprocess.CalledProcessError as e:
        print('Unable to call program')
        print(e)
        pass


if __name__ == '__main__':
    main()