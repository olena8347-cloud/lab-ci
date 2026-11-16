import pytest

from shop.cart import Cart


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()
