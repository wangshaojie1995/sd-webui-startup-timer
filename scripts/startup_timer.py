import inspect

from modules import script_callbacks
from startup_timer_api import on_app_started, on_model_loaded

script_callbacks.on_app_started(on_app_started)
script_callbacks.on_model_loaded(on_model_loaded)
