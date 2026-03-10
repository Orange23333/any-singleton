from .singletons import (
    singleton, singleton_value, singleton_instance,
    once, run_once, SecondCallingBehaviour,
    SealedObject,
    CannotCallingMoreThanOnceError,
    is_singleton_exists,
    get_cached_return
)

singleton = singleton
singleton_value = singleton_value
singleton_instance = singleton_instance

once = once
run_once = run_once

SecondCallingBehaviour = SecondCallingBehaviour

SealedObject = SealedObject

CannotCallingMoreThanOnceError = CannotCallingMoreThanOnceError

is_singleton_exists = is_singleton_exists

get_cached_return = get_cached_return
