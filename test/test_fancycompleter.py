from fancycompleter import DefaultConfig, Completer, setcolor

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
        if setcolor('__class__', '31') in match:
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
