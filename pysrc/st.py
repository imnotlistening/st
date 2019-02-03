#!/usr/bin/python

# Main st app! Yay.

import sys
import time
import locale
import curses

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

    def __init__(self, stdscr):
        """
        There are two primary windows in ST: the main window, which is managed
        by commands, and the command window, which is managed by us. We can
        either be in command context or in active context when a command is
        running.
        """

        self.log_file = open('log.txt', 'w')

        # Has it's uses.
        self.stdscr = stdscr

        # Colors for up vs down stocks. Hmm, may not need this.
        # curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # curses.init_pair(2, curses.COLOR_RED,   curses.COLOR_BLACK)

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

    def draw_main(self, str_list):
        """
        Redraw the main window.
        """

        self.clear_main()

        y, x = self.MAIN.getmaxyx()
        cur_y = 0


        for s in str_list:

            # Don't write too much!
            if cur_y >= y:
                break;

            self.MAIN.addnstr(cur_y, 0, s, x)
            cur_y += 1

        self.MAIN.refresh()

    def handle_user_input():
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

        self.draw_main(self.error_handler.do_update(cmdlist))

    def run(self):
        """
        Run the ST app.
        """

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

        cmdlist = cmd.split()
        self.log('Executing command: \'%s\'' % cmd)

        cmd = st_get_command(cmdlist[0])

        if not cmd:
            self.log('Unknown command \'%s\'' % cmdlist[0])
            self.handle_unknown(cmdlist)
            return

        # Handle a known command. First call .update_init() and then the
        # first .do_update().
        cmd.update_init(cmdlist)

        self.draw_main(cmd.do_update(cmdlist))

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
                self.draw_main(cmd.do_update(cmdlist))

def main(stdscr):
    """
    This expects to have been called via the curses wrapper.
    """

    st = ST(stdscr)
    st.run()

curses.wrapper(main)
