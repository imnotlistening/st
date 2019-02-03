#
# A command class for the stock tracker. This class encapsulates the necessary
# threading to handle a command continually running and updating the main info
# screen area.
#
# Commands are pretty complicated objects in the ST. Sorry.
#

import curses

__st_commands = { }
__st_aliases  = { }

class STCommand(object):
    def __init__(self, name, help_msg, help_details=None, refresh=15):
        """
        Initialize a command object that can execute commands.

        @name         - The name of the command to match.
        @help_msg     - Brief help message.
        @help_details - More in depth help message.
        @refresh      - How often the command should refresh it's output. If
                        @refresh is 0 or less then the command will only have
                        it's update method called once.
        """

        self.name         = name
        self.help_msg     = help_msg
        self.help_details = help_details
        self.refresh      = refresh

    def update(self, cmd):
        """
        This should be overridden by subclasses.

        Takes a list containing the command and any arguments to the command.

        Return a list of strings that should be copied to the terminal line by
        line. This will be called indefinitely during the
        """
        return None

    def update_init(self, cmd):
        """
        May be overriden by a subclass if some special behavior prior to the
        first update is desired.
        """
        pass

    def __str__(self):
        return '%-10s %s' % (self.name, self.help_msg)

    def get_help(self):
        return '%s\n\n%s' % (self, self.help_details)

    def __execute(self, window, cmd):
        """
        Subclasses should not override this. This executes the command and
        handles the necessary multithreading, etc, to make the window work as
        expected.
        """

        # Hmm. How to do this?
        pass

def st_add_command(stcmd):
    """
    Add a new command!
    """

    global __st_commands

    __st_commands[stcmd.name] = stcmd

def st_add_alias(alias, cmdname):
    """
    Add a new alias for a command!
    """

    global __st_aliases

    __st_aliases[alias] = cmdname

def st_get_command(cmd_name):
    """
    Resolves a string, cmd_name, into a command object. This first checks the
    alias list and then looks up the command using an alias if an alias was
    found.
    """

    global __st_commands
    global __st_aliases

    # Just return the cmd_name if nothing is found.
    resolved_name = __st_aliases.get(cmd_name, cmd_name)

    return __st_commands.get(resolved_name)

def st_get_commands():
    """
    Get real commands. Doesn't get any aliases.
    """

    global __st_commands

    for k in sorted(__st_commands.keys()):
        yield __st_commands[k]

def st_get_aliases():
    """
    Get aliases.
    """

    global __st_aliases

    for k in sorted(__st_aliases.keys()):
        yield k, __st_aliases[k]
