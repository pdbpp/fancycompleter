import os
from fancycompleter import DefaultConfig, Completer, Color, Installer

class ConfigForTest(DefaultConfig):
    use_colors = False

def test_complete_attribute():
    compl = Completer({'a': None}, ConfigForTest)
    assert compl.attr_matches('a.') == ['a.__']
    matches = compl.attr_matches('a.__')
    assert 'a.__class__' not in matches
    assert '__class__' in matches
    assert compl.attr_matches('a.__class') == ['a.__class__']

def test_complete_attribute_colored():
    class ColorConfig(DefaultConfig):
        use_colors = True
        color_by_type = {type: '31'}
        
    compl = Completer({'a': 42}, ColorConfig)
    matches = compl.attr_matches('a.__')
    for match in matches:
        if Color.set('31', '__class__') in match:
            break
    else:
        assert False
    assert ' ' in matches

def test_complete_global():
    compl = Completer({'foobar': 1, 'foobazzz': 2}, ConfigForTest)
    assert compl.global_matches('foo') == ['fooba']
    matches = compl.global_matches('fooba')
    assert set(matches) == set(['foobar', 'foobazzz', ' '])
    assert compl.global_matches('foobaz') == ['foobazzz']

def test_complete_with_indexer():
    compl = Completer({'lst': [None,2,3]}, ConfigForTest)
    assert compl.attr_matches('lst[0].') == ['lst[0].__']
    matches = compl.attr_matches('lst[0].__')
    assert 'lst[0].__class__' not in matches
    assert '__class__' in matches
    assert compl.attr_matches('lst[0].__class') == ['lst[0].__class__']


def test_unicode_in___dir__():
    class Foo(object):
        def __dir__(self):
            return [u'hello', 'world']

    compl = Completer({'a': Foo()}, ConfigForTest)
    matches = compl.attr_matches('a.')
    assert matches == ['hello', 'world', ' ']
    assert type(matches[0]) is str


class MyInstaller(Installer):
    env_var = 0

    def set_env_var(self):
        self.env_var += 1

class TestInstaller(object):
    
    def test_check(self, monkeypatch, tmpdir):
        installer = MyInstaller(str(tmpdir), force=False)
        monkeypatch.setenv('PYTHONSTARTUP', '')
        assert installer.check() is None
        f = tmpdir.join('python_startup.py').ensure(file=True)
        assert installer.check() == '%s already exists' % f
        monkeypatch.setenv('PYTHONSTARTUP', 'foo')
        assert installer.check() == 'PYTHONSTARTUP already defined: foo'

    def test_install(self, monkeypatch, tmpdir):
        installer = MyInstaller(str(tmpdir), force=False)
        monkeypatch.setenv('PYTHONSTARTUP', '')
        assert installer.install()
        assert 'fancycompleter' in tmpdir.join('python_startup.py').read()
        assert installer.env_var == 1
        #
        # the second time, it fails because the file already exists
        assert not installer.install()
        assert installer.env_var == 1
        #
        # the third time, it succeeds because we set force
        installer.force = True
        assert installer.install()
        assert installer.env_var == 2
        
