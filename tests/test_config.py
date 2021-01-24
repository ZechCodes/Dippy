import bevy
import dippy.config.config as config
import dippy.config.manager as manager
import pydantic
import pytest
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

    @pytest.fixture()
    def model(self):
        class Model(pydantic.BaseModel):
            test: str
            env: str = config.EnvField(env_var="TESTING", default="NOT SET")

        return Model

    @pytest.fixture()
    def model_env(self):
        os.environ["TESTING"] = "TEST"

        class Model(pydantic.BaseModel):
            test: str
            env: str = config.EnvField(env_var="TESTING", default="NOT SET")

        os.environ.pop("TESTING")

        return Model

    @pytest.fixture()
    def config_context(self):
        m = manager.ConfigManager(__file__, "")
        m.register_loader("test_load", r"\.py$", lambda f: {"test": "testing"})
        return bevy.Context().add(m)

    @pytest.fixture()
    def component(self, model):
        class Component(bevy.Injectable):
            factory: config.ConfigFactory[model]

            def config(self, *files):
                return self.factory(*files)

        return Component

    @pytest.fixture()
    def component_env(self, model_env):
        class Component(bevy.Injectable):
            factory: config.ConfigFactory[model_env]

            def config(self, *files):
                return self.factory(*files)

        return Component

    def test_get_value(self, config_context, component, model):
        c = config_context.create(component)
        assert c.config("test_config.py") == model(test="testing", env="NOT SET")

    def test_get_value_environment(self, config_context, component_env, model_env):
        c = config_context.create(component_env)
        assert c.config("test_config.py") == model_env(test="testing", env="TEST")
