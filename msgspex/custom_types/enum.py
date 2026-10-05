import enum
import inspect
import sys
import types
import typing

from msgspex.tools.class_property import class_property

_FRIENDS_NOT_SUPPORTED_VALUES_MAP: typing.Final[typing.Any] = None
_MISSING: typing.Final[typing.Any] = object()
_DEFAULT_NOT_SUPPORTED_STRING: typing.Final = "<not supported member>"
_DEFAULT_NOT_SUPPORTED_BYTES: typing.Final = b"<not supported member>"
_DEFAULT_NOT_SUPPORTED_INTEGER: typing.Final = -sys.maxsize
_DEFAULT_NOT_SUPPORTED_FLOAT: typing.Final = float("-inf")


def _create_enum_class() -> type[Enum]:
    cls_name = "Enum"
    classdict = enum.EnumDict(cls_name)

    for key, value in enum.Enum.__dict__.items():
        if isinstance(value, classmethod | staticmethod) or inspect.isroutine(value):
            try:
                classdict[key] = value
            except ValueError as e:
                if str(e) == f"_sunder_ names, such as {key!r}, are reserved for future Enum use":
                    continue
                raise

    classdict.update(
        dict(
            __module__=__name__,
            __name__=cls_name,
            __doc__=enum.Enum.__doc__,
            __qualname__=f"{__name__}.{cls_name}",
        ),
    )
    return typing.cast("type[Enum]", _EnumMeta(cls_name, (), classdict))


class _EnumMeta(enum.EnumMeta, type):
    def __new__[Self](
        metacls: type[Self],
        cls: str,
        bases: tuple[type[typing.Any], ...],
        classdict: enum.EnumDict,
        *,
        boundary: enum.FlagBoundary | None = None,
        _simple: bool = False,
        not_supported_member: typing.Any | None = "NOT_SUPPORTED_MEMBER",
        not_supported_value: typing.Any = _MISSING,
        **kwds: typing.Any,
    ) -> Self:
        if not_supported_member is not None and not isinstance(not_supported_member, str):
            raise ValueError(f"{not_supported_member=} is not instance of `str`.")

        if (
            not_supported_member is not None
            and _FRIENDS_NOT_SUPPORTED_VALUES_MAP
            and (
                not_supported := next(
                    (value for friend, value in _FRIENDS_NOT_SUPPORTED_VALUES_MAP.items() if friend in bases),
                    None,
                )
            )
            is not None
        ):
            if not_supported_value is not _MISSING and not isinstance(not_supported_value, type(not_supported)):
                raise ValueError(f"{not_supported_value=} is not instance of `{type(not_supported).__name__}`.")

            classdict[not_supported_member] = not_supported if not_supported_value is _MISSING else not_supported_value
            classdict["_missing_"] = classmethod(lambda cls, *_, **__: getattr(cls, not_supported_member))
            classdict["__not_supported__"] = class_property(lambda cls: getattr(cls, not_supported_member))

        classdict["name"] = property(lambda self: object.__getattribute__(self, "_name_"))
        classdict["value"] = property(lambda self: object.__getattribute__(self, "_value_"))
        return super().__new__(metacls, cls, bases, classdict, boundary=boundary, _simple=_simple, **kwds)


if typing.TYPE_CHECKING:

    class _EnumMixin[Value = typing.Any]:
        __not_supported__: typing.Final[Value]  # type: ignore

    @typing.no_type_check
    class Enum(_EnumMixin, enum.Enum): ...

    @typing.no_type_check
    class StrEnum(_EnumMixin[str], enum.StrEnum): ...

    @typing.no_type_check
    class BytesEnum(_EnumMixin[bytes], bytes, enum.Enum): ...  # type: ignore

    @typing.no_type_check
    class IntEnum(_EnumMixin[int], enum.IntEnum): ...

    @typing.no_type_check
    class FloatEnum(_EnumMixin[float], float, enum.Enum): ...  # type: ignore

else:
    Enum = _create_enum_class()

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return self._value_

    class IntEnum(int, Enum):
        def __int__(self) -> int:
            return int(self._value_)

        def __float__(self) -> float:
            return float(self._value_)

        def __index__(self) -> int:
            return int(self._value_)

        def __str__(self) -> str:
            return str(self._value_)

    class FloatEnum(float, Enum):
        def __int__(self) -> int:
            return int(self._value_)

        def __float__(self) -> float:
            return float(self._value_)

        def __str__(self) -> str:
            return str(self._value_)

    class BytesEnum(bytes, Enum):
        def __bytes__(self) -> bytes:
            return self._value_

        def __getnewargs__(self) -> tuple[bytes]:
            return (self._value_,)

        def __str__(self) -> str:
            return str(self._value_)


BaseEnumMeta = EnumMeta = _EnumMeta


_FRIENDS_NOT_SUPPORTED_VALUES_MAP: typing.Final = types.MappingProxyType(  # type: ignore
    mapping={
        str: _DEFAULT_NOT_SUPPORTED_STRING,
        int: _DEFAULT_NOT_SUPPORTED_INTEGER,
        float: _DEFAULT_NOT_SUPPORTED_FLOAT,
        bytes: _DEFAULT_NOT_SUPPORTED_BYTES,
        StrEnum: _DEFAULT_NOT_SUPPORTED_STRING,
        IntEnum: _DEFAULT_NOT_SUPPORTED_INTEGER,
        FloatEnum: _DEFAULT_NOT_SUPPORTED_FLOAT,
        BytesEnum: _DEFAULT_NOT_SUPPORTED_BYTES,
    },
)


__all__ = ("BaseEnumMeta", "BytesEnum", "Enum", "EnumMeta", "FloatEnum", "IntEnum", "StrEnum")
