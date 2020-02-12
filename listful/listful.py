import collections
import operator
import typing

from listful.exceptions import (
    ListfulsMismatchException,
    MoreThanOneResultException,
    NotFoundException,
)
from listful.utils import intersect_lists

T = typing.TypeVar('T')


class Results(typing.Generic[T]):
    def __init__(
        self,
        results: typing.Sequence[T],
        filter_: typing.Dict[str, typing.Any],
        source: 'Listful[T]',
    ):
        self._source = source
        self._filter = filter_
        self._results = results

    def one_or_none(self) -> typing.Optional[T]:
        if len(self._results) == 1:
            return next(iter(self._results))
        return None

    def one_or_raise(self) -> T:
        results = self._results
        if len(results) == 1:
            return next(iter(results))
        if len(results) > 1:
            raise MoreThanOneResultException(
                f'Found more than one result for filter {self._filter}: {results}'
            )
        raise NotFoundException(
            f'Found zero results for filter {self._filter}'
        )

    def to_list(self) -> typing.List[T]:
        return list(self._results)

    def to_listful(self) -> 'Listful[T]':
        return Listful(self._results, self._source.fields)


class Listful(typing.List[T]):
    def __init__(
        self,
        iterable: typing.Iterable[T],
        fields: typing.List[str],
        getter: typing.Optional[typing.Callable[[T, str], typing.Any]] = None,
    ):
        super().__init__(iterable)
        self.fields = fields
        if getter is None:
            # pylint: disable=unsubscriptable-object
            if len(self) > 0 and isinstance(self[0], dict):
                getter = typing.cast(
                    typing.Callable[[T, str], typing.Any], operator.getitem
                )
            else:
                getter = getattr
        self.getter: typing.Callable[[T, str], typing.Any] = getter
        self._indexes: typing.Dict[
            str, typing.Dict[typing.Any, typing.List[T]]
        ] = {}
        self._build_indexes()

    def _build_indexes(self) -> None:
        self._indexes = {}
        for field in self.fields:
            index = self._indexes[field] = collections.defaultdict(list)
            for element in self:  # pylint: disable=not-an-iterable
                value = self.getter(element, field)
                index[value].append(element)

    def filter(self, **kwargs: typing.Any) -> Results[T]:
        results = None
        for field, value in kwargs.items():
            if field in self._indexes:
                new_results = self._indexes[field][value]
            else:
                new_results = [
                    element
                    for element in self  # pylint: disable=not-an-iterable
                    if self.getter(element, field) == value
                ]
            if results is None:
                results = new_results
            else:
                results = intersect_lists(results, new_results)
        if results is None:
            results = self
        return Results(results, filter_=kwargs, source=self)

    def get_all_for_field(self, field: str) -> typing.List[T]:
        return [
            self.getter(element, field)
            for element in self  # pylint: disable=not-an-iterable
        ]

    def rebuild_indexes_for_item(self, item: T) -> None:
        for field in self.fields:
            value = self.getter(item, field)
            self._indexes[field][value].append(item)

    def append(self, item: T) -> None:
        super().append(item)  # pylint: disable=no-member
        self.rebuild_indexes_for_item(item)

    def _remove_item_from_indexes(self, item: T) -> None:
        for field in self.fields:
            value = self.getter(item, field)
            self._indexes[field][value].remove(item)

    def remove(self, item: T) -> None:
        super().remove(item)  # pylint: disable=no-member
        self._remove_item_from_indexes(item)

    @typing.overload
    def __setitem__(self, index: int, item: T) -> None:
        ...  # pragma: nocover

    @typing.overload
    def __setitem__(self, index: slice, item: typing.Iterable[T]) -> None:
        ...  # pragma: nocover

    def __setitem__(
        self,
        index: typing.Union[int, slice],
        item: typing.Union[T, typing.Iterable[T]],
    ) -> None:
        self._remove_indexes_from_multiple_items(index)
        if isinstance(index, slice):
            items = typing.cast(typing.Iterable[T], item)
            super().__setitem__(  # pylint: disable=no-member
                typing.cast(slice, index), items
            )
            for item_ in items:
                self.rebuild_indexes_for_item(item_)
        else:
            item = typing.cast(T, item)
            super().__setitem__(  # pylint: disable=no-member
                typing.cast(int, index), item
            )
            self.rebuild_indexes_for_item(item)

    def __delitem__(self, index: typing.Union[int, slice]) -> None:
        self._remove_indexes_from_multiple_items(index)
        super().__delitem__(index)  # pylint: disable=no-member

    def _remove_indexes_from_multiple_items(
        self, index: typing.Union[int, slice]
    ) -> None:
        item = self[index]  # pylint: disable=unsubscriptable-object
        if isinstance(index, slice):
            items = typing.cast(typing.Iterable[T], item)
            for item_ in items:
                self._remove_item_from_indexes(item_)
        else:
            item = typing.cast(T, item)
            self._remove_item_from_indexes(item)

    def extend(self, iterable: typing.Iterable[T]) -> None:
        for element in iterable:
            self.append(element)

    @classmethod
    def from_listfuls(
        cls, listfuls: typing.Iterable['Listful[T]']
    ) -> 'Listful[T]':
        listfuls_iterator = iter(listfuls)
        try:
            result = next(listfuls_iterator)
        except StopIteration:
            raise ValueError('Expected at least one listful object')
        fields = set(result.fields)
        getter = result.getter
        for listful_obj in listfuls_iterator:
            if set(listful_obj.fields) != fields:
                raise ListfulsMismatchException(
                    f"Can't merge listfuls with different indexes {listful_obj.fields} != {fields}"
                )
            if listful_obj.getter != getter:
                raise ListfulsMismatchException(
                    f"Can't merge listfuls with different getters {listful_obj.getter} != {getter}"
                )
            result.extend(listful_obj)
        return result
