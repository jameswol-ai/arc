import hashlib
import time

def generate_share_code(concept_id, prefix="ARC"):
    raw = f"{concept_id}-{time.time()}"
    hash_obj = hashlib.md5(raw.encode())
    code = hash_obj.hexdigest()[:6].upper()
    return f"{prefix}-{code}"

def create_share_link(concept, base_url="https://your-app.streamlit.app"):
    share_code = generate_share_code(concept["id"])
    return f"{base_url}?share={share_code}"