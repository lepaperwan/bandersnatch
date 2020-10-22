#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import abc
import io
from typing import (
    ByteString,
    Iterable,
    List,
    Optional,
    Union,
)


class AIOBase(abc.ABC, io.RawIOBase, metaclass=abc.ABCMeta):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        line = await self.readline()
        if not line:
            raise StopAsyncIteration

        return line

    @abc.abstractmethod
    async def close(self) -> None:
        pass

    @abc.abstractmethod
    async def flush(self) -> None:
        pass

    @abc.abstractmethod
    async def isatty(self) -> bool:
        pass

    @abc.abstractmethod
    async def read(self, size: int = ..., /) -> bytes:
        pass

    @abc.abstractmethod
    async def readall(self) -> bytes:
        pass

    @abc.abstractmethod
    async def readinto(self, buffer: Union[bytearray, memoryview], /) -> int:
        pass

    @abc.abstractmethod
    async def readline(self, size: Optional[int] = ..., /) -> bytes:
        pass

    @abc.abstractmethod
    async def readlines(self, hint: int = ..., /) -> List[bytes]:
        pass

    @abc.abstractmethod
    async def seek(self, offset: int, whence: int = ..., /) -> int:
        pass

    @abc.abstractmethod
    async def seekable(self) -> bool:
        pass

    @abc.abstractmethod
    async def tell(self) -> int:
        pass

    @abc.abstractmethod
    async def truncate(self, size: Optional[int] = ..., /) -> int:
        pass

    @abc.abstractmethod
    async def writable(self) -> bool:
        pass

    @abc.abstractmethod
    async def write(self, buffer: ByteString, /) -> int:
        pass

    @abc.abstractmethod
    async def writelines(self, lines: Iterable[ByteString], /) -> None:
        pass

# vim: fileencoding=utf-8 filetype=python autoindent expandtab shiftwidth=4 softtabstop=4 tabstop=4 nowrap
