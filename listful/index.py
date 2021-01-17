import collections
import typing

from listful.types import ITEM, VALUE


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
        elements = self._index[value]
        if element not in elements:
            elements.append(element)

    def remove(self, element: ITEM, value: VALUE) -> None:
        self._index[value].remove(element)

    def get(self, value: VALUE) -> typing.List[ITEM]:
        return self._index[value]
