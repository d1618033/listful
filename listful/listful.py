import collections
import typing

from listful.exceptions import MoreThanOneResultException, ZeroResultsException

T = typing.TypeVar('T')


class Results(typing.Generic[T]):
    def __init__(
        self,
        results: typing.Sequence[T],
        filter_: typing.Dict[str, typing.Any],
    ):
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
        raise ZeroResultsException(
            f'Found zero results for filter {self._filter}'
        )

    def to_list(self) -> typing.List[T]:
        return list(self._results)


class Listful(typing.List[T]):
    def __init__(
        self,
        iterable: typing.Iterable[T],
        fields: typing.List[str],
        getter: typing.Optional[typing.Callable[[T, str], typing.Any]] = None,
    ):
        super().__init__(iterable)
        self._fields = fields
        if getter is None:
            if len(self) > 0 and isinstance(self[0], dict):
                getter = dict.__getitem__
            else:
                getter = getattr
        self._getter: typing.Callable[[T, str], typing.Any] = getter
        self._indexes: typing.Dict[
            str, typing.Dict[typing.Any, typing.List[T]]
        ] = {}
        self._build_indexes()

    def _build_indexes(self) -> None:
        self._indexes = {}
        for field in self._fields:
            index = self._indexes[field] = collections.defaultdict(list)
            for element in self:  # pylint: disable=not-an-iterable
                value = self._getter(element, field)
                index[value].append(element)

    def filter(self, **kwargs: typing.Any) -> Results[T]:
        results = None
        for field, value in kwargs.items():
            if results is None:
                results = self._indexes[field][value]
            else:
                new_results = self._indexes[field][value]
                results = [
                    result for result in results if result in new_results
                ]
        if results is None:
            results = self
        return Results(results, filter_=kwargs)

    def rebuild_indexes_for_item(self, item: T) -> None:
        for field in self._fields:
            value = self._getter(item, field)
            self._indexes[field][value].append(item)

    def append(self, item: T) -> None:
        super().append(item)  # pylint: disable=no-member
        self.rebuild_indexes_for_item(item)

    def remove(self, item: T) -> None:
        super().remove(item)  # pylint: disable=no-member
        for field in self._fields:
            value = self._getter(item, field)
            self._indexes[field][value].remove(item)
