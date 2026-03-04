<div align="center">
    <h1>Any-singleton</h1>
</div>

---

# Installation

```shell
python -m pip install any-singleton
```

# Documentation

## Usage

### Create a singleton

> Register a singleton with a value:
```python
from any_singleton import singleton

tea = singleton('my_project.main.coffee', 'tea')
```

Instantiate an object and register as a singleton:
```python
from any_singleton import singleton

my_range = singleton('my_project.main.coffee', range, 123)
```

For disambiguating, you can use `singleton_value()` to instead `singleton()` when the value is a `type`:
```python
from any_singleton import singleton_value

class Tea:
    pass

tea = singleton_value('my_project.main.coffee', type(Tea))
```

### Make a function can only be called once in global

Using `@once` to create a function that can only be called once in global.

```python
import tomllib
from any_singleton import once, singleton

@once('my_project.initializations.init')
def init(config_path: str) -> None:
    with open(config_path, 'rb') as f:
        config = singleton('my_project.globals.config', tomllib.load(f))

init('config.toml')
```

Or just using `@run_once` to create a function as same as decorated with `@once` and calling it immediately.

```python
import tomllib
from any_singleton import run_once, singleton

@run_once('my_project.initializations.init', 'config.toml')
def init(config_path: str) -> None:
    with open(config_path, 'rb') as f:
        config = singleton('my_project.globals.config', tomllib.load(f))
```

# ATTENTION

- `any-singleton` will **OCCUPY** the global variable `_any_singleton`, see `any_singleton.singletons.GLOBAL_KEY`.
- **DO NOT** use `@cached_return` as a domain name. It's a **RESERVED** word.

---

View this source code on [GitHub](https://github.com/Orange23333/any-singleton).
