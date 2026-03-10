from types import NoneType

import pytest

from src.any_singleton.singletons import (
    SealedObject, SingletonInfo,
    GLOBAL_KEY, RETURN_POSTFIX,
    is_singleton_exists,
    _add_singleton, _get_singleton, _get_return_dn, _remove_singleton,
    singleton_value, singleton_instance,
    _nonreferenced_types, _is_nonreferenced,
    singleton,
    CannotCallingMoreThanOnceError,
    SecondCallingBehaviour,
    _add_cached_return, get_cached_return,
    once, run_once
)
from tests.fixtures.clean_up import reset_global_singletons as reset


class Cup:
    def __init__(self, content: str) -> None:
        self.content = content


#region === is_singleton_exists ===

def test_is_singleton_exists():
    dn = 'any_singleton.tests.test_is_singleton_exists.singleton_obj'

    assert not is_singleton_exists(dn)
    _add_singleton(dn, 'tea')
    assert is_singleton_exists(dn)

    _remove_singleton(dn)
    assert not is_singleton_exists(dn)

#endregion


#region === is_singleton_exists ===

def test_reset():
    dn = 'any_singleton.tests.test_singletons.singleton_obj'

    assert not is_singleton_exists(dn)
    singleton(dn, 'tea')
    assert is_singleton_exists(dn)

    reset()
    assert not is_singleton_exists(dn)

#endregion


#region === any_singleton.singletons.(_(add|get|remove)_singleton|_get_return_dn) ===

def test_agr_singleton():  # agr - add, get, remove
    dn = 'any_singleton.tests.test_agr_singleton.singleton_obj'

    assert not is_singleton_exists(dn)
    instance = Cup('tea')
    _add_singleton(dn, instance)
    assert is_singleton_exists(dn)

    singleton_obj = _get_singleton(dn)
    assert not isinstance(singleton_obj, SealedObject)
    assert singleton_obj.content == 'tea'
    assert singleton_obj is instance

    instance.content = 'milk'
    assert singleton_obj.content == 'milk'

    return_dn = _get_return_dn(dn)
    assert return_dn == dn + RETURN_POSTFIX

    singleton(return_dn, 'TEA')
    assert is_singleton_exists(return_dn)

    _remove_singleton(dn)
    assert not is_singleton_exists(dn)
    assert not is_singleton_exists(return_dn)

#endregion


#region === any_singleton.singletons.singleton_value ===

def test_singleton_value():
    same_dn = 'any_singleton.tests.test_singleton_value.singleton_obj'

    singleton_obj1 = singleton_value(same_dn, 'tea')
    singleton_obj2 = singleton_value(same_dn, 'coffee')
    assert isinstance(singleton_obj1, str)
    assert singleton_obj1 == 'tea'
    assert singleton_obj2 == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2 = 'milk'
    assert singleton_obj1 == 'tea'

    reset()

    singleton_obj1 = singleton_value(same_dn, Cup('tea'))
    singleton_obj2 = singleton_value(same_dn, Cup('coffee'))
    assert isinstance(singleton_obj1, Cup)
    assert singleton_obj1.content == 'tea'
    assert singleton_obj2.content == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2.content = 'milk'
    assert singleton_obj1.content == 'milk'
    singleton_obj2 = Cup('juice')
    assert singleton_obj1.content == 'milk'

#endregion


#region === any_singleton.singletons.singleton_instance ===

def test_singleton_instance():
    same_dn = 'any_singleton.tests.test_singleton_instance.singleton_obj'

    singleton_obj1 = singleton_instance(same_dn, str, 'tea')
    singleton_obj2 = singleton_instance(same_dn, str, 'coffee')
    assert isinstance(singleton_obj1, str)
    assert singleton_obj1 == 'tea'
    assert singleton_obj2 == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2 = 'milk'
    assert singleton_obj1 == 'tea'

    reset()

    singleton_obj1 = singleton_instance(same_dn, Cup, 'tea')
    singleton_obj2 = singleton_instance(same_dn, Cup, 'coffee')
    assert isinstance(singleton_obj1, Cup)
    assert singleton_obj1.content == 'tea'
    assert singleton_obj2.content == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2.content = 'milk'
    assert singleton_obj1.content == 'milk'
    singleton_obj2 = Cup('juice')
    assert singleton_obj1.content == 'milk'

#endregion


#region === any_singleton.singletons.singleton ===

def test_singleton__auto_sealing():
    dn = 'any_singleton.tests.test_singleton__auto_sealing.singleton_obj'

    for t in _nonreferenced_types:
        singleton_obj = singleton(dn, t())
        assert isinstance(singleton_obj, SealedObject)
        reset()

        if t is not NoneType:
            singleton_obj = singleton(dn, t, t())
            assert isinstance(singleton_obj, SealedObject)
            reset()

    other_types = (
        list, dict
    )
    for t in other_types:
        if t in _nonreferenced_types:
            raise ValueError(
                f'`{other_types.__name__}` contains a type that is in `{_nonreferenced_types.__name__}`.'
            )
    for t in other_types:
        singleton_obj = singleton(dn, t())
        assert not isinstance(singleton_obj, SealedObject)
        reset()

        singleton_obj = singleton(dn, t, t())
        assert not isinstance(singleton_obj, SealedObject)
        reset()

    singleton_obj = singleton(dn, SealedObject('tea'))
    assert not isinstance(singleton_obj.value, SealedObject)
    reset()

    singleton_obj = singleton(dn, SealedObject, 'tea')
    assert not isinstance(singleton_obj.value, SealedObject)
    reset()


def test_singleton__with_nonreferenced_object():
    same_dn = 'any_singleton.tests.test_singleton__with_nonreferenced_object.singleton_obj'

    singleton_obj1 = singleton(same_dn, 'tea')
    singleton_obj2 = singleton(same_dn, 'coffee')
    assert isinstance(singleton_obj1, SealedObject)
    assert singleton_obj1.value == 'tea'
    assert singleton_obj2.value == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2.value = 'milk'
    assert singleton_obj1.value == 'milk'

    reset()

    singleton_obj1 = singleton(same_dn, str, 'tea')
    singleton_obj2 = singleton(same_dn, str, 'coffee')
    assert isinstance(singleton_obj1, SealedObject)
    assert singleton_obj1.value == 'tea'
    assert singleton_obj2.value == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2.value = 'milk'
    assert singleton_obj1.value == 'milk'


def test_singleton__with_referenced_object():
    same_dn = 'any_singleton.tests.test_singleton__with_referenced_object.singleton_obj'

    singleton_obj1 = singleton(same_dn, Cup('tea'))
    singleton_obj2 = singleton(same_dn, Cup('coffee'))
    assert singleton_obj1.content == 'tea'
    assert singleton_obj2.content == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2.content = 'milk'
    assert singleton_obj1.content == 'milk'

    reset()

    singleton_obj1 = singleton(same_dn, Cup, 'tea')
    singleton_obj2 = singleton(same_dn, Cup, 'coffee')
    assert singleton_obj1.content == 'tea'
    assert singleton_obj2.content == 'tea'
    assert singleton_obj1 is singleton_obj2

    singleton_obj2.content = 'milk'
    assert singleton_obj1.content == 'milk'


def test_singleton__errors():
    dn = 'any_singleton.tests.test_singleton__errors.singleton_obj'

    with pytest.raises(ValueError, match='Too many arguments.'):
        singleton(dn, 'coffee', 'more_coffee')
    with pytest.raises(ValueError, match='Too many arguments.'):
        singleton(dn, 'coffee', more='coffee')

#endregion


#region === any_singleton.singletons.(_add|get)_cached_return ===

def test_ag_cached_return():  # ag - add, get
    dn = 'any_singleton.tests.test_ag_cached_return.singleton_obj'

    return_dn = _get_return_dn(dn)
    assert return_dn == dn + RETURN_POSTFIX

    assert not is_singleton_exists(return_dn)
    instance = Cup('tea')
    _add_cached_return(dn, instance)
    assert is_singleton_exists(return_dn)

    singleton_obj = get_cached_return(dn)
    assert isinstance(singleton_obj, Cup)
    assert singleton_obj.content == 'tea'
    assert singleton_obj is instance

    instance.content = 'milk'
    assert singleton_obj.content == 'milk'

#endregion


#region === any_singleton.singletons.once ===

def test_once__cache_return():
    dn = 'any_singleton.tests.test_once__cache_return.once_func'
    return_dn = _get_return_dn(dn)

    call_count = 0

    @once(dn, second_calling=SecondCallingBehaviour.CacheReturn)
    def serve_tea(cup: SealedObject, tea: str = 'tea') -> SealedObject:
        nonlocal call_count

        call_count += 1

        cup.value = tea
        return cup

    assert is_singleton_exists(dn)
    assert not is_singleton_exists(return_dn)

    wrapper = _get_singleton(dn)

    @once(dn)
    def f():
        pass

    assert _get_singleton(dn) is wrapper

    my_cup = SealedObject('empty')

    result1 = serve_tea(my_cup, tea='black_tea')
    assert call_count == 1
    assert is_singleton_exists(return_dn)
    assert result1 is my_cup

    result2 = get_cached_return(dn)
    assert result2 is result1

    result3 = serve_tea(my_cup, tea='green_tea')
    assert call_count == 1
    assert result3 is result1

    reset()
    call_count = 0

    @once(dn, second_calling=SecondCallingBehaviour.CacheReturn)
    def serve_tea(cup: SealedObject, tea: str = 'tea') -> str:
        nonlocal call_count

        call_count += 1

        cup.value = tea
        return cup.value

    assert is_singleton_exists(dn)
    assert not is_singleton_exists(return_dn)

    wrapper = _get_singleton(dn)

    @once(dn)
    def f():
        pass

    assert _get_singleton(dn) is wrapper

    my_cup = SealedObject('empty')

    result1 = serve_tea(my_cup, tea='black_tea')
    assert call_count == 1
    assert isinstance(result1, str)
    assert is_singleton_exists(return_dn)
    assert result1 == 'black_tea'
    assert my_cup.value == 'black_tea'

    result2 = get_cached_return(dn)
    assert result2 == 'black_tea'

    my_cup.value = 'empty'
    result3 = serve_tea(my_cup, tea='green_tea')
    assert call_count == 1
    assert result3 == 'black_tea'


def test_once__raise_error():
    dn = 'any_singleton.tests.test_once__raise_error.once_func'
    return_dn = _get_return_dn(dn)

    call_count = 0

    @once(dn, second_calling=SecondCallingBehaviour.RaiseError)
    def serve_tea(cup: SealedObject, tea: str = 'tea') -> SealedObject:
        nonlocal call_count

        call_count += 1

        cup.value = tea
        return cup

    assert is_singleton_exists(dn)
    assert not is_singleton_exists(return_dn)

    wrapper = _get_singleton(dn)

    @once(dn)
    def f():
        pass

    assert _get_singleton(dn) is wrapper

    my_cup = SealedObject('empty')

    result1 = serve_tea(my_cup, tea='black_tea')
    assert call_count == 1
    assert is_singleton_exists(return_dn)
    assert result1 is my_cup

    result2 = get_cached_return(dn)
    assert result2 is None

    with pytest.raises(CannotCallingMoreThanOnceError):
        serve_tea(my_cup, tea='green_tea')
    assert call_count == 1


def test_once__none_to_return():
    dn = 'any_singleton.tests.test_once__none_to_return.once_func'
    return_dn = _get_return_dn(dn)

    call_count = 0

    @once(dn, second_calling=SecondCallingBehaviour.NoneToReturn)
    def serve_tea(cup: SealedObject, tea: str = 'tea') -> SealedObject:
        nonlocal call_count

        call_count += 1

        cup.value = tea
        return cup

    assert is_singleton_exists(dn)
    assert not is_singleton_exists(return_dn)

    wrapper = _get_singleton(dn)

    @once(dn)
    def f():
        pass

    assert _get_singleton(dn) is wrapper

    my_cup = SealedObject('empty')

    result1 = serve_tea(my_cup, tea='black_tea')
    assert call_count == 1
    assert is_singleton_exists(return_dn)
    assert result1 is my_cup

    result2 = get_cached_return(dn)
    assert result2 is None

    result3 = serve_tea(my_cup, tea='green_tea')
    assert call_count == 1
    assert my_cup.value == 'black_tea'
    assert result3 is None

#endregion


#region === any_singleton.singletons.run_once ===

def test_run_once():
    dn = 'any_singleton.tests.test_run_once.once_func'
    return_dn = _get_return_dn(dn)

    call_count = 0

    my_cup = SealedObject('empty')

    @run_once(
        dn, my_cup,
        second_calling=SecondCallingBehaviour.NoneToReturn,
        tea='black_tea'
    )
    def serve_tea(cup: SealedObject, tea: str = 'tea') -> SealedObject:
        nonlocal call_count

        call_count += 1

        cup.value = tea
        return cup

    assert is_singleton_exists(dn)
    assert is_singleton_exists(return_dn)
    assert call_count == 1
    assert my_cup.value == 'black_tea'

    wrapper = _get_singleton(dn)

    @run_once(dn)
    def f():
        pass

    assert _get_singleton(dn) is wrapper

    serve_tea(my_cup, tea='green_tea')
    assert call_count == 1
    assert my_cup.value == 'black_tea'

#endregion
