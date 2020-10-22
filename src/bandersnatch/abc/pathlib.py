#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import os
import pathlib
from typing import (
    AsyncContextManager,
    AsyncGenerator,
    Optional,
    Union,
)

from .io import AIOBase


class Path(pathlib.Path, metaclass=abc.ABCMeta):
    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)

    @abc.abstractmethod
    async def samefile(self, other_path: Union[os.PathLike, 'Path']) -> bool:
        pass

    @abc.abstractmethod
    async def iterdir(self) -> AsyncGenerator['Path', None]:
        pass

    @abc.abstractmethod
    async def glob(self, pattern: str) -> AsyncGenerator['Path', None]:
        pass

    @abc.abstractmethod
    async def rglob(self, pattern: str) -> AsyncGenerator['Path', None]:
        pass

    @abc.abstractmethod
    async def resolve(self, strict: bool = False) -> 'Path':
        pass

    @abc.abstractmethod
    async def stat(self, strict: bool = False) -> os.stat_result:
        pass

    @abc.abstractmethod
    async def owner(self, strict: bool = False) -> str:
        pass

    @abc.abstractmethod
    async def group(self, strict: bool = False) -> str:
        pass

    @abc.abstractmethod
    def open(self, mode: str = 'r', buffering: int = -1,
             encoding: Optional[str] = None, errors: Optional[str] = None,
             newline: Optional[str] = None) -> AsyncContextManager[AIOBase]:
        pass

    @abc.abstractmethod
    async def read_bytes(self) -> bytes:
        pass

    @abc.abstractmethod
    async def read_text(self, encoding: Optional[str] = None, errors: Optional[str] = None) -> str:
        pass

    @abc.abstractmethod
    async def write_bytes(self, data: bytes, ) -> int:
        pass

    @abc.abstractmethod
    async def write_text(self, data: str, encoding: Optional[str] = None, errors: Optional[str] = None) -> int:
        pass

    @abc.abstractmethod
    async def touch(self, mode: int = 0o666, exist_ok: bool = True) -> None:
        pass

    @abc.abstractmethod
    async def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        pass

    @abc.abstractmethod
    async def chmod(self, mode: int) -> None:
        pass

    @abc.abstractmethod
    async def lchmod(self, mode: int) -> None:
        pass

    @abc.abstractmethod
    async def unlink(self, missing_ok: bool = False) -> None:
        pass

    @abc.abstractmethod
    async def rmdir(self) -> None:
        pass

    @abc.abstractmethod
    async def lstat(self) -> os.stat_result:
        pass

    @abc.abstractmethod
    async def link_to(self, target: Union[os.PathLike, 'Path']) -> None:
        pass

    @abc.abstractmethod
    async def rename(self, target: Union[os.PathLike, 'Path']) -> 'Path':
        pass

    @abc.abstractmethod
    async def replace(self, target: Union[os.PathLike, 'Path']) -> 'Path':
        pass

    @abc.abstractmethod
    async def symlink_to(self, target: Union[os.PathLike, 'Path'], target_is_directory: bool = False) -> 'Path':
        pass

    # endregion

    # region Convenience functions for querying the stat results

    @abc.abstractmethod
    async def exists(self):
        pass

    @abc.abstractmethod
    async def is_dir(self):
        pass

    @abc.abstractmethod
    async def is_file(self):
        pass

    @abc.abstractmethod
    async def is_mount(self):
        pass

    @abc.abstractmethod
    async def is_symlink(self):
        pass

    @abc.abstractmethod
    async def is_block_device(self):
        pass

    @abc.abstractmethod
    async def is_char_device(self):
        pass

    @abc.abstractmethod
    async def is_fifo(self):
        pass

    @abc.abstractmethod
    async def is_socket(self):
        pass


__all__ = (
    'Path',
)

# vim: fileencoding=utf-8 filetype=python autoindent expandtab shiftwidth=4 softtabstop=4 tabstop=4 nowrap
