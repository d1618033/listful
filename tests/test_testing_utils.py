from listful._internal.testing_utils import Item


def test_item_equality() -> None:
    assert Item(x=1, y=2) == Item(x=1, y=2)
    assert Item(x=1, y=2) != Item(x=5, y=2)
    assert Item(x=1, y=2) != 17
