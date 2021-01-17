import operator
import typing

from listful import MoreThanOneResultException, NotFoundException
from listful.exceptions import ListfulsMismatchException
from listful.index import Index, SimpleIndex
from listful.types import FIELD, GETTER, ITEM, VALUE
from listful.utils import intersect_lists, naive_find_elements_in_list


class Listful(typing.List[ITEM], typing.Generic[ITEM, VALUE]):
    def __init__(
        self,
        iterable: typing.Iterable[ITEM],
        fields: typing.Optional[typing.List[FIELD]] = None,
        getter: typing.Optional[GETTER[ITEM, VALUE]] = None,
    ):
        super().__init__(iterable)
        if getter is None:
            # pylint: disable=unsubscriptable-object
            if len(self) > 0 and isinstance(self[0], dict):
                getter = typing.cast(GETTER[ITEM, VALUE], operator.getitem)
            else:
                getter = getattr
        self.getter: GETTER[ITEM, VALUE] = getter
        if fields is None:
            if len(self) == 0:
                raise ValueError('fields is required when iterable is empty')
            first_item = self[0]  # pylint: disable=unsubscriptable-object
            if isinstance(first_item, dict):
                potential_fields = first_item
            else:
                potential_fields = vars(first_item)
            fields = sorted(
                field
                for field, value in potential_fields.items()
                if hasattr(value, '__hash__') and value.__hash__ is not None
            )
        self.fields = fields
        self._indexes: typing.Dict[FIELD, Index[ITEM, VALUE]] = {}
        self._build_indexes()

    def _build_indexes(self) -> None:
        self._indexes = {}
        for field in self.fields:
            index = self._indexes[field] = SimpleIndex()
            for element in self:  # pylint: disable=not-an-iterable
                value = self.getter(element, field)
                index.add(element, value)

    def filter(self, **kwargs: typing.Any) -> 'Results[ITEM, VALUE]':
        results = None
        for field, value in kwargs.items():
            if field in self._indexes:
                new_results = self._indexes[field].get(value)
            else:
                new_results = naive_find_elements_in_list(
                    self, field, value, self.getter
                )
            if results is None:
                results = new_results
            else:
                results = intersect_lists(results, new_results)
        if results is None:
            results = self
        return Results(results, filter_=kwargs, source=self)

    def get_all_for_field(self, field: FIELD) -> typing.List[VALUE]:
        return [
            self.getter(element, field)
            for element in self  # pylint: disable=not-an-iterable
        ]

    def rebuild_indexes_for_item(self, item: ITEM) -> None:
        for field in self.fields:
            value = self.getter(item, field)
            self._indexes[field].add(item, value)

    def append(self, item: ITEM) -> None:
        super().append(item)  # pylint: disable=no-member
        self.rebuild_indexes_for_item(item)

    def _remove_item_from_indexes(self, item: ITEM) -> None:
        for field in self.fields:
            value = self.getter(item, field)
            self._indexes[field].remove(item, value)

    def remove(self, item: ITEM) -> None:
        super().remove(item)  # pylint: disable=no-member
        self._remove_item_from_indexes(item)

    @typing.overload
    def __setitem__(self, index: int, item: ITEM) -> None:
        ...  # pragma: nocover

    @typing.overload
    def __setitem__(self, index: slice, item: typing.Iterable[ITEM]) -> None:
        ...  # pragma: nocover

    def __setitem__(
        self,
        index: typing.Union[int, slice],
        item: typing.Union[ITEM, typing.Iterable[ITEM]],
    ) -> None:
        self._remove_indexes_from_multiple_items(index)
        if isinstance(index, slice):
            items = typing.cast(typing.Iterable[ITEM], item)
            super().__setitem__(  # pylint: disable=no-member
                typing.cast(slice, index), items
            )
            for item_ in items:
                self.rebuild_indexes_for_item(item_)
        else:
            item = typing.cast(ITEM, item)
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
            items = typing.cast(typing.Iterable[ITEM], item)
            for item_ in items:
                self._remove_item_from_indexes(item_)
        else:
            item = typing.cast(ITEM, item)
            self._remove_item_from_indexes(item)

    def extend(self, iterable: typing.Iterable[ITEM]) -> None:
        for element in iterable:
            self.append(element)

    @classmethod
    def from_listfuls(
        cls, listfuls: typing.Iterable['Listful[ITEM, VALUE]']
    ) -> 'Listful[ITEM, VALUE]':
        listfuls_iterator = iter(listfuls)
        try:
            result = next(listfuls_iterator)
        except StopIteration as e:
            raise ValueError('Expected at least one listful object') from e
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


class Results(typing.Generic[ITEM, VALUE]):
    def __init__(
        self,
        results: typing.Sequence[ITEM],
        filter_: typing.Dict[FIELD, VALUE],
        source: 'Listful[ITEM, VALUE]',
    ):
        self._source = source
        self._filter = filter_
        self._results = results

    def one_or_none(self) -> typing.Optional[ITEM]:
        if len(self._results) == 1:
            return next(iter(self._results))
        return None

    def one_or_raise(self) -> ITEM:
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

    def to_list(self) -> typing.List[ITEM]:
        return list(self._results)

    def to_listful(self) -> 'Listful[ITEM, VALUE]':
        return Listful(self._results, self._source.fields)
