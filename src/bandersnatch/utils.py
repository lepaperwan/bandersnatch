import asyncio
import contextlib
import functools
import hashlib
import logging
import os
import os.path
import platform
import re
import shutil
import sys
import tempfile
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, AnyStr, Generator, Generic, IO, List, Set, Union
from urllib.parse import urlparse

import aiohttp

from . import __version__

logger = logging.getLogger(__name__)


def user_agent() -> str:
    template = "bandersnatch/{version} ({python}, {system})"
    template += f" (aiohttp {aiohttp.__version__})"
    version = __version__
    python = sys.implementation.name
    python += " {}.{}.{}-{}{}".format(*sys.version_info)
    uname = platform.uname()
    system = " ".join([uname.system, uname.machine])
    return template.format(**locals())


SAFE_NAME_REGEX = re.compile(r"[^A-Za-z0-9.]+")
USER_AGENT = user_agent()
WINDOWS = bool(platform.system() == "Windows")


class AIO(Generic[AnyStr]):
    """Asynchronous version of typing.IO"""

    __slots__ = ()

    @property
    @abstractmethod
    def mode(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @property
    @abstractmethod
    def closed(self) -> bool:
        pass

    @abstractmethod
    def fileno(self) -> int:
        pass

    @abstractmethod
    async def flush(self) -> None:
        pass

    @abstractmethod
    def isatty(self) -> bool:
        pass

    @abstractmethod
    async def read(self, n: int = -1) -> AnyStr:
        pass

    @abstractmethod
    def readable(self) -> bool:
        pass

    @abstractmethod
    async def readline(self, limit: int = -1) -> AnyStr:
        pass

    @abstractmethod
    async def readlines(self, hint: int = -1) -> List[AnyStr]:
        pass

    @abstractmethod
    def seek(self, offset: int, whence: int = 0) -> int:
        pass

    @abstractmethod
    def seekable(self) -> bool:
        pass

    @abstractmethod
    def tell(self) -> int:
        pass

    @abstractmethod
    async def truncate(self, size: int = None) -> int:
        pass

    @abstractmethod
    def writable(self) -> bool:
        pass

    @abstractmethod
    async def write(self, s: AnyStr) -> int:
        pass

    @abstractmethod
    async def writelines(self, lines: List[AnyStr]) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> 'AIO[AnyStr]':
        pass

    @abstractmethod
    async def __aexit__(self, type, value, traceback) -> None:
        pass


def make_time_stamp() -> str:
    """Helper function that returns a timestamp suitable for use
    in a filename on any OS"""
    return f"{datetime.utcnow().isoformat()}Z".replace(":", "")


def convert_url_to_path(url: str) -> str:
    return urlparse(url).path[1:]


def hash(path: Path, function: str = "sha256") -> str:
    h = getattr(hashlib, function)()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(128 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return str(h.hexdigest())


def find(root: Union[Path, str], dirs: bool = True) -> str:
    """A test helper simulating 'find'.

    Iterates over directories and filenames, given as relative paths to the
    root.

    """
    # TODO: account for alternative backends
    if isinstance(root, str):
        root = Path(root)

    results: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        names = filenames
        if dirs:
            names += dirnames
        for name in names:
            results.append(Path(dirpath) / name)
    results.sort()
    return "\n".join(str(result.relative_to(root)) for result in results)


@contextlib.contextmanager
def rewrite(
    filepath: Union[str, Path], mode: str = "w", **kw: Any
) -> Generator[IO, None, None]:
    """Rewrite an existing file atomically to avoid programs running in
    parallel to have race conditions while reading."""
    # TODO: Account for alternative backends
    if isinstance(filepath, str):
        base_dir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
    else:
        base_dir = str(filepath.parent)
        filename = filepath.name

    # Change naming format to be more friendly with distributed POSIX
    # filesystems like GlusterFS that hash based on filename
    # GlusterFS ignore '.' at the start of filenames and this avoid rehashing
    with tempfile.NamedTemporaryFile(
        mode=mode, prefix=f".{filename}.", delete=False, dir=base_dir, **kw
    ) as f:
        filepath_tmp = f.name
        yield f

    if not os.path.exists(filepath_tmp):
        # Allow our clients to remove the file in case it doesn't want it to be
        # put in place actually but also doesn't want to error out.
        return
    os.chmod(filepath_tmp, 0o100644)
    shutil.move(filepath_tmp, filepath)


def recursive_find_files(files: Set[Path], base_dir: Path) -> None:
    dirs = [d for d in base_dir.iterdir() if d.is_dir()]
    files.update([x for x in base_dir.iterdir() if x.is_file()])
    for directory in dirs:
        recursive_find_files(files, directory)


def unlink_parent_dir(path: Path) -> None:
    """ Remove a file and if the dir is empty remove it """
    logger.info(f"unlink {str(path)}")
    path.unlink()

    parent_path = path.parent
    try:
        parent_path.rmdir()
        logger.info(f"rmdir {str(parent_path)}")
    except OSError as oe:
        logger.debug(f"Did not remove {str(parent_path)}: {str(oe)}")


def bandersnatch_safe_name(name: str) -> str:
    """Convert an arbitrary string to a standard distribution name
    Any runs of non-alphanumeric/. characters are replaced with a single '-'.

    - This was copied from `pkg_resources` (part of `setuptools`)

    bandersnatch also lower cases the returned name
    """
    return SAFE_NAME_REGEX.sub("-", name).lower()


def run_in_executor(func_or_executor, executor=None):
    """
    Function decorator to automatically schedule the wrapped synchronous
    function for execution in an executor (or the loop default if unspecified).

    The wrapped method will raise RuntimeError if called outside a running
    event loop.
    """
    if not callable(func_or_executor):
        return functools.partial(run_in_executor, executor=func_or_executor)

    @functools.wraps(func_or_executor)
    async def wrapper(*args, **kwargs):
        nonlocal executor

        # loop.run_in_executor doesn't support kwargs making `partial`
        # mandatory to support the generic use-case
        func = functools.partial(func_or_executor, *args, **kwargs)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, func)

    return wrapper()
