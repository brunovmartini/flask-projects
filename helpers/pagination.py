import math
from typing import Any, List

from werkzeug.exceptions import BadRequest

from resources.response.pagination_response import PaginatedResponse, PaginationMeta


def validate_pagination(request: dict[str, Any]) -> tuple[int, int] | None:
    try:
        page = int(request.get('page', 1))
        page_size = int(request.get('page_size', 10))
    except (ValueError, TypeError):
        raise BadRequest('Invalid pagination parameters. Value of page and page_size must be integers.')

    if page < 1:
        raise BadRequest('Value of page must be greater than 0')
    if page_size < 1 or page_size > 100:
        raise BadRequest('Value of page_size must be between 1 and 100')

    return page, page_size


def create_pagination_response(items: List[dict[str, Any]], total: int, page: int, page_size: int):
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    ).model_dump()
