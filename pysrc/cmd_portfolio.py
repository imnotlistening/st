#
# Built in portfolio command.
#

import sys
import argparse

from StringIO import StringIO

from stcommand import STCommand
from stcommand import STLine
from stcommand import st_add_command
from stcommand import st_add_alias

from stock.portfolio import Portfolio


portfolio_header = '%-15s %-5s %9s %10s | %-6s %11s %10s'
portfolio_fields = '%-15s %-5s %9.2f %10s | %-6d %11.2f %10.2f'

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
        parser.add_argument('--details', '-d',
                            action='store_true',
                            help='Print more details about each stock.')
        parser.add_argument('--reverse-sort', '-R',
                            action='store_true',
                            help='Reverse the sort done on the stocks.')
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

        try:
            p = Portfolio(args.portfolio[0])
        except Exception as e:
            self.println('> %s' % e)
            return STCommand.FAILURE

        for l in unicode(p).split('\n'):
            self.println(l)

        self.portfolio = p
        self.runs = 0
        self.refresh = args.refresh

        return STCommand.SUCCESS

    def update(self, cmdlist):
        """
        Assumes the update_init() was successfull which means the arg parsing
        was successful.
        """

        # Well, we need one of these, for sure.
        if not self.portfolio:
            return STCommand.FAILURE

        self.println('Portfolio: %s' % self.args.portfolio[0]);

        lot_list = self.portfolio.lots
        lot_dict = { }

        if self.runs > 0:
            self.portfolio.refresh()
        self.runs += 1

        # Build a dictionary of the lots - map stock to list of relevant lots.
        for l in lot_list:
            if l.stock.symb() not in lot_dict:
                lot_dict[l.stock.symb()] = list()
            lot_dict[l.stock.symb()].append(l)

        # Now start printing stuff.
        self.println(portfolio_header % (
            'Company Name',
            'Symb',
            'Price ($)',
            'Change',
            'Shares',
            'Value',
            'Gain'))

        self.println(portfolio_header % (
            '------------',
            '----',
            '---------',
            '------',
            '------',
            '-----',
            '----'))

        for symb in sorted(lot_dict.keys()):
            shares = 0
            for l in lot_dict[symb]:
                shares += l.nr

            l = lot_dict[symb][0] # Access to a lot for general info.
            c = None
            if l.stock.change() > 0:
                c = STLine.GREEN
            elif l.stock.change() < 0:
                c = STLine.RED

            direction = ''
            if l.stock.change() > 0:
                direction = u'\u25b2'
            elif l.stock.change() < 0:
                direction = u'\u25bc'

            self.println(portfolio_fields % (
                l.stock.name()[0:14],
                l.stock.symb(),
                l.stock.price(),
                '%-1s %.02f' % (direction, l.stock.change()),
                shares,
                shares * l.stock.price(),
                shares * l.stock.change()), color=c)

            if not self.args.details:
                continue

            for l in lot_dict[symb]:
                change = l.stock.price() - l.acquire_price
                change_pc = (change / l.acquire_price) * 100

                self.println('  %s: %5d @ %7.02f  $%9.02f [%7.02f%%]' % (
                    l.date.strftime('%b %d, %Y'),
                    l.nr, l.acquire_price,
                    change, change_pc))

            self.println('')

        self.println('** Runs: %d' % self.runs);

        return STCommand.SUCCESS

st_add_command(STCommandPortfolio())
st_add_alias('port', 'portfolio')
st_add_alias('p', 'portfolio')
