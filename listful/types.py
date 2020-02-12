import typing

ITEM = typing.TypeVar('ITEM')
VALUE = typing.TypeVar('VALUE')
GETTER = typing.Callable[[ITEM, str], VALUE]
