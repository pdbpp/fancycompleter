from fancycompleter import ConfigurableClass


def test_config(tmphome, capsys):
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
    p = tmphome.ensure(MyCfg.config_filename)
    print(p, file=capsys._capture.out._old)
    cfgfile.write("def Config(): raise Exception('my_exc')")
    assert isinstance(cfg.get_config(None), DefaultCfg)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == (
        "XXX** error when setting up Config from ~/.mycfg: my_exc (%s:1) **\n" % p
    )
    print("passed first", file=capsys._capture.out._old)

    # Error during execfile.
    config_filename = tmphome.ensure(MyCfg.config_filename)
    print("config_filename:", config_filename, file=capsys._capture.out._old)
    cfgfile.write("raise Exception('my_execfile_exc')")
    assert isinstance(cfg.get_config(None), DefaultCfg)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "** error when importing ~/.mycfg: my_execfile_exc **\n"
