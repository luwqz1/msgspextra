import typing


class class_property[T]:  # noqa: N801
    def __init__(self, func: typing.Callable[[typing.Any], T], /) -> None:
        self.func = func
        self.func_name = "__" + func.__name__

    def __get__(self, instance: typing.Any | None, owner: type[typing.Any], /) -> T:
        return self.func(owner)


__all__ = ("class_property",)
