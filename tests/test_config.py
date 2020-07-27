import dippy.config.manager as config


class TestConfig:
    def test_invalid_path(self):
        try:
            config.ConfigManager(__file__, "config")
        except Exception as e:
            assert isinstance(e, config.InvalidConfigPath)

    def test_no_loaders(self):
        try:
            c = config.ConfigManager(__file__, "")
            c.load("test_config.py")
        except Exception as e:
            assert isinstance(e, config.NoConfigLoaderFound)

    def test_no_config_file(self):
        try:
            c = config.ConfigManager(__file__, "")
            c.load("test_config.yaml")
        except Exception as e:
            assert isinstance(e, config.InvalidConfigPath)

    def test_load(self):
        c = config.ConfigManager(__file__, "")
        c.register_loader("test_load", r"\.py$", lambda f: f.name)
        assert c.load("test_config.py") == "test_config.py"

    def test_load_search(self):
        c = config.ConfigManager(__file__, "")
        c.register_loader("test_load", r"\.py$", lambda f: f.name)
        assert c.load("dev_config.py", "test_config.py") == "test_config.py"

    def test_load_search_first(self):
        c = config.ConfigManager(__file__, "")
        c.register_loader("test_load", r"\.py$", lambda f: f.name)
        assert c.load("__init__.py", "test_config.py") == "__init__.py"
