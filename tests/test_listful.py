import typing

import pytest

from listful import Listful, MoreThanOneResultException, NotFoundException
from listful._internal.testing_utils import Item

BasicListful = Listful[typing.Dict[str, int]]
ObjectListful = Listful[Item]


def test_filter_one_or_none(basic_listful: BasicListful) -> None:
    assert basic_listful.filter(x=1).one_or_none() == {'x': 1, 'y': 2}
    assert basic_listful.filter(y=4).one_or_none() == {'x': 3, 'y': 4}
    assert basic_listful.filter(y=17).one_or_none() is None


def test_filter_multiple_returned(basic_listful: BasicListful) -> None:
    assert basic_listful.filter(x=3).to_list() == [
        {'x': 3, 'y': 4},
        {'x': 3, 'y': 5},
    ]


def test_filter_multiple_fields_in_filter(basic_listful: BasicListful) -> None:
    assert basic_listful.filter(x=3, y=4).one_or_none() == {'x': 3, 'y': 4}
    assert basic_listful.filter(x=3, y=17).one_or_none() is None


def test_one_or_raises(basic_listful: BasicListful) -> None:
    with pytest.raises(NotFoundException):
        assert basic_listful.filter(x=3, y=17).one_or_raise()
    with pytest.raises(MoreThanOneResultException):
        assert basic_listful.filter(x=3).one_or_raise()
    assert basic_listful.filter(x=3, y=4).one_or_raise() == {'x': 3, 'y': 4}


def test_filter_no_kwargs(basic_listful: BasicListful) -> None:
    assert basic_listful.filter().to_list() == list(basic_listful)


def test_append(basic_listful: BasicListful) -> None:
    item = {'x': 3, 'y': 17}
    basic_listful.append(item)
    assert basic_listful.filter(x=3, y=17).one_or_none() == item


def test_set_item(basic_listful: BasicListful) -> None:
    item = {'x': 3, 'y': 17}
    basic_listful[2] = item
    assert basic_listful.filter(x=3).to_list() == [
        {'x': 3, 'y': 4},
        {'x': 3, 'y': 17},
    ]


def test_set_item_slice(basic_listful: BasicListful) -> None:
    items = [{'x': 3, 'y': 17}, {'x': 3, 'y': 18}]
    basic_listful[1:3] = items
    assert basic_listful.filter(x=3).to_list() == [
        {'x': 3, 'y': 17},
        {'x': 3, 'y': 18},
    ]


def test_remove(basic_listful: BasicListful) -> None:
    basic_listful.remove({'x': 3, 'y': 5})
    assert basic_listful.filter(x=3).one_or_none() == {'x': 3, 'y': 4}


def test_del(basic_listful: BasicListful) -> None:
    del basic_listful[2]
    assert basic_listful.filter(x=3).one_or_none() == {'x': 3, 'y': 4}


def test_del_slice(basic_listful: BasicListful) -> None:
    del basic_listful[1:3]
    assert basic_listful.filter(x=3).one_or_none() is None


def test_object_listful(object_listful: ObjectListful) -> None:
    object_listful.remove(Item(x=3, y=5))
    assert object_listful.filter(x=3).one_or_none() == Item(x=3, y=4)


def test_object_listful_custom_getter(
    object_custom_getter_listful: ObjectListful
) -> None:
    assert object_custom_getter_listful.filter(x=3, y=4).one_or_none() == Item(
        x=3, y=4
    )
