import typing


class Item:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, Item):
            return self.x == other.x and self.y == other.y
        return False
