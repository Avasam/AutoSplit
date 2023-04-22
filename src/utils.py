from __future__ import annotations

import asyncio
import fcntl
import os
import subprocess
import sys
from collections.abc import Callable, Iterable
from enum import IntEnum
from platform import version
from threading import Thread
from typing import Any, TypeVar, cast

import cv2
from typing_extensions import TypeGuard

from gen.build_vars import AUTOSPLIT_BUILD_NUMBER, AUTOSPLIT_GITHUB_REPOSITORY

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes

    from win32 import win32gui
    from winsdk.windows.ai.machinelearning import LearningModelDevice, LearningModelDeviceKind
    from winsdk.windows.media.capture import MediaCapture

DWMWA_EXTENDED_FRAME_BOUNDS = 9
MAXBYTE = 255
RGB_CHANNEL_COUNT = 3
"""How many channels in an RGB image"""
RGBA_CHANNEL_COUNT = 4
"""How many channels in an RGB image"""


class ImageShape(IntEnum):
    X = 0
    Y = 1
    Alpha = 2


class ColorChannel(IntEnum):
    Red = 0
    Green = 1
    Blue = 2
    Alpha = 3


def decimal(value: int | float):
    # NOTE: The coeficient (1000) has to be above what's mathematically necessary (100)
    # because of python float rounding errors (ie: xx.99999999999999)
    return f"{int(value * 1000) / 1000:.2f}"


def is_digit(value: str | int | None):
    """Checks if `value` is a single-digit string from 0-9."""
    if value is None:
        return False
    try:
        return 0 <= int(value) <= 9  # noqa: PLR2004
    except (ValueError, TypeError):
        return False


def is_valid_image(image: cv2.Mat | None) -> TypeGuard[cv2.Mat]:
    return image is not None and bool(image.size)


def is_valid_hwnd(hwnd: int):
    """Validate the hwnd points to a valid window and not the desktop or whatever window obtained with `""`."""
    if not hwnd:
        return False
    if sys.platform == "win32":
        # TODO: Fix stubs, IsWindow should return a boolean
        return bool(win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd))
    return True


T = TypeVar("T")


def first(iterable: Iterable[T]) -> T:
    """@return: The first element of a collection. Dictionaries will return the first key."""
    return next(iter(iterable))


def get_window_bounds(hwnd: int) -> tuple[int, int, int, int]:
    if sys.platform != "win32":
        raise OSError

    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds),
    )

    window_rect = win32gui.GetWindowRect(hwnd)
    window_left_bounds = cast(int, extended_frame_bounds.left) - window_rect[0]
    window_top_bounds = cast(int, extended_frame_bounds.top) - window_rect[1]
    window_width = cast(int, extended_frame_bounds.right) - cast(int, extended_frame_bounds.left)
    window_height = cast(int, extended_frame_bounds.bottom) - cast(int, extended_frame_bounds.top)
    return window_left_bounds, window_top_bounds, window_width, window_height


def open_file(file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if sys.platform == "win32":
        os.startfile(file_path)  # noqa: S606
    else:
        opener = "xdg-open" if sys.platform == "linux" else "open"
        subprocess.call([opener, file_path])   # noqa: S603


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()


def get_direct3d_device():
    if sys.platform != "win32":
        raise OSError("Direct3D Device is only available on Windows")

    # Note: Must create in the same thread (can't use a global) otherwise when ran from LiveSplit it will raise:
    # OSError: The application called an interface that was marshalled for a different thread
    media_capture = MediaCapture()

    async def init_mediacapture():
        await (media_capture.initialize_async() or asyncio.sleep(0))
    asyncio.run(init_mediacapture())
    direct_3d_device = media_capture.media_capture_settings and \
        media_capture.media_capture_settings.direct3_d11_device
    if not direct_3d_device:
        try:
            # May be problematic? https://github.com/pywinrt/python-winsdk/issues/11#issuecomment-1315345318
            direct_3d_device = LearningModelDevice(LearningModelDeviceKind.DIRECT_X_HIGH_PERFORMANCE).direct3_d11_device
        # TODO: Unknown potential error, I don't have an older Win10 machine to test.
        except BaseException:  # noqa: S110,BLE001
            pass
    if not direct_3d_device:
        raise OSError("Unable to initialize a Direct3D Device.")
    return direct_3d_device


def try_get_direct3d_device():
    try:
        return get_direct3d_device()
    except OSError:
        return None


def try_input_device_access():
    """Same as `make_uinput` in `keyboard/_nixcommon.py`."""
    if sys.platform != "linux":
        return False
    try:
        UI_SET_EVBIT = 0x40045564  # noqa: N806
        with open("/dev/uinput", "wb") as uinput:
            fcntl.ioctl(uinput, UI_SET_EVBIT)
    except OSError:
        return False
    return True


def fire_and_forget(func: Callable[..., Any]):
    """
    Runs synchronous function asynchronously without waiting for a response.

    Uses threads on Windows because ~~`RuntimeError: There is no current event loop in thread 'MainThread'.`~~
    Because maybe asyncio has issues. Unsure. See alpha.5 and https://github.com/Avasam/AutoSplit/issues/36

    Uses asyncio on Linux because of a `Segmentation fault (core dumped)`
    """
    def wrapped(*args: Any, **kwargs: Any):
        if sys.platform == "win32":
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return get_or_create_eventloop().run_in_executor(None, func, *args, *kwargs)

    return wrapped


# Environment specifics
WINDOWS_BUILD_NUMBER = int(version().split(".")[-1]) if sys.platform == "win32" else -1
FIRST_WIN_11_BUILD = 22000
"""AutoSplit Version number"""
WGC_MIN_BUILD = 17134
"""https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to"""
FROZEN = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
"""The directory of either the AutoSplit executable or AutoSplit.py"""
IS_WAYLAND = bool(os.environ.get("WAYLAND_DISPLAY", False))

# Shared strings
# Check `excludeBuildNumber` during workflow dispatch build generate a clean version number
AUTOSPLIT_VERSION = "2.0.0-beta.3" + (f"-{AUTOSPLIT_BUILD_NUMBER}" if AUTOSPLIT_BUILD_NUMBER else "")
GITHUB_REPOSITORY = AUTOSPLIT_GITHUB_REPOSITORY
