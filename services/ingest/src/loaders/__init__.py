from .pdf import load_pdf_pages

_REGISTRY = {
    "pdf": load_pdf_pages,
}


def get_loader(name: str):
    if name not in _REGISTRY:
        raise ValueError(f"Unknown loader: {name!r}. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]
