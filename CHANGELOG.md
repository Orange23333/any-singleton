# any-singleton v1.1.0 (2026 Mar 10th)
- Fix `__init__.py`.
- Fix `singleton_instance()`.
- Fix automatic sealing in `singleton()` for created instance.
- Fix `@once`.
- Add `_nonreferenced_types`, fixing `None` to `NoneType`.
- Rename `Package` to `SealedObject`.
- `singleton()` will automatically seal the value of `bool`, `int`, `float`, `str` and `None` into `SealedObject`, and `singleton_value()` and `singleton_instance()` will not do it anymore.
- Give the parameter `value` of `__init__()` of `SealedObject` a default value of `None`.
- Add `_get_return_dn()`.
- Add more APIs to `__init__.py`.
- Add `pytest` for testing.
- Add `ruff` for formating.

# any-singleton v1.0.1 (2026 Mar 5th)
- Add more APIs to `__init__.py`.
- Remove unused `TVar`.

# any-singleton v1.0.0 (2026 Mar 5th)
- Add `singleton`, `singleton_value`, `singleton_instance` for creating a singleton.
- Add `@once`, `@run_once` for creating a function can be called only once.
