import typing

import pytest

from listful import Listful
from listful._internal.testing_utils import Item


@pytest.fixture()
def basic_listful() -> Listful[typing.Dict[str, int], int]:
    return Listful(
        [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}, {'x': 3, 'y': 5}],
        fields=['x', 'y'],
    )


@pytest.fixture()
def object_listful() -> Listful[Item, int]:
    return Listful(
        list(
            map(
                lambda d: Item(**d),
                [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}, {'x': 3, 'y': 5}],
            )
        ),
        fields=['x', 'y'],
    )


@pytest.fixture()
def object_custom_getter_listful() -> Listful[Item, int]:
    return Listful(
        list(
            map(
                lambda d: Item(**d),
                [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}, {'x': 3, 'y': 5}],
            )
        ),
        fields=['x', 'y'],
        getter=getattr,
    )
