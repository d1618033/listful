import typing

T = typing.TypeVar('T')
V = typing.TypeVar('V')
F = typing.TypeVar('F')


def intersect_lists(
    list1: typing.Iterable[T], list2: typing.Iterable[T]
) -> typing.Iterable[T]:
    return [element for element in list1 if element in list2]


def naive_find_elements_in_list(
    elements: typing.List[T],
    field: F,
    value: V,
    getter: typing.Callable[[T, F], V],
) -> typing.List[T]:
    return [element for element in elements if getter(element, field) == value]
