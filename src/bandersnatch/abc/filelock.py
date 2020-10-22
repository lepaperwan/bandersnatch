#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
from typing import (
    Optional,
)

import filelock


class BaseFileLock(filelock.BaseFileLock, metaclass=abc.ABCMeta):
    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.release()

    @abc.abstractmethod
    async def acquire(self, timeout: Optional[float] = None, poll_interval: float = 0.05) -> None:
        pass

    @abc.abstractmethod
    async def release(self, force: bool = False) -> None:
        pass

# vim: fileencoding=utf-8 filetype=python autoindent expandtab shiftwidth=4 softtabstop=4 tabstop=4 nowrap
