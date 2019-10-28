import os

from fancycompleter import ConfigurableClass


def test_config(tmphome, capsys, LineMatcher):
    class DefaultCfg:
        default = 42

    class MyCfg(ConfigurableClass):
        DefaultConfig = DefaultCfg
        config_filename = ".mycfg"

    cfg = MyCfg()

    # Calls passed in Config.
    assert cfg.get_config(Config=lambda: "42") == "42"

    # Uses DefaultConfig instance.
    assert isinstance(cfg.get_config(None), DefaultCfg)

    cfgfile = tmphome.join(MyCfg.config_filename)

    # Handles empty config file (missing "Config").
    cfgfile.ensure()
    assert isinstance(cfg.get_config(None), DefaultCfg)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""

    # Exception when instantiating Config.
    p = os.path.normpath(str(tmphome.ensure(MyCfg.config_filename)))
    cfgfile.write("def Config(): raise Exception('my_exc')")
    assert isinstance(cfg.get_config(None), DefaultCfg)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == (
        "** error when setting up Config from ~/.mycfg: my_exc (%s:1) **\n" % p
    )

    # Error during execfile.
    tmphome.ensure(MyCfg.config_filename)
    cfgfile.write("raise Exception('my_execfile_exc')")
    assert isinstance(cfg.get_config(None), DefaultCfg)
    out, err = capsys.readouterr()
    assert out == ""
    LineMatcher(err.splitlines()).fnmatch_lines([
        "[*][*] error when importing ~/.mycfg: Exception('my_execfile_exc'*) [*][*]",
        '  File */fancycompleter.py", line *, in get_config',
        '    my_execfile(rcfile, mydict)',
        '  File */fancycompleter.py", line *, in my_execfile',
        '    exec(code, mydict)',
        '  File "*/test_config0/.mycfg", line 1, in <module>',
        "    raise Exception('my_execfile_exc')",
    ])
