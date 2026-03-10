from enum import Enum
from functools import wraps
from types import NoneType
from typing import Any, Callable, overload


class SealedObject:
    def __init__(self, value: Any = None) -> None:
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


def is_singleton_exists(dn: str) -> bool:
    """
    Returns whether the singleton object with the given domain name exists.

    :param dn: The unique domain name of the singleton object.
    :return: whether the singleton object exists.
    """

    return dn in _g


def _add_singleton(dn: str, value: Any) -> None:
    _g[dn] = SingletonInfo(dn, value)


def _get_singleton(dn: str) -> Any:
    return _g[dn].instance


def _get_return_dn(func_dn: str) -> str:
    return func_dn + RETURN_POSTFIX


def _remove_singleton(dn: str) -> None:
    return_dn = _get_return_dn(dn)
    if return_dn in _g:
        del _g[return_dn]
    del _g[dn]


def singleton_value(dn: str, value: Any) -> Any:
    """
    Creating a singleton with given value.

    ATTENTION
    If you directly give a non-referenced type value, this function will not seal the value.
    It means that the singleton object will not be changed outside.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param value: The default value of the singleton.
    :return: The singleton instance.
    """

    if dn not in _g:
        _add_singleton(dn, value)

        return value
    else:
        return _get_singleton(dn)


def singleton_instance(dn: str, t: type, *args, **kwargs) -> Any:
    """
    Creating an instance as singleton.

    ATTENTION
    If you directly create an instance of a non-referenced type, this function will not seal the instance.
    It means that the singleton object will not be changed outside.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param t: The type of instance to be created.
    :param args: The arguments to be passed to initialize an instance of given type.
    :param kwargs: The keyword arguments to initialize an instance of given type.
    :return: The singleton instance.
    """

    if dn not in _g:
        instance = t(*args, **kwargs)

        _add_singleton(dn, instance)

        return instance
    else:
        return _get_singleton(dn)


_nonreferenced_types = singleton_value(
    'any_singleton.nonreferenced_types',
    (bool, int, float, str, NoneType)
)


def _is_nonreferenced(obj: Any) -> bool:
    return isinstance(obj, _nonreferenced_types)  # or (obj is type and issubclass(obj, _nonreferenced_types))


@overload
def singleton(dn: str, value: bool | int | float | str | None) -> SealedObject:
    """
    Creating a singleton with given value.
    The function will automatically seal the value into a SealedObject.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param value: The default value of the singleton.
    :return: The singleton instance.
    """
    pass


@overload
def singleton(dn: str, value: Any) -> Any:
    """
    Creating a singleton with given value.

    ATTENTION
    If you directly give a non-referenced type value,
    and it isn't a bool, int, float or str,
    this function will not seal the value.
    It means that the singleton object will not be changed outside.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param value: The default value of the singleton.
    :return: The singleton instance.
    """
    pass


@overload
def singleton(dn: str, t: type, *args, **kwargs) -> Any:
    """
    Creating an instance as singleton.

    :param dn: The unique domain name for the instance.
               It could be like "project.module.variable".
    :param t: The type of instance to be created.
    :param args: The arguments to be passed to initialize an instance of given type.
    :param kwargs: The keyword arguments to initialize an instance of given type.
    :return: The singleton instance.
    """
    pass


def singleton(dn: str, x: Any, *args, **kwargs):
    is_type = isinstance(x, type)

    if not is_type and (len(args) > 0 or len(kwargs) > 0):
        raise ValueError('Too many arguments.')

    if dn not in _g:
        if is_type:
            t = x
            v = t(*args, **kwargs)
        else:
            v = x

        if _is_nonreferenced(v):
            v = SealedObject(v)

        _add_singleton(dn, v)

        ret = v
    else:
        ret = _get_singleton(dn)

    return ret


class CannotCallingMoreThanOnceError(Exception):
    pass


class SecondCallingBehaviour(Enum):
    """
    The behavior when the function is called more than once.
    """

    """
    Returns the result of the first calling.
    """
    CacheReturn = 'c'

    """
    Raises a `CannotCallingMoreThanOnceError`.
    """
    RaiseError = 'e'

    """
    Returns `None` without cache.
    """
    NoneToReturn = None


def _add_cached_return(dn: str, value: Any) -> Any:
    return singleton_value(_get_return_dn(dn), value)


def get_cached_return(dn: str) -> Any:
    """
    Get the cached return value of a function decorated with `@once`.

    By the way, If its `second_calling` isn't `SecondCallingBehaviour.RaiseError`,
    you can call the function once again to get the cached return value.

    :param dn: The unique domain name of the function.
               It will not be sealed as SealedObject automatically.
    :return: The cached return value.
    """

    return _get_singleton(_get_return_dn(dn))


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

    return_dn = _get_return_dn(dn)

    def decorator(f: Callable) -> Callable:
        """
        A decorator to ensure that the function is only called once.
        :param f: The function to be decorated.
        :return: Decorated function.
        """

        if dn in _g:
            wrapper = _get_singleton(dn)

            return wrapper
        else:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Any:
                """
                :return: The return value or cached value of the function.
                         It will not be sealed as SealedObject automatically.
                :except CannotCallingMoreThanOnceError: If the second_calling set with SecondCallingBehaviour.CacheReturn,
                                                        when the function is called more than once,
                                                        it will raise CannotCallingMoreThanOnceError.
                """

                if return_dn not in _g:
                    ret = f(*args, **kwargs)

                    if second_calling == SecondCallingBehaviour.CacheReturn:
                        _add_cached_return(dn, ret)
                    else:
                        _add_cached_return(dn, None)

                    return ret

                match second_calling:
                    case SecondCallingBehaviour.CacheReturn:
                        return get_cached_return(dn)
                    case SecondCallingBehaviour.RaiseError:
                        raise CannotCallingMoreThanOnceError(f'"{dn}" has already been called.')
                    case SecondCallingBehaviour.NoneToReturn:
                        return None
                    case _:
                        raise ValueError(f'Unknown "{SecondCallingBehaviour.__name__}".')

            _add_singleton(dn, wrapper)

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
