from . import by_page, by_section

_REGISTRY = {
    "by_page": by_page.chunk,
    "by_section": by_section.chunk,
}


def get_chunker(name: str):
    if name not in _REGISTRY:
        raise ValueError(f"Unknown chunker: {name!r}. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]
