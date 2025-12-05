import uuid

def create_slug(title: str) -> str:
    slug = title.lower().replace(' ', '-')[:100] + '-' + str(uuid.uuid4())[:12]
    return slug