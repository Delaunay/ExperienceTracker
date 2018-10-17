from typing import *
from experience_tracker.database import ExperienceDatabase


database = ExperienceDatabase()


def list_programs(test=False):
    print('Listing Programs')
    print(test)

    for program in database.programs():
        print(program)


def list_systems():
    print('Listing Systems')
    pass


def list_obs():
    print('Listing Observation')
    pass


defined_commands = {
    'list-programs': list_programs,
    'list-systems': list_systems,
    'list-observations': list_obs
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
        except TypeError as e:
            print('    [E] {}'.format(e))


if __name__ == '__main__':
    main()
