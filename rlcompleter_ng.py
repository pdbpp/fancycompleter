import readline
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

    # WARNING: for this option to work properly, you need to patch readline with this:
    # http://codespeak.net/svn/user/antocuni/hack/readline-escape.patch
    use_colors = False
    
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
                print '** error when importing %s: %s **' % (s, e)
        return self.DefaultConfig()


class Completer(rlcompleter.Completer, ConfigurableClass):
    """
    When doing someting like a.b.<TAB>, display only the attributes of
    b instead of the full a.b.attr string.
    
    Optionally, display the various completions in different colors
    depending on the type.
    """

    DefaultConfig = DefaultConfig
    config_filename = '.rlcompleter_ng.py'

    def __init__(self, namespace = None, Config=None):
        rlcompleter.Completer.__init__(self, namespace)
        self.config = self.get_config(Config)
        if self.config.use_colors:
            readline.parse_and_bind('set dont-escape-ctrl-chars on')

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
        m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        if not m:
            return
        expr, attr = m.group(1, 3)
        object = eval(expr, self.namespace)
        names = []
        values = []
        n = len(attr)
        for word in dir(object):
            if word[:n] == attr and word != "__builtins__":
                names.append(word)
                values.append(getattr(object, word))
                
        prefix = commonprefix(names)
        if prefix and prefix != attr:
            return ['%s.%s' % (expr, prefix)] # autocomplete prefix

        matches = [self.color_for_obj(i, name, value)
                   for i, name, value
                   in izip(count(), names, values)]
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
