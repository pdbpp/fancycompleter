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

def find_readline():
    """
    Return the best "readline" module we can find.

    If pyrepl is installed and has support for colored completions, return it.
    Else, monkeypatch pyrepl to add support for colored completions.
    If pyrepl is not installed, just use the standard readline.
    """
    try:
        # prefer pyrepl
        import pyrepl.completing_reader
        import pyrepl.unix_console
        import pyrepl.readline
    except ImportError:
        # if not found, try readline
        import readline
        return readline, False
    #
    if hasattr(pyrepl.completing_reader, 'stripcolor'):
        # moder version of pyrepl, no monkeypatch needed
        return pyrepl.readline, True
    #
    # -----------------------------------------------------------------------------
    # monkeypatch pyrepl to support colors
    # this code will go away as soon as a new version of pyrepl is released
    #
    # inside class pyrepl.unix_console.UnixConsole
    class UnixConsole:
        # we put it inside a class so that __* names are mangled correctly
        def __write_changed_line(self, y, oldline, newline, px):
            # this is frustrating; there's no reason to test (say)
            # self.dch1 inside the loop -- but alternative ways of
            # structuring this function are equally painful (I'm trying to
            # avoid writing code generators these days...)
            x = 0
            minlen = min(len(oldline), len(newline))
            #
            # reuse the oldline as much as possible, but stop as soon as we
            # encounter an ESCAPE, because it might be the start of an escape
            # sequene
            while x < minlen and oldline[x] == newline[x] and newline[x] != '\x1b':
                x += 1
            if oldline[x:] == newline[x+1:] and self.ich1:
                if ( y == self.__posxy[1] and x > self.__posxy[0]
                     and oldline[px:x] == newline[px+1:x+1] ):
                    x = px
                self.__move(x, y)
                self.__write_code(self.ich1)
                self.__write(newline[x])
                self.__posxy = x + 1, y
            elif x < minlen and oldline[x + 1:] == newline[x + 1:]:
                self.__move(x, y)
                self.__write(newline[x])
                self.__posxy = x + 1, y
            elif (self.dch1 and self.ich1 and len(newline) == self.width
                  and x < len(newline) - 2
                  and newline[x+1:-1] == oldline[x:-2]):
                self.__hide_cursor()
                self.__move(self.width - 2, y)
                self.__posxy = self.width - 2, y
                self.__write_code(self.dch1)
                self.__move(x, y)
                self.__write_code(self.ich1)
                self.__write(newline[x])
                self.__posxy = x + 1, y
            else:
                self.__hide_cursor()
                self.__move(x, y)
                if len(oldline) > len(newline):
                    self.__write_code(self._el)
                self.__write(newline[x:])
                self.__posxy = len(newline), y
    pyrepl.unix_console.UnixConsole._UnixConsole__write_changed_line = \
        UnixConsole._UnixConsole__write_changed_line.im_func
    #
    import re
    def stripcolor(s):
        return stripcolor.regexp.sub('', s)
    stripcolor.regexp = re.compile(r"\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[m|K]")

    def real_len(s):
        return len(stripcolor(s))

    def left_align(s, maxlen):
        stripped = stripcolor(s)
        if len(stripped) > maxlen:
            # too bad, we remove the color
            return stripped[:maxlen]
        padding = maxlen - len(stripped)
        return s + ' '*padding

    def build_menu(cons, wordlist, start, use_brackets=False):
        if use_brackets:
            item = "[ %s ]"
            padding = 4
        else:
            item = "%s  "
            padding = 2
        maxlen = min(max(map(real_len, wordlist)), cons.width - padding)
        cols = cons.width / (maxlen + padding)
        rows = (len(wordlist) - 1)/cols + 1
        menu = []
        i = start
        for r in range(rows):
            row = []
            for col in range(cols):
                row.append(item % left_align(wordlist[i], maxlen))
                i += 1
                if i >= len(wordlist):
                    break
            menu.append( ''.join(row) )
            if i >= len(wordlist):
                i = 0
                break
            if r + 5 > cons.height:
                menu.append("   %d more... "%(len(wordlist) - i))
                break
        return menu, i    
    #
    pyrepl.completing_reader.build_menu = build_menu
    return pyrepl.readline, True

readline, SUPPORT_COLORS = find_readline()

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

    # WARNING: for this option to work properly, you need to patch readline with this:
    # http://codespeak.net/svn/user/antocuni/hack/readline-escape.patch
    use_colors = SUPPORT_COLORS
    
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
    if has_leopard_libedit():
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
    readline.set_completer(completer.complete)
