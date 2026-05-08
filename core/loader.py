import importlib
import pkgutil
import core.pipelines

def load_pipelines():
    for _, module_name, _ in pkgutil.iter_modules(core.pipelines.__path__):
        importlib.import_module(f"core.pipelines.{module_name}")
