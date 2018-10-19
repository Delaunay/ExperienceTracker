from typing import *
from experience_tracker.database import ExperienceDatabase


database = ExperienceDatabase()


class NotFound(Exception):
    def __init__(self, message):
        self.message = message


def str_program(prog):
    return """
        * id       : {}
        * UID      : {}
        * Program  : {}
        * Arguments: {}
        * Systems  : {}
        * Date     : {}
        * version  : {}
    """.format(
        prog['id'], prog['uid'], prog['name'], prog['arguments'], prog['systems'], prog['date'], prog['version']
    )


def str_system(sys):
    return """
        * id      : {}
        * UID     : {}
        * cpu     : {}
        * gpu     : {}
        * hostname: {}
        * memmory : {}
    """.format(
        sys['id'], sys['uid'], sys['cpu'], sys['gpus'], sys['hostname'], sys['memory']
    )


def str_obs(obs):
    return """
        * id         : {}
        * program_uid: {}
        * system_uid : {}
        * date       : {}
    """.format(
        obs['id'],
        obs['program_uid'],
        obs['system_uid'],
        obs['date']
    )


def list_programs():
    """ list all the programs stored in the database """
    for program in database.programs():
        print(str_program(program), end='')
    print()


def list_systems():
    """ list all the systems stored in the database """
    for system in database.systems():
        print(str_system(system), end='')
    print()


def list_obs():
    """ list all the observations stored in the database """
    for obs in database.observations():
        print(str_obs(obs), end='')
    print()


def show_obs(id):
    """ display a detailed report of the observation of an experiement """
    results = database.get_observation(by='id', value=int(id))

    if len(results) == 0:
        raise NotFound('Not found document with id={}'.format(id))

    doc = results[0]

    system = database.get_system(by='uid', value=doc['system_uid'])[0]
    program = database.get_program(by='uid', value=doc['program_uid'])[0]

    print('>' * 20)
    print('    * System')
    print(str_system(system))
    print('    * Program')
    print(str_program(program))

    print('    * STDOUT')
    print('-' * 20)
    for line in doc['stdout']:
        print(line)
    print('-' * 20)

    print('    * STDERR')
    print('-' * 20)
    for line in doc['stderr']:
        print(line)
    print('-' * 20)

    for report_name, report in doc['reports'].items():
        print(report_name)
        print('=' * len(report_name))

    print('<' * 20)


def exit():
    """ exit the repl"""
    pass


def show_help():
    """ show a list of the commands available """
    for cmd, fun in defined_commands.items():
        print("{:>20}: {}".format(cmd, fun.__doc__))


defined_commands = {
    'list-programs': list_programs,
    'list-systems': list_systems,
    'list-observations': list_obs,
    'show-observation': show_obs,
    'exit': exit,
    'help': show_help,
}


def parse_command(cmd: str) -> Tuple[str, Dict[str, str]]:
    cmd = cmd.split(' ')
    arg_dict = {}

    def parse_args(arg):
        args = arg.split('=')

        if len(args) != 2:
            raise TypeError('Not a valid argument expect `arg_name`=`arg_value` not {}'.format(arg))

        arg_dict[args[0]] = args[1]

    for arg in cmd[1:]:
        parse_args(arg)

    return cmd[0], arg_dict


def execute_cmd(name: str, args: Dict[str, str]):
    defined_commands[name](**args)


def main():
    i = 0

    while True:
        try:
            i += 1
            cmd = input('[{:3d}] > '.format(i))

            cmd, args = parse_command(cmd)

            if cmd in {'stop', 'exit', 'quit'}:
                return

            if len(cmd) == 0:
                i -= 1
                continue

            if cmd not in defined_commands:
                print('    [E] Command `{}` not defined'.format(cmd))
                continue

            execute_cmd(cmd, args)
        except Exception as e:
            print('    [E] {}'.format(e))


if __name__ == '__main__':
    main()
