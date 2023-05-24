"""Paginator page size calculation."""


def get_page_size(
    page: int,
    total: int,
    size_default: int,
    next: str | None
) -> int:
    """Return the size (amount of elements) of a page.

    """

    if total >= size_default:
        if next:
            return size_default
        else:
            return total - size_default * (page - 1)
    return total
