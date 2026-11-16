from unittest.mock import Mock

import pytest

from shop.cart import Cart


# Тести додавання та кількості
def test_cart_initial_is_empty(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0
    assert empty_cart.total() == 0.0


def test_add_single_item(empty_cart: Cart) -> None:
    empty_cart.add("Apple", 10.0, 2)
    assert empty_cart.items_count() == 2
    assert empty_cart.total() == 20.0


def test_add_multiple_different_items(empty_cart: Cart) -> None:
    empty_cart.add("Apple", 10.0, 1)
    empty_cart.add("Banana", 15.5, 2)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 41.0


def test_add_existing_item_accumulates_qty(empty_cart: Cart) -> None:
    empty_cart.add("Apple", 10.0, 2)
    empty_cart.add("Apple", 10.0, 3)
    assert empty_cart.items_count() == 5
    assert empty_cart.total() == 50.0


# Тести видалення товарів
def test_remove_item(empty_cart: Cart) -> None:
    empty_cart.add("Apple", 10.0, 2)
    empty_cart.remove("Apple")
    assert empty_cart.items_count() == 0
    assert empty_cart.total() == 0.0


def test_remove_non_existent_item_raises_key_error(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("GhostItem")


# Перевірка винятків для валідації вхідних даних
@pytest.mark.parametrize(
    "name, price, qty, expected_exception",
    [
        ("BadPrice", -5.0, 1, ValueError),  # від'ємна ціна
        ("BadQty", 10.0, 0, ValueError),  # нульова кількість
        ("BadQtyNeg", 10.0, -2, ValueError),  # від'ємна кількість
    ],
)
def test_add_invalid_parameters_raises_value_error(
    empty_cart: Cart, name: str, price: float, qty: int, expected_exception: type[Exception]
) -> None:
    with pytest.raises(expected_exception):
        empty_cart.add(name, price, qty)


# Параметризований тест з граничними значеннями знижок (одна з технік тест дизайну)
@pytest.mark.parametrize(
    "discount, expected_total",
    [
        (0.0, 100.0),
        (50.0, 50.0),
        (100.0, 0.0),
    ],
)
def test_total_with_boundary_discounts(
    empty_cart: Cart, discount: float, expected_total: float
) -> None:
    empty_cart.add("Item", 100.0, 1)
    assert empty_cart.total(discount) == expected_total


@pytest.mark.parametrize(
    "invalid_discount",
    [-0.1, 100.1, 150.0],
)
def test_invalid_discount_raises_value_error(empty_cart: Cart, invalid_discount: float) -> None:
    empty_cart.add("Item", 50.0, 1)
    with pytest.raises(ValueError):
        empty_cart.total(invalid_discount)


# Тест методу total_in з тестовим дублером
def test_total_in_with_mock_rate_provider(empty_cart: Cart) -> None:
    empty_cart.add("Item", 100.0, 1)

    rate_provider = Mock()
    rate_provider.get_rate.return_value = 25.0

    result = empty_cart.total_in("USD", rate_provider)
    assert result == 4.0
    rate_provider.get_rate.assert_called_once_with("USD")


def test_total_in_with_invalid_rate_raises_value_error(empty_cart: Cart) -> None:
    empty_cart.add("Item", 50.0, 1)
    rate_provider = Mock()
    rate_provider.get_rate.return_value = 0.0

    with pytest.raises(ValueError):
        empty_cart.total_in("XXX", rate_provider)


# Тест на поведінку при додаванні товару з однаковою назвою, але іншою ціною
def test_add_same_name_different_price_updates_qty_keeps_original_price(empty_cart: Cart) -> None:
    empty_cart.add("Book", 100.0, 1)
    empty_cart.add("Book", 150.0, 2)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 100.0 * 3


# Для нового методу most_expensive()
def test_most_expensive_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_single_item(empty_cart: Cart) -> None:
    empty_cart.add("Pen", 15.0, 3)
    result = empty_cart.most_expensive()
    assert result is not None
    assert result.name == "Pen"
    assert result.price == 15.0


def test_most_expensive_multiple_items(empty_cart: Cart) -> None:
    empty_cart.add("Pen", 10.0, 5)
    empty_cart.add("Laptop", 25000.0, 1)
    empty_cart.add("Notebook", 50.0, 2)

    result = empty_cart.most_expensive()
    assert result is not None
    assert result.name == "Laptop"
    assert result.price == 25000.0
