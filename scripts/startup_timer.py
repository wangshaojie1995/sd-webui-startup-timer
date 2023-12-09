import inspect

from startup_timer_api import on_app_started

from modules import script_callbacks

script_callbacks.on_app_started(on_app_started)
