"""  # noqa: Y021
This type stub file was generated by pyright.
"""


import ctypes
from typing import Literal, Optional

#


class Display:
    name: str
    adapter_name: str
    resolution: tuple[int, int]
    position: dict[Literal["left", "top", "right", "bottom"], int]
    rotation: int
    scale_factor: int
    is_primary: bool
    hmonitor: int
    dxgi_output: Optional = ...
    dxgi_adapter: Optional = ...
    d3d_device: Optional = ...
    d3d_device_context: Optional = ...
    dxgi_output_duplication: ctypes.pointer

    def __init__(
            self,
            name=...,
            adapter_name=...,
            resolution=...,
            position=...,
            rotation=...,
            scale_factor=...,
            is_primary=...,
            hmonitor=...,
            dxgi_output=...,
            dxgi_adapter=...) -> None:
        ...

    def capture(self, process_func, region=...) -> None:
        ...

    @classmethod
    def discover_displays(cls) -> list:
        ...
