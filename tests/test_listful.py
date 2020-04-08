import typing

import pytest

from listful import Listful, MoreThanOneResultException, NotFoundException
from listful._internal.testing_utils import Item
from listful.exceptions import ListfulsMismatchException

BasicListful = Listful[typing.Dict[str, int], int]
ObjectListful = Listful[Item, int]


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
    object_custom_getter_listful: ObjectListful,
) -> None:
    assert object_custom_getter_listful.filter(x=3, y=4).one_or_none() == Item(
        x=3, y=4
    )


def test_filter_non_indexed_field() -> None:
    items = BasicListful([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}], fields=['x'])
    assert items.filter(y=2).one_or_none() == {'x': 1, 'y': 2}
    assert items.get_all_for_field('y') == [2, 4]


def test_filter_non_indexed_field_add_del() -> None:
    items = BasicListful([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}], fields=['x'])
    assert items.filter(y=2).one_or_none() == {'x': 1, 'y': 2}
    del items[0]
    assert items.filter(y=2).one_or_none() is None
    items[0] = {'x': 3, 'y': 2}
    assert items.filter(y=2).one_or_none() == {'x': 3, 'y': 2}


def test_get_all_for_field(basic_listful: BasicListful) -> None:
    assert basic_listful.get_all_for_field('x') == [1, 3, 3]


def test_get_all_for_field_after_seitem(basic_listful: BasicListful) -> None:
    basic_listful[1] = {'x': 2, 'y': 17}
    assert basic_listful.get_all_for_field('x') == [1, 2, 3]


def test_extend(basic_listful: BasicListful) -> None:
    basic_listful.extend(
        Listful([{'x': 10, 'y': 20}, {'x': 20, 'y': 40}], fields=['x', 'y'])
    )
    assert basic_listful.filter(x=10).one_or_raise() == {'x': 10, 'y': 20}


def test_to_listful(basic_listful: BasicListful) -> None:
    assert basic_listful.filter(x=3).to_listful().filter(
        y=4
    ).one_or_none() == {'x': 3, 'y': 4}


def test_from_listfuls(basic_listful: BasicListful) -> None:
    items = Listful.from_listfuls(
        [basic_listful, BasicListful([{'x': 17, 'y': 17}], fields=['x', 'y'])]
    )
    assert items.filter(x=17).one_or_none() == {'x': 17, 'y': 17}
    assert items.filter(x=1).one_or_none() == {'x': 1, 'y': 2}


def test_from_listfuls_mismatch_indexes(basic_listful: BasicListful) -> None:
    with pytest.raises(ListfulsMismatchException):
        Listful.from_listfuls(
            [basic_listful, BasicListful([{'x': 17, 'y': 17}], fields=['y'])]
        )


def test_from_listfuls_mismatch_getter(basic_listful: BasicListful) -> None:
    with pytest.raises(ListfulsMismatchException):
        Listful.from_listfuls(
            [  # type: ignore
                basic_listful,
                ObjectListful([Item(x=17, y=17)], fields=['x', 'y']),
            ]
        )


def test_from_listfuls_empty() -> None:
    with pytest.raises(
        ValueError, match='Expected at least one listful object'
    ):
        Listful.from_listfuls([])


def test_no_fields_supplied_and_no_data() -> None:
    with pytest.raises(
        ValueError, match='fields is required when iterable is empty'
    ):
        Listful([])


def test_no_fields_supplied_and_data_has_dict() -> None:
    listful: Listful[typing.Dict[str, typing.Any], typing.Any] = Listful(
        [{'a': 1, 'b': [5, 7]}]
    )
    assert listful.fields == ['a']


def test_no_fields_supplied_and_data_has_object() -> None:
    listful: Listful[Item, int] = Listful([Item(x=1, y=2)])
    assert listful.fields == ['x', 'y']
