"""
fancycompleter
==============

This module represents an alternative to rlcompleter and rlcompleter2,
for those who don't like their default behaviour.

There are two main differences between stdlib's rlcompleter and
fancycompleter:

  - when doing something like a.b.c.<TAB>, rlcompleter prepends a.b.c
    to all the completions it finds; fancycompleter displays only the
    attributes, making the screen less cluttered;

  - you can use the <TAB> key both to indent (when the current line is
    blank) or to complete (when it's not blank);

  - more important, fancycompleter prints the various attributes found
    in different colors depending on their type.

Unfortunately, the default version of libreadline don't support
colored completions, so you need to patch it to fully exploid
fancycompleter capabilities.

You can find the patches in the misc/ directory.

Installation
------------

Simply put the file fancycompleter.py in a directory which is in your
PYTHONPATH.

Configuration
-------------

Since it requires a patched version of libreadline, coloured
completions are disabled by default.

To customize the configuration of fancycompleter, you need to put a
file named .fancycompleterrc.py in your home directory.  The file must
contain a class named ``Config`` inheriting from ``DefaultConfig`` and
overridding the desired values.

You can find a sample configuration file, which enables colors, in the
``fancycompleterrc.py`` file.

Usage
-----

From the interactive prompt, import fancycompleter and call setup():

>>> import fancycompleter
>>> fancycompleter.setup()

Alternatively, you can put these lines in some file that it's
referenced by the PYTHONSTARTUP environment variable, so that
completions is always enabled.
"""

__version__='0.1'
__author__ ='Antonio Cuni <anto.cuni@gmail.com>'
__url__='http://bitbucket.org/antocuni/fancycompleter'

import rlcompleter
import types
import os.path
from itertools import izip, count

class colors:
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


class DefaultConfig:

    consider_getitems = True

    readline = None # set by setup()
    prefer_pyrepl = True
    use_colors = 'auto'
    
    color_by_type = {
        types.BuiltinMethodType: colors.turquoise,
        types.BuiltinMethodType: colors.turquoise,
        types.MethodType: colors.turquoise,
        type((42).__add__): colors.turquoise,
        type(int.__add__): colors.turquoise,
        type(str.replace): colors.turquoise,

        types.FunctionType: colors.blue,
        types.BuiltinFunctionType: colors.blue,
        
        types.ClassType: colors.fuchsia,
        type: colors.fuchsia,
        
        types.ModuleType: colors.teal,
        types.NoneType: colors.lightgray,
        str: colors.green,
        unicode: colors.green,
        int: colors.yellow,
        float: colors.yellow,
        complex: colors.yellow,
        bool: colors.yellow,
        }

    def find_pyrepl(self):
        try:
            import pyrepl.readline
            import pyrepl.completing_reader
        except ImportError:
            return None
        if hasattr(pyrepl.completing_reader, 'stripcolor'):
            # modern version of pyrepl
            pyrepl.completing_reader.USE_BRACKETS = False
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

def setcolor(s, color):
    return '\x1b[%sm%s\x1b[00m' % (color, s)


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
                execfile(rcfile, mydict)
                return mydict['Config']()
            except Exception, e:
                print '** error when importing %s: %s **' % (filename, e)
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
        return '\x1b[%03d;00m' % i + setcolor(name, color)


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


def has_leopard_libedit():
    import commands
    import sys
    # Detect if we are using Leopard's libedit.
    # Taken from IPython's rlineimpl.py.
    if sys.platform != 'darwin':
        return False
    cmd =  "otool -L %s | grep libedit" % readline.__file__
    (status, result) = commands.getstatusoutput(cmd)
    if status == 0 and len(result) > 0:
        return True
    return False
    
def setup():
    completer = Completer()
    readline = completer.config.readline
    if has_leopard_libedit():
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
    readline.set_completer(completer.complete)
