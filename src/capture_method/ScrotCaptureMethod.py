from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np
import pyscreeze

from capture_method.interface import ThreadedCaptureMethod
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class ScrotCaptureMethod(ThreadedCaptureMethod):
    def _read_action(self, autosplit: AutoSplit):
        selection = autosplit.settings_dict["capture_region"]
        image = pyscreeze.screenshot(
            None,
            (selection["x"], selection["y"], selection["width"], selection["height"]))
        return np.array(image)

    def get_frame(self, autosplit: AutoSplit):
        image, is_old_image = super().get_frame(autosplit)
        if not is_valid_image(image):
            return None, is_old_image
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA), is_old_image

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit) -> bool:
        raise NotImplementedError()

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return True
