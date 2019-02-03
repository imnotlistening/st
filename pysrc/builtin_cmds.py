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

        lines = [ ]

        lines.append('ST command help. ST is a stock tracker app for the')
        lines.append('command line. Customizable and extensible!')
        lines.append('')
        lines.append('ST Commands')
        lines.append('-----------')
        lines.append('')

        for c in st_get_commands():
            lines.append('  %s' % c)

        lines.append('')
        lines.append('Aliases          Command')
        lines.append('-------          -------')
        for a, c in st_get_aliases():
            lines.append('  %-14s %s' % (a, c))

        return lines

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

        lines.append('Loading commands:')

        for c in cmd[1:]:
            # Handle load...
            lines.append('  > %-30s: <UNKNOWN>' % c)

        return lines

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

        lines = [ ]

        if len(cmd) < 3:
            lines.append('Invalid alias command: \'%s\'' % ' '.join(cmd))
            return lines

        alias  = cmd[1]
        cmdstr = cmd[2]

        st_add_alias(alias, cmdstr)

        lines.append('New alias: \'%s\' -> \'%s\'' % (alias, cmdstr))
        return lines

st_add_command(STCommandHelp())
st_add_command(STCommandLoad())
st_add_command(STCommandQuit())
st_add_command(STCommandAlias())
