import os
from importlib import import_module

try:
    # Prefer python-decouple so DJANGO_ENV can come from .env
    from decouple import config as env_config  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    env_config = None

if env_config is not None:
    env_name = str(env_config("DJANGO_ENV", default="dev")).strip().lower()
else:
    env_name = os.getenv("DJANGO_ENV", "dev").strip().lower()

module_name = "prod" if env_name == "prod" else "dev"
selected_settings = import_module(f"{__name__}.{module_name}")

# Export uppercase settings so Django can import from config.settings
for key in dir(selected_settings):
    if key.isupper():
        globals()[key] = getattr(selected_settings, key)

