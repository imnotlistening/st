#!/usr/bin/python

# Main st app! Yay.

import sys
import time
import locale
import curses
import argparse

from curses.textpad import Textbox

from stcommand import STCommand
from stcommand import st_get_command
from stcommand import st_get_commands

locale.setlocale(locale.LC_ALL, '')

class ST(object):
    """
    The main ST app. This handles the little command line and kicking off
    commands to the command objects.
    """

    class STCommandUnknown(STCommand):
        def __init__(self):
                    super(ST.STCommandUnknown, self).__init__('unknown',
                                                              'Unknown command',
                                                              None, 0)
        def update(self, cmdlist):
            self.println('Unknown command:')
            self.println('')
            self.println('  \'%s\'' % ' '.join(cmdlist))

            return STCommand.SUCCESS

    def __init__(self, stdscr, args):
        """
        There are two primary windows in ST: the main window, which is managed
        by commands, and the command window, which is managed by us. We can
        either be in command context or in active context when a command is
        running.
        """

        self.log_file = open('log.txt', 'w')

        self.args = args

        # Has it's uses.
        self.stdscr = stdscr

        # Colors for up vs down stocks. Hmm, may not need this.
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED,   curses.COLOR_BLACK)

        # Windows - CMD starts 3 chars in so we can draw a simple prompt.
        # Ugh. The textbox should really support this some how!
        self.MAIN = curses.newwin(curses.LINES - 1, curses.COLS - 1, 0, 0)
        self.CMD  = curses.newwin(1,                curses.COLS - 1,
                                  curses.LINES - 1, 2)

        # Make sure we get instant key presses.
        self.stdscr.nodelay(True)

        # Init the display.
        self.clear_main()
        self.stdscr.addstr(curses.LINES - 1, 0, '>')

        # Error handling 'command'
        self.error_handler = ST.STCommandUnknown()

        self.__load_builtins()
        self.__refresh()

    def log(self, msg):
        self.log_file.write(msg + '\n')
        self.log_file.flush()

    def __load_builtins(self):
        """
        Load builtin commands such as 'help'.
        """

        import builtin_cmds
        import cmd_portfolio

        self.log('Loaded builtin commands:')
        for c in st_get_commands():
            self.log('  %s' % c)

    def __refresh(self):
        """
        Refresh everything.
        """

        self.stdscr.refresh()
        self.MAIN.refresh()
        self.CMD.refresh()

    def clear_main(self):
        """
        Clear MAIN but make sure the border is still present.
        """

        self.MAIN.erase()
        self.MAIN.border(' ', ' ', ' ',              curses.ACS_HLINE,
                         ' ', ' ', curses.ACS_HLINE, curses.ACS_HLINE)

    def draw_main(self, line_list):
        """
        Redraw the main window.
        """

        self.clear_main()

        y, x = self.MAIN.getmaxyx()
        cur_y = 0


        for l in line_list:

            # Don't write too much!
            if (cur_y - 1) >= y:
                break;

            color = curses.color_pair(0)
            if l.color == 'g':
                color = curses.color_pair(1)
            elif color == 'r':
                color = curses.color_pair(2)

            self.MAIN.addnstr(cur_y, 0, l.line.encode('utf-8'), x, color)
            cur_y += 1

        self.MAIN.refresh()

    def handle_user_input(self):
        """
        Handle user input: mostly we care about 'q': this means quit the current
        command. There could be other uses in the future too, though.

        Returns Ture if a 'q' was detected; False otherwise.
        """

        c = self.stdscr.getch()

        if c == ord('q'):
            return True

        return False

    def handle_unknown(self, cmdlist):
        """
        Handle an unknown command.
        """

        status, lines = self.error_handler.st_update(cmdlist)
        self.draw_main(lines)

    def run(self):
        """
        Run the ST app.
        """

        # If there's a portfolio argument, then load it up as a first command.
        if self.args.portfolio:
            self.exec_cmd('portfolio %s' % ' '.join(self.args.portfolio))

        # User will terminate.
        while True:

            # Clear any previous commands.
            self.CMD.erase()
            self.CMD.refresh()

            # Make a textbox and use it to get a command.
            cmdbox = Textbox(self.CMD)
            cmdstr = cmdbox.edit()

            # Execute the command.... Coming soon.
            self.exec_cmd(cmdstr.strip())

    def exec_cmd(self, cmd):
        """
        Attempt to execute the passed command.
        """

        if not cmd:
            return

        cmdlist = cmd.split()
        self.log('Executing command: \'%s\'' % cmd)

        cmd = st_get_command(cmdlist[0])

        if not cmd:
            self.log('Unknown command \'%s\'' % cmdlist[0])
            self.handle_unknown(cmdlist)
            return

        # Handle a known command. First call .do_update_init() and then the
        # first .do_update().
        success, lines = cmd.st_update_init(cmdlist)
        self.draw_main(lines)
        if not success:
            return

        success, lines = cmd.st_update(cmdlist)
        self.draw_main(lines)
        if not success:
            return

        sleep_duration = cmd.refresh

        # If the command doesn't want to execute the update() call over and
        # over just return and get ready for the next command.
        if sleep_duration <= 0:
            self.log('Done command \'%s\'' % cmdlist[0])
            return

        # Periodically rerun the .do_update() method on the command.
        while True:

            current_sleep = 0
            while current_sleep < sleep_duration:

                # Sleep for 35ms intervals. Fast enough to be responsive to user
                # input but not going to bog down the system either.
                current_sleep += .035
                time.sleep(.035)

                # Handle user keyboard input. Lets the user quit the command.
                if self.handle_user_input():
                    return

            if cmd.refresh > 0:
                success, lines = cmd.st_update(cmdlist)
                self.draw_main(lines)
                if not success:
                    return

def parse_args():
    parser = argparse.ArgumentParser(description='Stock Tracking CLI App')

    # Currently we don't take many arguments!
    parser.add_argument('portfolio', nargs='*',
                        help='Path to portfolio to display and args')

    return parser.parse_args()

def main(stdscr):
    """
    This expects to have been called via the curses wrapper.
    """

    global args

    st = ST(stdscr, args)
    st.run()

args = parse_args()

curses.wrapper(main)
