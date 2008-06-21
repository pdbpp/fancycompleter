from rlcompleter_ng import DefaultConfig, Completer, setcolor

def test_complete_attribute():
    compl = Completer({'a': 42}, DefaultConfig)
    assert compl.attr_matches('a.') == ['a.__']
    matches = compl.attr_matches('a.__')
    assert 'a.__abs__' not in matches
    assert '__abs__' in matches
    assert compl.attr_matches('a.__abs') == ['a.__abs__']

def test_complete_attribute_colored():
    class ColorConfig(DefaultConfig):
        use_colors = True
        color_by_type = {type: '31'}
        
    compl = Completer({'a': 42}, ColorConfig)
    matches = compl.attr_matches('a.__')
    for match in matches:
        if setcolor('__class__', '31') in match:
            break
    else:
        assert False
    assert ' ' in matches

def test_complete_global():
    compl = Completer({'foobar': 1, 'foobazzz': 2}, DefaultConfig)
    assert compl.global_matches('foo') == ['fooba']
    matches = compl.global_matches('fooba')
    assert set(matches) == set(['foobar', 'foobazzz', ' '])
    assert compl.global_matches('foobaz') == ['foobazzz']
