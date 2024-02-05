from typing import Type, TypeVar



def ignore_errors(cb: Type, fallback) -> Type:
    T = TypeVar('T')
    try:
        return cb()
    except Exception as e:
        print("error " + e)
        return fallback
