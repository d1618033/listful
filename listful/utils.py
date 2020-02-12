import typing

T = typing.TypeVar('T')


def intersect_lists(
    list1: typing.Iterable[T], list2: typing.Iterable[T]
) -> typing.Iterable[T]:
    return [element for element in list1 if element in list2]
