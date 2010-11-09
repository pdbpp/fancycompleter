from rlcompleter_ng import DefaultConfig

class Config(DefaultConfig):
    prefer_pyrepl = False
    use_colors = True # need a patched libreadline
