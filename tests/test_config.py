import bevy
import dippy.config.config as config
import dippy.config.manager as manager
import os


class TestConfig:
    def test_invalid_path(self):
        try:
            manager.ConfigManager(__file__, "config")
        except Exception as e:
            assert isinstance(e, manager.InvalidConfigPath)

    def test_no_loaders(self):
        try:
            c = manager.ConfigManager(__file__, "")
            c.load("test_config.py")
        except Exception as e:
            assert isinstance(e, manager.NoConfigLoaderFound)

    def test_no_config_file(self):
        try:
            c = manager.ConfigManager(__file__, "")
            c.load("test_config.yaml")
        except Exception as e:
            assert isinstance(e, manager.InvalidConfigPath)

    def test_load(self):
        c = manager.ConfigManager(__file__, "")
        c.register_loader("test_load", r"\.py$", lambda f: f.name)
        assert c.load("test_config.py") == "test_config.py"

    def test_load_search(self):
        c = manager.ConfigManager(__file__, "")
        c.register_loader("test_load", r"\.py$", lambda f: f.name)
        assert c.load("dev_config.py", "test_config.py") == "test_config.py"

    def test_load_search_first(self):
        c = manager.ConfigManager(__file__, "")
        c.register_loader("test_load", r"\.py$", lambda f: f.name)
        assert c.load("__init__.py", "test_config.py") == "__init__.py"

    def test_get_value(self):
        m = manager.ConfigManager(__file__, "")
        m.register_loader("test_load", r"\.py$", lambda f: {"test": "testing"})
        context = bevy.Context().load(m)
        c = context.create(config.Config, __file__, "")
        assert c.get_value("test") == "testing"

    def test_get_value_required(self):
        m = manager.ConfigManager(__file__, "")
        m.register_loader("test_load", r"\.py$", lambda f: {})
        context = bevy.Context().load(m)
        c = context.create(config.Config, __file__, "")
        try:
            c.get_value("test", required=True)
        except Exception as e:
            assert isinstance(e, config.RequiredValueNotFound)

    def test_get_value_default(self):
        m = manager.ConfigManager(__file__, "")
        m.register_loader("test_load", r"\.py$", lambda f: {})
        context = bevy.Context().load(m)
        c = context.create(config.Config, __file__, "")
        assert c.get_value("test", default="foobar") == "foobar"

    def test_get_value_environment(self):
        os.environ["TESTING"] = "foobar"
        m = manager.ConfigManager(__file__, "")
        m.register_loader("test_load", r"\.py$", lambda f: {})
        context = bevy.Context().load(m)
        c = context.create(config.Config, __file__, "")
        assert c.get_value("test", env_name="TESTING") == "foobar"
