from enum import Enum
from functools import wraps
from typing import Any, Callable, overload, TypeVar

TVar = TypeVar('TVar')


class Package:
    def __init__(self, value: Any) -> None:
        self.__value = value

    @property
    def value(self) -> Any:
        return self.__value

    @value.setter
    def value(self, value: Any) -> None:
        self.__value = value


class SingletonInfo:
    def __init__(self, dn: str, instance: Any) -> None:
        self.__dn: str = dn
        self.__instance: Any = instance

    @property
    def dn(self) -> str:
        return self.__dn

    @property
    def instance(self) -> Any:
        return self.__instance


GLOBAL_KEY = '_any_singleton'  # `any-singleton` will use this name to save all the global declarations.
if GLOBAL_KEY not in globals():
    globals()[GLOBAL_KEY] = {}
_g: dict[str, SingletonInfo] = globals()[GLOBAL_KEY]

RETURN_POSTFIX = '.@cached_return'


def is_exists(dn: str) -> bool:
    """
    Returns whether the singleton object with the given domain name exists.

    :param dn: The unique domain name of the singleton object.
    :return: whether the singleton object exists.
    """

    return dn in _g


def _is_nonreferenced(obj: Any) -> bool:
    known_nonreferenced_types = (
        bool, int, float, str
    )
    return isinstance(obj, known_nonreferenced_types)


def _add_singleton(dn: str, value: Any) -> None:
    if _is_nonreferenced(value):
        obj = Package(value)
    else:
        obj = value

    _g[dn] = SingletonInfo(dn, obj)


def _get_singleton(dn: str) -> Any:
    return _g[dn].instance


def _remove_singleton(dn: str) -> None:
    return_dn = dn + RETURN_POSTFIX
    if return_dn in _g:
        del _g[return_dn]
    del _g[dn]


def singleton_value(dn: str, value: Any) -> Any:
    """
    Used for creating a singleton.

    ATTENTION
    If you give a non-referenced type value, this function will not seal the value.
    It means that the value can be changed outside.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param value: The value in a Non-referenced type to be stored in the singleton.
    :return: The singleton instance.
    """

    if dn not in _g:
        _add_singleton(dn, value)

        return value
    else:
        return _get_singleton(dn)


def singleton_instance(dn: str, t: type, *args, **kwargs) -> Any:
    """
    Used for creating a singleton of referenced types.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.function".
    :param t: The type of referenced type.
    :param args: The arguments to be passed to initialize an instance of given type.
    :param kwargs: The keyword arguments to initialize an instance of given type.
    """

    if dn not in _g:
        instance = t(*args, **kwargs)

        _add_singleton(dn, isinstance)

        return instance
    else:
        return _get_singleton(dn)


@overload
def singleton(dn: str, value: Any) -> Any:
    """
    Used for creating a singleton of non-referenced types (like int, float, str, etc.).

    Although it available for giving a value of referenced type, it is not recommended.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param value: The value in a Non-referenced type to be stored in the singleton.
    :return: The singleton instance.
    """
    pass


@overload
def singleton(dn: str, t: type, *args, **kwargs) -> Any:
    """
    Used for creating a singleton of referenced types.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.function".
    :param t: The type of referenced type.
    :param args: The arguments to be passed to initialize an instance of given type.
    :param kwargs: The keyword arguments to initialize an instance of given type.
    """
    pass


def singleton(dn: str, x: Any, *args, **kwargs):
    is_type = isinstance(x, type)

    if not is_type and (len(args) > 0 or len(kwargs) > 0):
        raise ValueError('Too many arguments.')

    if is_type:
        return singleton_instance(dn, x, *args, **kwargs)
    else:
        return singleton_value(dn, x)


class CannotCallingMoreThanOnceError(Exception):
    pass


class SecondCallingBehaviour(Enum):
    """
    Returns the result of the first calling.
    """
    CacheReturn = 'c'

    """
    Raises a `CannotCallingMoreThanOnceError`.
    """
    RaiseError = 'e'

    """
    Returns `None`.
    """
    NoneToReturn = None


def _add_cached_return(dn: str, value: Any) -> None:
    """
    Set the cached return value of a function decorated with `@once`.

    :param dn: The unique domain name of the function.
    :param value: The value to be cached.
    """

    singleton_value(dn + RETURN_POSTFIX, value)


def get_cached_return(dn: str) -> Any:
    """
    Get the cached return value of a function decorated with `@once`.

    :param dn: The unique domain name of the function.
    :return: The cached return value.
    """

    return _get_singleton(dn + RETURN_POSTFIX)


def once(
        dn: str,
        second_calling: SecondCallingBehaviour = SecondCallingBehaviour.CacheReturn
) -> Callable:
    """
    Returns a decorator for functions to ensure that the function is only called once.

    :param dn: The unique domain name for the function.
               It could be like "project.module.function".
    :param second_calling: The behavior when the function is called more than once.
    :return: The decorator.
    """

    def decorator(f: Callable) -> Callable:
        """
        A decorator to ensure that the function is only called once.
        :param f: The function to be decorated.
        :return: Decorated function.
        """

        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            if dn not in _g:
                _add_singleton(dn, f)

                ret = f(*args, **kwargs)

                if second_calling == SecondCallingBehaviour.CacheReturn:
                    _add_cached_return(dn, ret)

                return ret

            match second_calling:
                case SecondCallingBehaviour.CacheReturn:
                    return get_cached_return(dn)
                case SecondCallingBehaviour.RaiseError:
                    raise RuntimeError(f'"{dn}" has already been called.')
                case SecondCallingBehaviour.NoneToReturn:
                    return None
                case _:
                    raise ValueError(f'Unknown "{SecondCallingBehaviour.__name__}".')

        return wrapper

    return decorator


def run_once(
        dn: str,
        *args,
        second_calling: SecondCallingBehaviour = SecondCallingBehaviour.CacheReturn,
        **kwargs
) -> Callable:
    """
    Returns a decorator for functions to ensure that the function is only called once and
    call once immediately if the function has not been called before.

    By the way, the function will be decorated with `@once`.

    :param dn: The unique domain name for the function.
               It could be like "project.module.function".
    :param args: The arguments to be passed to the function.
    :param second_calling: The behavior when the function is called more than once.
    :param kwargs: The keyword arguments to be passed to the function.
    :return: The decorator.
    """

    def decorator(f) -> Callable:
        wrapper = once(dn, second_calling=second_calling)(f)

        wrapper(*args, **kwargs)

        return wrapper

    return decorator
