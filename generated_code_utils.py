import uuid
def generate_unique_satznummer():
    return str(uuid.uuid4())[:8]