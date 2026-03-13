import typing

import msgspec
from kungfu.library import Sum
from kungfu.library.monad.option import NOTHING, Nothing
from msgspec._utils import get_class_annotations, get_type_hints  # type: ignore

_COMMON_TYPES: typing.Final = frozenset((Sum, str, bytes, int, float, bool, None))


def get_origin[T](t: T, /) -> type[T]:
    t_ = typing.get_origin(t) or t
    t_ = type(t_) if not isinstance(t_, type) else t_  # type: ignore
    return typing.cast("type[T]", t_)


def is_none(obj: typing.Any, /) -> typing.TypeIs[Nothing | None]:
    return obj is None or obj is NOTHING


def is_common_type[T](t: T, /) -> typing.TypeGuard[type[T]]:
    if not isinstance(t, type):
        return False
    return t in _COMMON_TYPES or issubclass(t, msgspec.Struct) or hasattr(t, "__dataclass_fields__")  # type: ignore


def struct_asdict(
    struct: msgspec.Struct,
    /,
    *,
    exclude_unset: bool = True,
    exclude_none: bool = False,
    exclude_nothing: bool = False,
    unset_as_nothing: bool = False,
    none_as_nothing: bool = False,
    nothing_as_none: bool = False,
) -> dict[str, typing.Any]:
    return {
        k: v
        if not (unset_as_nothing or none_as_nothing or nothing_as_none)
        else NOTHING
        if unset_as_nothing and v is msgspec.UNSET
        else NOTHING
        if none_as_nothing and v is None
        else None
        if nothing_as_none and v is NOTHING
        else v
        for k, v in msgspec.structs.asdict(struct).items()
        if not (exclude_nothing and v is NOTHING) and not (exclude_unset and v is msgspec.UNSET) and not (exclude_none and v is None)
    }


def type_check(obj: typing.Any, t: typing.Any) -> bool:
    return isinstance(obj, t) if isinstance(t, type) and issubclass(t, msgspec.Struct) else type(obj) in t if isinstance(t, tuple) else type(obj) is t


__all__ = (
    "get_class_annotations",
    "get_origin",
    "get_type_hints",
    "is_common_type",
    "is_none",
    "struct_asdict",
    "type_check",
)
