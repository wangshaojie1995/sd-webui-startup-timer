import math
import time
from secrets import compare_digest
from threading import Lock
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from startup_timer import startup_timer_class

from modules import shared, timer
from modules.call_queue import queue_lock


class Api:
    version = 1

    def __init__(self, app: FastAPI, queue_lock: Lock, prefix: str = None) -> None:
        if shared.cmd_opts.api_auth:
            self.credentials = dict()
            for auth in shared.cmd_opts.api_auth.split(","):
                user, password = auth.split(":")
                self.credentials[user] = password

        self.app = app
        self.queue_lock = queue_lock
        self.prefix = prefix

        self.add_api_route(
            'detail',
            self.startupTimer,
            methods=['GET'],
        )

    def auth(self, creds: HTTPBasicCredentials = Depends(HTTPBasic())):
        if creds.username in self.credentials:
            if compare_digest(creds.password, self.credentials[creds.username]):
                return True

        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Basic"
            })

    def add_api_route(self, path: str, endpoint: Callable, **kwargs):
        if self.prefix:
            path = f'{self.prefix}/{path}'
        if shared.cmd_opts.api_auth:
            return self.app.add_api_route(path, endpoint, dependencies=[Depends(self.auth)], **kwargs)
        return self.app.add_api_route(path, endpoint, **kwargs)

    def startupTimer(self):
        startup_timer = timer.startup_timer
        version = self.version
        self.version += 1
        modeLoaded = math.ceil(
            startup_timer_class.modeLoadedTime - startup_timer_class.startedTime)
        return {**startup_timer.dump(), "version": version, 'modeLoaded': modeLoaded}


def on_app_started(_, app: FastAPI):
    Api(app, queue_lock, '/startup-timer')
    startup_timer_class.startedTime = time.time()
    # print('on_app_started -=-=-=-=-=',
    #       startup_timer_class.startedTime)


def on_model_loaded(sd_model):
    startup_timer_class.modeLoadedTime = time.time()
    # print('on_model_loaded -=-=-=-=-=', startup_timer_class.modeLoadedTime)
