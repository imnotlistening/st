#!/usr/bin/python

# Main st app! Yay.

import curses
import curses.textpad
import time
import threading
import time
import locale
import sys
from datetime import datetime

import stock
from portfolio import Portfolio

# Set to true to kill the background refresh thread.
st_refresh_thread_die = False
st_refresh_thread_interval = 15.0 # In seconds

locale.setlocale(locale.LC_ALL, '')

st_sort_key = stock.stock_key_name
st_reverse_sort = True # "reverse" sort is better IMO

def st_refresh_thread(args):
    """
    Runs in the background and refreshes the active portfolio into the
    main screen.

    Pass in the tracker to use.
    """

    global st_refresh_thread_die
    global st_refresh_thread_interval

    tracker = args

    accumulated_time = 0

    while not st_refresh_thread_die:

        # Sleep in tenth second increments to keep this thread decently
        # responsive. Add up the time between increments; when we get to
        # the refresh interval, reset the accumulated time and refresh the
        # portfolio.
        if accumulated_time < st_refresh_thread_interval:
            time.sleep(.1)
            accumulated_time += .1
            continue
        else:
            accumulated_time = 0

        p = tracker.active_portfolio
        p.refresh()

        tracker.lock.acquire()

        # Check if the portfolio we just updated is still the active portfolio.
        # If it's not that means somewhere else has assigned a new active
        # portfolio and we should not override that. Instead just go an try to
        # update the new active portfolio and try again.
        if p != tracker.active_portfolio:
            tracker.lock.release()
            continue

        tracker.display_portfolio(p)

        tracker.lock.release()

class ST(object):
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
        self.active_portfolio = None
        self.portfolios = list()
        self.refresh_thread = None
        self.terminate = False

        # Simple layout: 3 boxes, stacked on top of each other. The top will
        # show some general stuff, the middle will show what ever info is
        # requested by the user, and the bottom will show a simple terminal
        # interface.
        windows = dict()
        windows['HEADER'] = stdscr.subwin(3, curses.COLS, 0, 0)
        windows['MAIN']   = stdscr.subwin(curses.LINES - 4, curses.COLS,
                                          3, 0)
        windows['ACTION'] = stdscr.subwin(1, curses.COLS,
                                          curses.LINES - 1, 0)
        self.windows = windows

        # Locks for the windows.
        self.lock = threading.Lock()

        self.clear_header()
        self.clear_main()
        self.clear_action()

        self.refresh()

        # For displaying stocks going up/down.
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    def clear_main(self):
        """
        Return the main screen to the default blank state (with borders). Does
        not do a refresh. That must be done by the caller.
        """

        if self.terminate:
            return

        self.windows['MAIN'].erase()
        self.windows['MAIN'].border(' ', ' ',
                                    curses.ACS_HLINE, curses.ACS_HLINE,
                                    curses.ACS_HLINE, curses.ACS_HLINE,
                                    curses.ACS_HLINE, curses.ACS_HLINE)

    def clear_action(self):
        """
        Return the action box to it's default.
        """

        if self.terminate:
            return

        self.windows['ACTION'].erase()
        self.windows['ACTION'].addstr(0, 0, 'For help press \'h\'')

    def clear_header(self):
        """
        Return the header to the default header text.
        """

        if self.terminate:
            return

        self.windows['HEADER'].erase()
        # if not self.active_portfolio:
        self.windows['HEADER'].addstr(0, 0, 'Portfolio: None')

    def set_header(self, portfolio):
        """
        Set the header window based on the passed portfolio.
        """
        if self.terminate:
            return

        portfolio_fields = '%-15s %-5s %9s %14s | %-6s %11s %10s' % (
            'Company Name',
            'Symb',
            'Price ($)',
            'Change',
            'Shares',
            'Value',
            'Gain')

        w = self.windows['HEADER']

        # Delete the old...
        w.erase()

        # And in with the new.
        w.addstr(0, 0, 'Portfolio: %s' % portfolio.name)
        w.addstr(1, 0, 'Time:')
        w.addstr(1, 6, datetime.now().strftime('%A, %d. %B %Y %I:%M%p'))
        w.addstr(2, 0, portfolio_fields, curses.A_BOLD)

    def __display_portfolio(self, p, w):
        """
        Actually do the portfolio write.
        """

        global st_sort_key
        global st_reverse_sort

        line = 1
        total_assets = 0
        total_change = 0

        p.assets.sort(key=st_sort_key, reverse=st_reverse_sort)

        for s in p.assets:
            # Make sure we have space to write the portfolio totals.
            if line >= (curses.LINES - 3):
                break

            total_assets += (p.asset_counts[s.symb()] * s.price())
            total_change += (p.asset_counts[s.symb()] * s.change())

            # Color red/green for stocks going up/down.
            change_color = curses.color_pair(0)
            if s.change() > 0:
                change_color = curses.color_pair(1)
            elif s.change() < 0:
                change_color = curses.color_pair(2)

            direction = ''
            if s.change() > 0:
                direction = u'\u25b2'
            elif s.change() < 0:
                direction = u'\u25bc'

            w.addstr(line, 0,  '%-15s' % s.name()[0:14])
            w.addstr(line, 16, '%-5s' % s.symb(), curses.A_BOLD)
            w.addstr(line, 22, '%9.2f' % s.price())
            w.addstr(line, 32, direction.encode('utf-8'), change_color)
            w.addstr(line, 33, '%6.2f %5.2f%%' % (abs(s.change()),
                                                  abs(s.change_percent()) *
                                                  100),
                     change_color)
            w.addstr(line, 47, '|')
            w.addstr(line, 49, '%-6d' % p.asset_counts[s.symb()])
            w.addstr(line, 56, '%11.2f' % (p.asset_counts[s.symb()] *
                                           s.price()))
            w.addstr(line, 68, '%10.2f' % (p.asset_counts[s.symb()] *
                                           s.change()),
                     change_color)

            line += 1

        line += 1

        # Get overall change (of assets) for the portfolio.
        overall_change = total_assets - p.cost_basis()
        overall_color = curses.color_pair(0)
        if overall_change > 0:
            overall_color = curses.color_pair(1)
        elif overall_change < 0:
            overall_color = curses.color_pair(2)

        # Color red/green for assets changing.
        change_color = curses.color_pair(0)
        if total_change > 0:
            change_color = curses.color_pair(1)
        elif total_change < 0:
            change_color = curses.color_pair(2)

        # Print accumulated stats for the portfolio.
        w.addstr(line,     0,  'Daily:')
        w.addstr(line,     8, '$%.2f' % total_change,
                 curses.A_BOLD | change_color)
        w.addstr(line,     23, 'Total:')
        w.addstr(line,     30, '$%.2f' % overall_change,
                 curses.A_BOLD | overall_color)
        w.addstr(line + 1, 0,  'Assets:')
        w.addstr(line + 1, 8, '$%.2f' % total_assets)
        w.addstr(line + 1, 23, 'Cash:  $%.2f' % p.cash)
        w.addstr(line + 1, 44, 'Total value:')
        w.addstr(line + 1, 58, '$%.2f' % (p.cash + total_assets),
                 curses.A_BOLD)

    def display_portfolio(self, p):
        """
        Display the active portfolio on the main screen. You must have the
        window lock!
        """

        if self.terminate:
            return

        w = self.windows['MAIN']

        self.clear_main()
        self.__display_portfolio(p, w)
        self.clear_header()
        self.set_header(p)

        self.refresh()

    def track_portfolio(self, p):
        """
        This runs a thread that updates the main screen based on the passed
        portfolio. We can get portfolio information from the
        """

        global st_refresh_thread

        if self.terminate:
            return

        p.refresh()

        self.lock.acquire()
        self.active_portfolio = p
        self.display_portfolio(p)
        self.lock.release()

        if not self.refresh_thread:
            thr_args = list()
            thr_args.append(self)
            self.refresh_thread = threading.Thread(target=st_refresh_thread,
                                                   args=thr_args)
            self.refresh_thread.start()

    def load_portfolio(self):
        """
        Load a portfolio from a file.
        """

        if self.terminate:
            return

        # First get a file.
        self.lock.acquire()
        self.windows['ACTION'].erase()

        curses.curs_set(1)

        tp = curses.textpad.Textbox(self.windows['ACTION'])
        file_str = tp.edit()
        curses.curs_set(0)

        self.clear_action()
        self.lock.release()

        self.refresh()

        # Now that we have a portfolio file, let's load it up and
        # fire off a thread to update it.
        p = Portfolio(file_str.strip())
        self.portfolios.append(p)
        self.track_portfolio(p)

    def swap_active_portfolio(self):
        """
        Display a list of available portfolios and allow the user to pick
        one by number.
        """

        self.lock.acquire()

        self.clear_main()

        w = self.windows['MAIN']
        l = 1

        for p in self.portfolios:
            # Only support 9 portfolios since that makes this easier to deal
            # with.
            if l >= 10:
                break

            w.addstr(l, 0, '%2d' % l, curses.A_BOLD | curses.color_pair(1))
            w.addstr(l, 3, p.name)
            l += 1

        self.refresh()

        # Wait for the user to give is a key.
        while True:
            c = self.stdscr.getch()

            if c < ord('1') and c > ord('9'):
                continue

            index = c - ord('1')

            if index < len(self.portfolios):
                break

        self.portfolios[index].refresh()

        self.active_portfolio = self.portfolios[index]
        self.display_portfolio(self.active_portfolio)
        self.lock.release()

    def choose_sort_key(self):
        """
        Choose the sort key we want to sort the portfolio lines by. Currently
        accepts the following keys:

          Company name
          Symbol
          Price
          Change
          Change percent
        """

        global st_sort_key
        global st_reverse_sort

        sort_choices = [
            ('*Reverse*',      None),
            ('Company name',   stock.stock_key_name),
            ('Symbol',         stock.stock_key_symb),
            ('Price',          stock.stock_key_price),
            ('Change',         stock.stock_key_change),
            ('Change percent', stock.stock_key_change_percent)
        ]

        self.lock.acquire()
        self.clear_main()
        w = self.windows['MAIN']
        line = 1

        for choice, func in sort_choices:
            w.addstr(line, 0, '%2d' % line, curses.A_BOLD | curses.color_pair(1))
            w.addstr(line, 3, choice)
            line += 1

        self.refresh()

        # Wait for the user to give is a key.
        while True:
            c = self.stdscr.getch()

            if c < ord('1') and c > ord('9'):
                continue

            index = c - ord('1')

            if index < len(sort_choices):
                break

        self.lock.release()

        # Set the new sort function.
        if index == 0:
            st_reverse_sort = not st_reverse_sort
        else:
            _, st_sort_key = sort_choices[index]

        self.lock.acquire()
        self.display_portfolio(self.active_portfolio)
        self.lock.release()

    def force_refresh(self):
        """
        """

        if not self.active_portfolio:
            return

        self.active_portfolio.refresh()

        self.lock.acquire()
        self.display_portfolio(self.active_portfolio)
        self.lock.release()


    def display_help(self):
        """
        Display a help message to the main screen.
        """

        msg = """Stock Tracker help

Action                        Key stroke
------                        ----------
Help                          h
Quit                          q
Force refresh                 r
Load portfolio                l
Toggle active portfolio       t
Set refresh interval          d
Choose sort key               k

Quit this dialog with 'q' or 'h'
"""

        if self.terminate:
            return

        self.lock.acquire()
        self.clear_main()
        self.windows['MAIN'].addstr(1, 0, msg)
        self.refresh()

        # Hold the lock until the user quits this dialog.
        while True:
            c = self.stdscr.getch()
            if c == ord('q') or c == ord('h'):
                break

        # Now, go back to the active portfolio (or nothing).
        if not self.refresh_thread or not self.active_portfolio:
            self.clear_main()
        else:
            self.display_portfolio(self.active_portfolio)

        self.lock.release()

        self.refresh()

    def run(self, starting_portfolios=list()):
        """
        Main execution thread - listens for input from the user and handles
        user commands.
        """

        global st_refresh_thread_die

        self.portfolios = starting_portfolios

        if len(self.portfolios) > 0:
            self.track_portfolio(self.portfolios[0])

        # Loop forever - user will terminate.
        while True:

            c = self.stdscr.getch()

            if c == ord('h'):
                # Print help screen to the main window.
                self.display_help()
            elif c == ord('q'):
                # Quit. Get the window lock so that we can be sure that the
                # update portfolio function isn't currently running.
                self.lock.acquire()
                self.terminate = True
                st_refresh_thread_die = True
                self.lock.release()
                break
            elif c == ord('l'):
                # Load a portfolio
                self.load_portfolio()
            elif c == ord('s'):
                # Switch to a different portfolio.
                self.swap_active_portfolio()
            elif c == ord('r'):
                # Force refresh
                self.force_refresh()
            elif c == ord('k'):
                self.choose_sort_key()


    def refresh(self):
        """
        Refresh the STs screen.
        """

        for w in self.windows.values():
            w.refresh()

def main(stdscr, starting_portfolios):
    """
    Our main routine! Set everything up and away we go!
    """

    # Generally don't need a cursor.
    curses.curs_set(0)

    # Clear the screen
    stdscr.clear()

    # Fire up the Stock Tracker.
    st = ST(stdscr);
    st.run(starting_portfolios)

##
## Treat arguments as portfolios to load.
##
starting_portfolios = list()

for i in range(1, len(sys.argv)):
    starting_portfolios.append(Portfolio(sys.argv[i]))

# Actually start the app!
#
# Handles annoying crashes, etc.
curses.wrapper(main, starting_portfolios)
