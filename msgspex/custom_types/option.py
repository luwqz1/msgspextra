import typing

import msgspec
from kungfu.library import Nothing, Some
from msgspec import UnsetType


class OptionMeta(type):
    def __instancecheck__(cls, __instance: typing.Any) -> bool:
        return isinstance(__instance, Some | Nothing | UnsetType)


class Option[Value](metaclass=OptionMeta):
    pass


type NullableOption[T] = typing.Annotated[Option[T], msgspec.Meta(extra=dict(nullable=True))]


__all__ = ("NullableOption", "Option")
