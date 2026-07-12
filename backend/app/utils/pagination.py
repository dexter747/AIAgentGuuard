"""
Cursor-based pagination utilities for efficient large dataset navigation.
Replaces offset-based pagination to avoid performance issues with large tables.
"""
from typing import Optional, List, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc
import base64
import json


T = TypeVar('T')


class CursorPage(BaseModel, Generic[T]):
    """Paginated response with cursor navigation."""
    items: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_count: Optional[int] = None


def encode_cursor(cursor_data: dict) -> str:
    """Encode cursor data to base64 string."""
    json_str = json.dumps(cursor_data, default=str)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> dict:
    """Decode base64 cursor to dict."""
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        return json.loads(json_str)
    except Exception:
        return {}


def paginate_cursor(
    query: Query,
    cursor: Optional[str] = None,
    limit: int = 50,
    order_by_column = None,
    order_desc: bool = True,
    cursor_column_name: str = 'created_at',
    include_total: bool = False
) -> CursorPage:
    """
    Apply cursor-based pagination to SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query to paginate
        cursor: Base64-encoded cursor from previous page
        limit: Number of items per page (max 100)
        order_by_column: Column to order by (defaults to created_at)
        order_desc: Sort descending (True) or ascending (False)
        cursor_column_name: Name of the cursor column in results
        include_total: Whether to include total count (expensive)
    
    Returns:
        CursorPage with items and navigation cursor
    
    Example:
        query = db.query(Trace).filter(Trace.agent_id == agent_id)
        page = paginate_cursor(
            query,
            cursor=request_cursor,
            limit=50,
            order_by_column=Trace.created_at,
            order_desc=True
        )
    """
    # Limit pagination size
    limit = min(limit, 100)
    
    # Default order column
    if order_by_column is None:
        # Try to get created_at from model
        model = query.column_descriptions[0]['type']
        order_by_column = getattr(model, 'created_at', None)
        if order_by_column is None:
            raise ValueError("order_by_column must be specified")
    
    # Apply ordering
    if order_desc:
        query = query.order_by(desc(order_by_column))
    else:
        query = query.order_by(asc(order_by_column))
    
    # Apply cursor filter if provided
    if cursor:
        cursor_data = decode_cursor(cursor)
        if cursor_data and cursor_column_name in cursor_data:
            cursor_value = cursor_data[cursor_column_name]
            
            if order_desc:
                query = query.filter(order_by_column < cursor_value)
            else:
                query = query.filter(order_by_column > cursor_value)
    
    # Fetch limit + 1 to check if there are more results
    items = query.limit(limit + 1).all()
    
    # Check if there are more results
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
    
    # Generate next cursor from last item
    next_cursor = None
    if has_more and items:
        last_item = items[-1]
        cursor_value = getattr(last_item, cursor_column_name.split('.')[-1], None)
        if cursor_value:
            next_cursor = encode_cursor({cursor_column_name: cursor_value})
    
    # Optionally get total count (expensive, avoid if possible)
    total_count = None
    if include_total:
        # Remove ordering and limits for count
        count_query = query.order_by(None).limit(None).offset(None)
        total_count = count_query.count()
    
    return CursorPage(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more,
        total_count=total_count
    )


def paginate_list(
    items: List[T],
    cursor: Optional[str] = None,
    limit: int = 50,
    get_cursor_value = None
) -> CursorPage[T]:
    """
    Paginate an in-memory list with cursor.
    Useful for paginating pre-fetched or computed data.
    
    Args:
        items: List of items to paginate (must be pre-sorted)
        cursor: Cursor from previous page
        limit: Items per page
        get_cursor_value: Function to extract cursor value from item
    """
    limit = min(limit, 100)
    
    # Find start index from cursor
    start_idx = 0
    if cursor and get_cursor_value:
        cursor_data = decode_cursor(cursor)
        if 'value' in cursor_data:
            cursor_value = cursor_data['value']
            # Find first item after cursor
            for idx, item in enumerate(items):
                if get_cursor_value(item) <= cursor_value:
                    start_idx = idx + 1
                else:
                    break
    
    # Slice items
    end_idx = start_idx + limit
    page_items = items[start_idx:end_idx]
    has_more = end_idx < len(items)
    
    # Generate next cursor
    next_cursor = None
    if has_more and page_items and get_cursor_value:
        last_value = get_cursor_value(page_items[-1])
        next_cursor = encode_cursor({'value': last_value})
    
    return CursorPage(
        items=page_items,
        next_cursor=next_cursor,
        has_more=has_more,
        total_count=len(items)
    )
