import typing

ITEM = typing.TypeVar('ITEM')
FIELD = str
VALUE = typing.TypeVar('VALUE')
GETTER = typing.Callable[[ITEM, FIELD], VALUE]
