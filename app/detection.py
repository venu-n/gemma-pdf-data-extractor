from dataclasses import dataclass
import cv2
import numpy as np

@dataclass(frozen=True)
class CheckRegion:
    x: int
    y: int
    width: int
    height: int
    confidence: float

def detect_check_regions(image: np.ndarray) -> list[CheckRegion]:
    if image is None or image.size == 0:
        raise ValueError('Invalid page image')
    if image.ndim == 3:
        if image.shape[2] != 3:
            raise ValueError('Expected RGB image with 3 channels')
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    elif image.ndim == 2:
        gray = image
    else:
        raise ValueError('Expected grayscale or RGB image')
    height, width = gray.shape
    candidates = []
    non_white = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (31, 31))
    closed = cv2.morphologyEx(non_white, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates.extend(_candidate_boxes(contours, width, height))
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edge_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 9))
    edge_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, edge_kernel, iterations=2)
    contours, _ = cv2.findContours(edge_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates.extend(_candidate_boxes(contours, width, height))
    return sorted(_remove_contained(_deduplicate(candidates)), key=lambda r: (r.y, r.x))

def _candidate_boxes(contours, page_width, page_height):
    page_area = page_width * page_height
    results = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w <= 0 or h <= 0:
            continue
        area = w * h
        aspect_ratio = w / h
        relative_area = area / page_area
        if not (1.2 <= aspect_ratio <= 6.0 and 0.01 <= relative_area <= 0.70 and
                w >= page_width * 0.20 and h >= page_height * 0.05 and
                w <= page_width * 0.95 and h <= page_height * 0.80):
            continue
        aspect_score = 1.0 - min(abs(aspect_ratio - 2.5) / 3.0, 1.0)
        size_score = min(relative_area / 0.15, 1.0)
        confidence = round(0.5 * aspect_score + 0.5 * size_score, 3)
        results.append(CheckRegion(x, y, w, h, confidence))
    return results

def _deduplicate(regions):
    selected = []
    for region in sorted(regions, key=lambda r: r.confidence, reverse=True):
        if all(_iou(region, existing) < 0.50 for existing in selected):
            selected.append(region)
    return selected

def _remove_contained(regions):
    kept = []
    for region in sorted(regions, key=lambda r: r.width * r.height, reverse=True):
        region_area = region.width * region.height
        if any(larger.x <= region.x and larger.y <= region.y and
               larger.x + larger.width >= region.x + region.width and
               larger.y + larger.height >= region.y + region.height and
               region_area <= larger.width * larger.height * 0.70 for larger in kept):
            continue
        kept.append(region)
    return kept

def _iou(first, second):
    x1, y1 = max(first.x, second.x), max(first.y, second.y)
    x2, y2 = min(first.x + first.width, second.x + second.width), min(first.y + first.height, second.y + second.height)
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    if intersection == 0:
        return 0.0
    union = first.width * first.height + second.width * second.height - intersection
    return intersection / union
