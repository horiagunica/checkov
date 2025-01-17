from __future__ import annotations

import logging
from typing import Any, TypeVar

_T = TypeVar("_T")


def get_inner_dict(source_dict: dict[str, Any], path_as_list: list[str]) -> dict[str, Any]:
    result = source_dict
    for index in path_as_list:
        try:
            result = result[index]
        except KeyError:
            # for getting the source context for resources with for_each name - index can be "resource_name[0]"
            for k in result:
                if index.startswith(k):
                    result = result[k]
    return result


def merge_dicts(*dicts: dict[_T, Any]) -> dict[_T, Any]:
    """
    Merges two or more dicts. If there are duplicate keys, later dict arguments take precedence.

    Null, empty, or non-dict arguments are qiuetly skipped.
    :param dicts:
    :return:
    """
    res: dict[Any, Any] = {}
    for d in dicts:
        if not d or not isinstance(d, dict):
            continue
        res = {**res, **d}
    return res


def search_deep_keys(
    search_text: str, obj: dict[str, Any] | list[dict[str, Any]] | None, path: list[int | str]
) -> list[list[int | str]]:
    """Search deep for keys and get their values"""
    keys: list[list[int | str]] = []
    if isinstance(obj, dict):
        for key in obj:
            pathprop = path[:]
            pathprop.append(key)
            if key == search_text:
                pathprop.append(obj[key])
                keys.append(pathprop)
                # pop the last element off for nesting of found elements for
                # dict and list checks
                pathprop = pathprop[:-1]
            if isinstance(obj[key], dict):
                if key != 'parent_metadata':
                    # Don't go back to the parent metadata, it is scanned for the parent
                    keys.extend(search_deep_keys(search_text, obj[key], pathprop))
            elif isinstance(obj[key], list):
                for index, item in enumerate(obj[key]):
                    pathproparr = pathprop[:]
                    pathproparr.append(index)
                    keys.extend(search_deep_keys(search_text, item, pathproparr))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            pathprop = path[:]
            pathprop.append(index)
            keys.extend(search_deep_keys(search_text, item, pathprop))

    return keys


def find_in_dict(input_dict: dict[str, Any], key_path: str) -> Any:
    """Tries to retrieve the value under the given 'key_path', otherwise returns None."""

    value: Any = input_dict
    key_list = key_path.split("/")

    try:
        for key in key_list:
            if key.startswith("[") and key.endswith("]"):
                if isinstance(value, list):
                    idx = int(key[1:-1])
                    value = value[idx]
                    continue
                else:
                    return None

            value = value.get(key)
            if value is None:
                return None
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        logging.debug(f"Could not find {key_path} in dict")
        return None

    return value


def get_empty_list_str() -> list[str]:
    """Returns an empty list with type 'list[str]'

    This is needed for using empty lists with a list union type hint
    ex.
        foo: list[str] | list[int] = []

    more info can be found here https://github.com/python/mypy/issues/6463
    """

    return []
