import numpy as np
from app.detection import detect_check_regions

def test_detector_rejects_invalid_image():
    try:
        detect_check_regions(np.zeros((0, 0, 3), dtype=np.uint8))
    except ValueError:
        return
    raise AssertionError('Expected ValueError')
