#!/usr/bin/python

# Main st app! Yay.

import curses
import time

class ST:
    """
    ST: stock tracker! This encapsulates our little stock tracking app!
    """

    def __init__(self, stdscr):
        """
        Init the list of windows we want for ST. This includes the following:
    
          GLOBAL_INFO - Display's global info about stocks
          MAIN        - Main window that displays stock info
          TERM        - A little terminal for accepting commands
        
        These windows are stored in the windows dictionary.
        """

        # Store this away for later!
        self.stdscr = stdscr

        # Simple layout: 3 boxes, stacked on top of each other. The top will
        # show some general stuff, the middle will show what ever info is
        # requested by the user, and the bottom will show a simple terminal
        # interface.
        windows = dict()
        windows['GLOBAL_INFO'] = stdscr.subwin(4, curses.COLS, 0, 0)
        windows['MAIN']        = stdscr.subwin(curses.LINES - 13, curses.COLS,
                                               5, 0)
        windows['TERM']        = stdscr.subwin(9, curses.COLS,
                                               curses.LINES - 9, 0)
        self.windows = windows
        
        windows['MAIN'].border(' ', ' ')

    def refresh(self):
        """
        Refresh the STs screen.
        """

        for w in self.windows.values():
            w.refresh()


def main(stdscr):
    """
    Our main routine! Set everything up and away we go!
    """

    # Clear the screen
    stdscr.clear()

    st = ST(stdscr);

    st.refresh()
    
    stdscr.getch()

# Actually start the app!
#
# Handles annoying crashes, etc.
curses.wrapper(main)
