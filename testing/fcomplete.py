import cmd
import sys

from fancycompleter import interact, DefaultConfig


class ConfigForTest(DefaultConfig):
    use_colors = False


class CompleterCmd(cmd.Cmd):
    prompt = ''


if __name__ == '__main__':
    globals().update({
        name: name
        for name in sys.argv[1:]
    })

    interact(Config=ConfigForTest)

    repl = CompleterCmd(completekey=None)
    repl.cmdloop(intro='')
