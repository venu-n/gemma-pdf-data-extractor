import numpy as np

from app.detection import detect_check_regions


def test_blank_page_has_no_check_regions():
    image = np.full((1000, 1500, 3), 255, dtype=np.uint8)

    regions = detect_check_regions(image)

    assert regions == []


def test_small_noise_does_not_create_check_region():
    image = np.full((1000, 1500, 3), 255, dtype=np.uint8)

    # Small dark mark, much smaller than a check.
    image[100:120, 100:130] = 0

    regions = detect_check_regions(image)

    assert regions == []


def test_detect_check_shaped_region():
    image = np.full((1000, 1500, 3), 255, dtype=np.uint8)

    # Synthetic check-like rectangle.
    image[250:650, 200:1300] = 0
    image[270:630, 220:1280] = 255

    regions = detect_check_regions(image)

    assert len(regions) >= 1