from app.models import VisionExtraction


def extract_check(image) -> VisionExtraction:
    from app.ollama_provider import extract_with_ollama
    return extract_with_ollama(image)
