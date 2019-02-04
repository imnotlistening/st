#
# Built in portfolio command.
#

import sys
import argparse

from StringIO import StringIO

from stcommand import STCommand
from stcommand import st_add_command
from stcommand import st_add_alias

# Let's us handle errors instead of argparse printing a useless help message
# and killing our app.
class ArgumentParserError(Exception):
    pass
class ArgumentParserExit(Exception):
    pass

class ExceptionArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
    def exit(self, status=0, message=None):
        raise ArgumentParserExit(message)

class STCommandPortfolio(STCommand):
    """
    Load an display a stock portfolio. Usage:

     port <portfolio-path>

    This will continuously display a portfolio. Default update is every 15
    seconds.
    """

    def __init__(self):
        super(STCommandPortfolio, self).__init__('portfolio',
                                                 'Load and display a portfolio',
                                                 None, 15)

        # Make an arg parser for ourselves!
        parser = ExceptionArgumentParser(description='Load a portfolio',
                                         prog='portfolio')

        parser.add_argument('--refresh', '-r', type=int,
                            action='store', default=15,
                            help='Refresh interval for querying stock prices')
        parser.add_argument('portfolio', nargs=1,
                            help='Path to portfolio to display')

        self.parser = parser

    def parse_args(self, cmdlist):
        """
        The argparser object will write to stdout and stderr; this isn't good if
        we are a curses app. Thus we modify the sys.stderr and sys.stdout
        variables to point to StringIO buffers during the argparse operation.
        """

        args = None

        o_stdout = sys.stdout
        o_stderr = sys.stderr
        output = StringIO()
        sys.stdout = sys.stderr = output

        self.println('Executing portfolio command:')
        self.println('  > %s' % ' '.join(cmdlist))

        try:
            args = self.parser.parse_args(cmdlist[1:])
        except ArgumentParserError as e:
            self.println('Failed to load portfolio:\n')
            self.println('  > %s' % e)
            self.println('')
            self.parser.print_help()
        except ArgumentParserExit as e:
            pass
        finally:
            sys.stdout = o_stdout
            sys.stderr = o_stderr

        output_str = output.getvalue()
        if output_str:
            for l in output.getvalue().split('\n'):
                self.println(l)

        return args

    def update_init(self, cmdlist):

        self.args = None

        args = self.parse_args(cmdlist)
        if not args:
            return STCommand.FAILURE

        self.args = args
        self.println('Loading portfolio: \'%s\'' % args.portfolio[0])

        return STCommand.FAILURE

    def update(self, cmdlist):
        """
        Assumes the update_init() was successfull which means the arg parsing
        was successful.
        """

        portfolio_path = self.args.portfolio[0]

        return STCommand.SUCCESS

st_add_command(STCommandPortfolio())
st_add_alias('port', 'portfolio')
