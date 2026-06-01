"""QR code (quishing) analyzer."""
from .url_analyzer import analyze as analyze_url

def decode_image(file_bytes: bytes):
    try:
        import cv2, numpy as np
        from pyzbar.pyzbar import decode
        arr = np.frombuffer(file_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return [d.data.decode("utf-8", "ignore") for d in decode(img)]
    except Exception as e:
        return [f"__error__:{e}"]

def analyze(file_bytes: bytes):
    payloads = decode_image(file_bytes)
    results = []
    for p in payloads:
        if p.startswith("__error__:"):
            results.append({"payload": p, "score": 0, "reasons": ["Decode error"]})
        elif p.lower().startswith(("http://","https://")):
            results.append({"payload": p, **analyze_url(p)})
        else:
            results.append({"payload": p, "score": 5, "reasons": ["Non-URL payload"]})
    return results
