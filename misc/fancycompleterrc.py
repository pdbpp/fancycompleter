from fancycompleter import DefaultConfig


class Config(DefaultConfig):
    prefer_pyrepl = False  # force fancycompleter to use the standard readline
    use_colors = True  # you need a patched libreadline for this
