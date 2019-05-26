"""
fancycompleter: colorful TAB completion for Python prompt
"""
from __future__ import with_statement
from __future__ import print_function

import rlcompleter
import sys
import types
import os.path
from itertools import count
try:
    reduce
except NameError:
    from functools import reduce

PY3K = sys.version_info[0] >= 3

# python3 compatibility
# ---------------------
try:
    from itertools import izip
except ImportError:
    izip = zip

try:
    from types import ClassType
except ImportError:
    ClassType = type

try:
    unicode
except NameError:
    unicode = str

# ----------------------

class LazyVersion(object):

    def __init__(self, pkg):
        self.pkg = pkg
        self.__version = None

    @property
    def version(self):
        if self.__version is None:
            self.__version = self._load_version()
        return self.__version

    def _load_version(self):
        try:
            from pkg_resources import get_distribution, DistributionNotFound
        except ImportError:
            return 'N/A'
        #
        try:
            return get_distribution(self.pkg).version
        except DistributionNotFound:
            # package is not installed
            return 'N/A'

    def __repr__(self):
        return self.version

    def __eq__(self, other):
        return self.version == other

    def __ne__(self, other):
        return not self == other

__version__ = LazyVersion(__name__)

# ----------------------

class Color:
    black = '30'
    darkred = '31'
    darkgreen = '32'    
    brown = '33'
    darkblue = '34'
    purple = '35'
    teal = '36'
    lightgray = '37'
    darkgray = '30;01'
    red = '31;01'
    green = '32;01'
    yellow = '33;01'
    blue = '34;01'
    fuchsia = '35;01'
    turquoise = '36;01'
    white = '37;01'

    @classmethod
    def set(cls, color, string):
        try:
            color = getattr(cls, color)
        except AttributeError:
            pass
        return '\x1b[%sm%s\x1b[00m' % (color, string)

class DefaultConfig:

    consider_getitems = True
    prefer_pyrepl = True
    use_colors = 'auto'  
    readline = None # set by setup()
    using_pyrepl = False # overwritten by find_pyrepl
  
    color_by_type = {
        types.BuiltinMethodType: Color.turquoise,
        types.BuiltinMethodType: Color.turquoise,
        types.MethodType: Color.turquoise,
        type((42).__add__): Color.turquoise,
        type(int.__add__): Color.turquoise,
        type(str.replace): Color.turquoise,

        types.FunctionType: Color.blue,
        types.BuiltinFunctionType: Color.blue,
        
        ClassType: Color.fuchsia,
        type: Color.fuchsia,
        
        types.ModuleType: Color.teal,
        type(None): Color.lightgray,
        str: Color.green,
        unicode: Color.green,
        int: Color.yellow,
        float: Color.yellow,
        complex: Color.yellow,
        bool: Color.yellow,
        }

    def find_pyrepl(self):
        try:
            import pyrepl.readline
            import pyrepl.completing_reader
        except ImportError:
            return None
        self.using_pyrepl = True
        if hasattr(pyrepl.completing_reader, 'stripcolor'):
            # modern version of pyrepl
            return pyrepl.readline, True
        else:
            return pyrepl.readline, False

    def find_pyreadline(self):
        try:
            import readline
            import pyreadline
            from pyreadline.modes import basemode
        except ImportError:
            return None
        if hasattr(basemode, 'stripcolor'):
            # modern version of pyreadline; see:
            # https://github.com/pyreadline/pyreadline/pull/48
            return readline, True
        else:
            return readline, False

    def find_best_readline(self):
        if self.prefer_pyrepl:
            result = self.find_pyrepl()
            if result:
                return result
        if sys.platform == 'win32':
            result = self.find_pyreadline()
            if result:
                return result
        import readline
        return readline, False # by default readline does not support colors

    def setup(self):
        self.readline, supports_color = self.find_best_readline()
        if self.use_colors == 'auto':
            self.use_colors = supports_color

def my_execfile(filename, mydict):
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
        exec(code, mydict)


class ConfigurableClass:
    DefaultConfig = None
    config_filename = None

    def get_config(self, Config):
        if Config is not None:
            return Config()
        # try to load config from the ~/filename file
        filename = '~/' + self.config_filename
        rcfile = os.path.expanduser(filename)
        if os.path.exists(rcfile):
            mydict = {}
            try:
                my_execfile(rcfile, mydict)
                return mydict['Config']()
            except Exception:
                # python 2.5 compatibility, can't use 'except Exception as e'
                e = sys.exc_info()[1]
                print('** error when importing %s: %s **' % (filename, e))
        return self.DefaultConfig()


class Completer(rlcompleter.Completer, ConfigurableClass):
    """
    When doing someting like a.b.<TAB>, display only the attributes of
    b instead of the full a.b.attr string.
    
    Optionally, display the various completions in different colors
    depending on the type.
    """

    DefaultConfig = DefaultConfig
    config_filename = '.fancycompleterrc.py'

    def __init__(self, namespace = None, Config=None):
        rlcompleter.Completer.__init__(self, namespace)
        self.config = self.get_config(Config)
        self.config.setup()
        readline = self.config.readline
        if hasattr(readline, '_setup'):
            # this is needed to offer pyrepl a better chance to patch
            # raw_input. Usually, it does at import time, but is we are under
            # pytest with output captured, at import time we don't have a
            # terminal and thus the raw_input hook is not installed
            readline._setup()
        if self.config.use_colors:
            readline.parse_and_bind('set dont-escape-ctrl-chars on')
        if self.config.consider_getitems:
            delims = readline.get_completer_delims()
            delims = delims.replace('[', '')
            delims = delims.replace(']', '')
            readline.set_completer_delims(delims)

    def complete(self, text, state):
        """
        stolen from:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496812
        """
        if text == "":
            return ['\t',None][state]
        else:
            return rlcompleter.Completer.complete(self,text,state)
            
    def _callable_postfix(self, val, word):
        # disable automatic insertion of '(' for global callables: this method exists only in Python 2.6+
        return word

    def global_matches(self, text):
        import keyword
        names = rlcompleter.Completer.global_matches(self, text)
        prefix = commonprefix(names)
        if prefix and prefix != text:
            return [prefix]

        names.sort()
        values = []
        for name in names:
            if name in keyword.kwlist:
                values.append(None)
            else:
                try:
                    values.append(eval(name, self.namespace))
                except Exception:
                    # Skip e.g. SyntaxError with "elif".
                    pass
        return self.color_matches(names, values)

    def attr_matches(self, text):
        import re
        expr, attr = text.rsplit('.', 1)
        if '(' in expr or ')' in expr:  # don't call functions
            return
        try:
            object = eval(expr, self.namespace)
        except Exception:
            return []
        names = []
        values = []
        n = len(attr)
        for word in dir(object):
            if isinstance(word, unicode) and not PY3K:
                # this is needed because pyrepl doesn't like unicode
                # completions: as soon as it finds something which is not str,
                # it stops.
                word = word.encode('utf-8')
            if word[:n] == attr and word != "__builtins__":
                names.append(word)
                try:
                    value = getattr(object, word)
                except:
                    value = None
                values.append(value)
                
        prefix = commonprefix(names)
        if prefix and prefix != attr:
            return ['%s.%s' % (expr, prefix)] # autocomplete prefix
        return self.color_matches(names, values)

    def color_matches(self, names, values):
        matches = [self.color_for_obj(i, name, obj)
                   for i, name, obj
                   in izip(count(), names, values)]
        # we add a space at the end to prevent the automatic completion of the
        # common prefix, which is the ANSI ESCAPE sequence
        if matches:
            return matches + [' ']
        return []

    def color_for_obj(self, i, name, value):
        if not self.config.use_colors:
            return name
        t = type(value)
        color = self.config.color_by_type.get(t, '00')
        # hack hack hack
        # prepend a fake escape sequence, so that readline can sort the matches correctly
        return '\x1b[%03d;00m' % i + Color.set(color, name)


# stolen from rlcompleter2
def commonprefix(names, base = ''):
    """ return the common prefix of all 'names' starting with 'base'
    """
    def commonfunc(s1,s2):
        while not s2.startswith(s1): 
            s1=s1[:-1]
        return s1

    if base:
        names = filter(lambda x, base=base: x.startswith(base), names)
        names = list(names) # for py3k
    if not names:
        return ''
    return reduce(commonfunc,names)


def has_leopard_libedit(config):
    # Detect if we are using Leopard's libedit.
    # Adapted from IPython's rlineimpl.py.
    if config.using_pyrepl or sys.platform != 'darwin':
        return False
    from subprocess import Popen, PIPE
    cmd = ["otool", "-L", config.readline.__file__]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode == 0 and 'libedit' in stdout.decode('utf-8'):
        return True
    return False
    
def setup():
    """
    Install fancycompleter as the default completer for readline.
    """
    completer = Completer()
    readline = completer.config.readline
    if has_leopard_libedit(completer.config):
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
    readline.set_completer(completer.complete)
    return completer

def interact_pyrepl():
    import pyrepl
    import os, sys
    from pyrepl import readline
    from pyrepl.simple_interact import run_multiline_interactive_console
    sys.modules['readline'] = readline
    run_multiline_interactive_console()

def setup_history(completer, persist_history):
    import atexit
    readline = completer.config.readline
    #
    if isinstance(persist_history, (str, unicode)):
        filename = persist_history
    else:
        filename = '~/.history.py'
    filename = os.path.expanduser(filename)
    if os.path.isfile(filename):
        readline.read_history_file(filename)
    def save_history():
        readline.write_history_file(filename)
    atexit.register(save_history)

def interact(persist_history=None):
    """
    Main entry point for fancycompleter: run an interactive Python session
    after installing fancycompleter.

    This function is supposed to be called at the end of PYTHONSTARTUP:

      - if we are using pyrepl: install fancycompleter, run pyrepl multiline
        prompt, and sys.exit().  The standard python prompt will never be
        reached

      - if we are not using pyrepl: install fancycompleter and return.  The
        execution will continue as normal, and the standard python prompt will
        be displayed.

    This is necessary because there is no way to tell the standard python
    prompt to use the readline provided by pyrepl instead of the builtin one.

    By default, pyrepl is preferred and automatically used if found.
    """
    import sys
    completer = setup()
    if persist_history:
        setup_history(completer, persist_history)
    if completer.config.using_pyrepl and '__pypy__' not in sys.builtin_module_names:
        # if we are on PyPy, we don't need to run a "fake" interpeter, as the
        # standard one is fake enough :-)
        interact_pyrepl()
        sys.exit()


class Installer(object):
    """
    Helper to install fancycompleter in PYTHONSTARTUP
    """

    def __init__(self, basepath, force):
        fname = os.path.join(basepath, 'python_startup.py')
        self.filename = os.path.expanduser(fname)
        self.force = force

    def check(self):
        PYTHONSTARTUP = os.environ.get('PYTHONSTARTUP')
        if PYTHONSTARTUP:
            return 'PYTHONSTARTUP already defined: %s' % PYTHONSTARTUP
        if os.path.exists(self.filename):
            return '%s already exists' % self.filename

    def install(self):
        import textwrap
        error = self.check()
        if error and not self.force:
            print(error)
            print('Use --force to overwrite.')
            return False
        with open(self.filename, 'w') as f:
            f.write(textwrap.dedent("""
                import fancycompleter
                fancycompleter.interact(persist_history=True)
            """))
        self.set_env_var()
        return True

    def set_env_var(self):
        if sys.platform == 'win32':
            os.system('SETX PYTHONSTARTUP "%s"' % self.filename)
            print('%PYTHONSTARTUP% set to', self.filename)
        else:
            print('startup file written to', self.filename)
            print('Append this line to your ~/.bashrc:')
            print('    export PYTHONSTARTUP=%s' % self.filename)


if __name__ == '__main__':
    def usage():
        print('Usage: python -m fancycompleter install [-f|--force]')
        sys.exit(1)
    
    cmd = None
    force = False
    for item in sys.argv[1:]:
        if item in ('install',):
            cmd = item
        elif item in ('-f', '--force'):
            force = True
        else:
            usage()
    #
    if cmd == 'install':
        installer = Installer('~', force)
        installer.install()
    else:
        usage()
