import collections
import typing

from listful.types import GETTER, ITEM, VALUE


class Index(typing.Generic[ITEM, VALUE]):
    # pylint: disable=unused-argument
    def add(self, element: ITEM, value: VALUE) -> None:
        ...  # pragma: nocover

    # pylint: disable=unused-argument
    def remove(self, element: ITEM, value: VALUE) -> None:
        ...  # pragma: nocover

    # pylint: disable=unused-argument
    def get(self, value: VALUE) -> typing.List[ITEM]:
        ...  # pragma: nocover


class SimpleIndex(Index[ITEM, VALUE]):
    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self._index: typing.Dict[
            VALUE, typing.List[ITEM]
        ] = collections.defaultdict(list)

    def add(self, element: ITEM, value: VALUE) -> None:
        self._index[value].append(element)

    def remove(self, element: ITEM, value: VALUE) -> None:
        self._index[value].remove(element)

    def get(self, value: VALUE) -> typing.List[ITEM]:
        return self._index[value]


class NaiveIndex(Index[ITEM, VALUE]):
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        getter: GETTER[ITEM, VALUE],
        field: str,
        elements: typing.List[ITEM],
    ) -> None:
        self._field = field
        self._getter = getter
        self._elements = elements

    # pylint: disable=unused-argument
    def add(self, element: ITEM, value: VALUE) -> None:
        self._elements.append(element)

    # pylint: disable=unused-argument
    def remove(self, element: ITEM, value: VALUE) -> None:
        self._elements.remove(element)

    def get(self, value: VALUE) -> typing.List[ITEM]:
        return [
            element
            for element in self._elements
            if self._getter(element, self._field) == value
        ]
