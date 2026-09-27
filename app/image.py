import cv2
import numpy as np
from app.detection import CheckRegion

def crop_check(page_image: np.ndarray, region: CheckRegion, padding: int = 10) -> np.ndarray:
    if page_image is None or page_image.size == 0:
        raise ValueError('Invalid page image')
    height, width = page_image.shape[:2]
    x1, y1 = max(region.x - padding, 0), max(region.y - padding, 0)
    x2, y2 = min(region.x + region.width + padding, width), min(region.y + region.height + padding, height)
    if x1 >= x2 or y1 >= y2:
        raise ValueError('Invalid check crop coordinates')
    return page_image[y1:y2, x1:x2].copy()

def prepare_gemma_image(image: np.ndarray, max_dimension: int = 1600) -> np.ndarray:
    if image is None or image.size == 0:
        raise ValueError('Invalid check image')
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('Gemma image must be RGB')
    height, width = image.shape[:2]
    largest = max(height, width)
    if largest <= max_dimension:
        return image.copy()
    scale = max_dimension / largest
    return cv2.resize(image, (max(1, int(round(width * scale))), max(1, int(round(height * scale)))), interpolation=cv2.INTER_AREA)
