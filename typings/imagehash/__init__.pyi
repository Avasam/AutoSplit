""" # noqa: Y021
This type stub file was generated by pyright.
"""
from __future__ import absolute_import, annotations, division, print_function

from PIL import Image

__version__: str


class ImageHash:
    def __init__(self, binary_array) -> None:
        ...

    def __sub__(self, other: ImageHash) -> int:
        ...

    def __eq__(self, other: ImageHash) -> bool:
        ...

    def __ne__(self, other: ImageHash) -> bool:
        ...

    def __hash__(self) -> int:
        ...

    def __len__(self) -> int:
        ...


def hex_to_hash(hexstr) -> ImageHash:
    ...


def hex_to_flathash(hexstr, hashsize) -> ImageHash:
    ...


def old_hex_to_hash(hexstr, hash_size=...) -> ImageHash:
    ...


def average_hash(image, hash_size=..., mean=...) -> ImageHash:
    ...


def phash(image: Image.Image, hash_size: int = ..., highfreq_factor: int = ...) -> ImageHash:
    ...


def phash_simple(image, hash_size=..., highfreq_factor=...) -> ImageHash:
    ...


def dhash(image, hash_size=...) -> ImageHash:
    ...


def dhash_vertical(image, hash_size=...) -> ImageHash:
    ...


def whash(image, hash_size=..., image_scale=..., mode=..., remove_max_haar_ll=...) -> ImageHash:
    ...


def colorhash(image, binbits=...) -> ImageHash:
    ...


class ImageMultiHash:
    def __init__(self, hashes) -> None:
        ...

    def __eq__(self, other) -> bool:
        ...

    def __ne__(self, other) -> bool:
        ...

    def __sub__(self, other, hamming_cutoff=..., bit_error_rate=...) -> int | float:
        ...

    def __hash__(self) -> int:
        ...

    def hash_diff(self, other_hash, hamming_cutoff=..., bit_error_rate=...) -> tuple[int, int]:
        ...

    def matches(self, other_hash, region_cutoff=..., hamming_cutoff=..., bit_error_rate=...):
        ...

    def best_match(self, other_hashes, hamming_cutoff=..., bit_error_rate=...):
        ...


def crop_resistant_hash(
        image,
        hash_func=...,
        limit_segments=...,
        segment_threshold=...,
        min_segment_size=...,
        segmentation_image_size=...) -> ImageMultiHash:
    ...
