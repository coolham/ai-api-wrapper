from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')


def safe_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get a value from a nested dictionary."""
    if not data or not isinstance(data, dict):
        return default

    keys = path.split('.')
    result = data
    try:
        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return default
        return result
    except (KeyError, TypeError):
        return default 