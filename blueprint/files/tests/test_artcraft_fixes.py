"""Regression tests for the artcraft research tool defects found by subagent S2."""
from types import SimpleNamespace

import numpy as np

from tools.artcraft import deblur_and_restore


def test_deblur_restore_handles_lab_lightness_range() -> None:
    rgb = np.zeros((32, 32, 3), dtype=np.uint8)
    rgb[8:24, 8:24] = (40, 90, 60)
    alpha = np.zeros((32, 32), dtype=np.uint8)
    alpha[8:24, 8:24] = 255
    args = SimpleNamespace(deblur_iterations=0, deblur_sigma=1.0, clahe=0.02, saturation=1.1)
    out = deblur_and_restore(rgb, alpha, args)
    assert out.shape == rgb.shape
    assert out.dtype == np.uint8
    assert out[0, 0].tolist() == [0, 0, 0]