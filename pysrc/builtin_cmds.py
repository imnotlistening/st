#
# The built in ST commands.
#

from stcommand import STCommand
from stcommand import st_add_command
from stcommand import st_get_commands
from stcommand import st_add_alias
from stcommand import st_get_aliases

class STCommandQuit(STCommand):
    """
    Quit ST.
    """

    def __init__(self):
        super(STCommandQuit, self).__init__('quit',
                                            'Quit ST', None, 0)

    def update(self, cmd):
        # Just die.
        exit()

class STCommandHelp(STCommand):
    """
    A command to display help messages for all commands.
    """

    def __init__(self):
        """
        This builds a 'help' command which displays a help message based on the
        passed dictionary of commands.
        """

        super(STCommandHelp, self).__init__('help',
                                        'Display a summary of known commands',
                                        None, 0)

    def update(self, cmd):
        """
        Run through the list of known commands and display their help messages.
        """

        self.println('ST command help. ST is a stock tracker app for the')
        self.println('command line. Customizable and extensible!')
        self.println('')
        self.println('ST Commands')
        self.println('-----------')
        self.println('')

        for c in st_get_commands():
            self.println('  %s' % c)

        self.println('')
        self.println('Aliases          Command')
        self.println('-------          -------')
        for a, c in st_get_aliases():
            self.println('  %-14s %s' % (a, c))

        return STCommand.SUCCESS

class STCommandLoad(STCommand):
    """
    Allow the user to load custom pyhton commands!
    """

    def __init__(self):
        super(STCommandLoad, self).__init__('load',
                                            'Load a custom command', None, 0)

    def update(self, cmd):
        """
        Load a custom command. TBD how the semantics of this will work, though.
        """

        lines = [ ]

        for c in cmd[1:]:
            # Handle load...
            self.println('  > %-30s: <UNKNOWN>' % c)

        return STCommand.SUCCESS

class STCommandAlias(STCommand):
    """
    Allow a user to alias one command to another one. For example:

      alias h help

    Means that the command 'h' will invoke 'help'. Note this lets you override
    built in commands.
    """

    def __init__(self):
        super(STCommandAlias, self).__init__('alias',
                                    'Create an alias for a command', None, 0)

    def update(self, cmd):
        """
        Create an alias.
        """

        if len(cmd) < 3:
            self.println('Invalid alias command: \'%s\'' % ' '.join(cmd))
            return STCommand.FAILURE

        alias  = cmd[1]
        cmdstr = cmd[2]

        st_add_alias(alias, cmdstr)

        self.println('New alias: \'%s\' -> \'%s\'' % (alias, cmdstr))

        return STCommand.SUCCESS

st_add_command(STCommandHelp())
st_add_command(STCommandLoad())
st_add_command(STCommandQuit())
st_add_command(STCommandAlias())

st_add_alias('h', 'help')
st_add_alias('q', 'quit')
