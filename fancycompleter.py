"""
fancycompleter: colorful TAB completion for Python prompt
"""

__version__='0.3'
__author__ ='Antonio Cuni <anto.cuni@gmail.com>'
__url__='http://bitbucket.org/antocuni/fancycompleter'

import rlcompleter
import types
import os.path
from itertools import count
from functools import reduce

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

    def find_best_readline(self):
        if self.prefer_pyrepl:
            result = self.find_pyrepl()
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
            except Exception as e:
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
                values.append(eval(name, self.namespace))
        matches = [self.color_for_obj(i, name, obj)
                   for i, name, obj
                   in izip(count(), names, values)]
        return matches + [' ']

    def attr_matches(self, text):
        import re
        expr, attr = text.rsplit('.', 1)
        if '(' in expr or ')' in expr:  # don't call functions
            return
        object = eval(expr, self.namespace)
        names = []
        values = []
        n = len(attr)
        for word in dir(object):
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

        matches = [self.color_for_obj(i, name, value)
                   for i, name, value
                   in izip(count(), names, values)]
        # we add a space at the end to prevent the automatic completion of the
        # common prefix, which is the ANSI ESCAPE sequence
        return matches + [' ']

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
        if not names:
            return ''
    return reduce(commonfunc,names)


def has_leopard_libedit(config):
    try:
        import commands
    except ImportError:
        # python3? just return False for now
        return False
    import sys
    # Detect if we are using Leopard's libedit.
    # Taken from IPython's rlineimpl.py.
    if config.using_pyrepl or sys.platform != 'darwin':
        return False
    cmd =  "otool -L %s | grep libedit" % config.readline.__file__
    (status, result) = commands.getstatusoutput(cmd)
    if status == 0 and len(result) > 0:
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
