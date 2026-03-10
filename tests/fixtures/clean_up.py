import pytest

import src.any_singleton.singletons as sgt

def reset_global_singletons() -> None:
    sgt._g.clear()


@pytest.fixture(autouse=True)
def auto_reset_global_singletons():
    yield

    reset_global_singletons()
