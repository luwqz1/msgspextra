import enum
import math
import sys
import typing

NOT_SUPPORTED: typing.Final = "NOT_SUPPORTED"


def _is_friend(bases: tuple[type[typing.Any], ...], /) -> bool:
    return any(friend in bases for friend in ENUM_FRIENDS)


class StrEnum(str, enum.Enum):
    def __str__(self) -> str:
        return self.value


class IntEnum(int, enum.Enum):
    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    def __index__(self) -> int:
        return self.value


class FloatEnum(float, enum.Enum):
    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return self.value


class BaseEnumMeta(enum.EnumMeta, type):
    if typing.TYPE_CHECKING:

        class _BaseEnumMeta(enum.Enum):  # noqa
            NOT_SUPPORTED = enum.auto()

        NOT_SUPPORTED: typing.Literal[_BaseEnumMeta.NOT_SUPPORTED]

    else:

        @staticmethod
        def _member_missing(cls, value):
            return cls._member_map_["NOT_SUPPORTED"]

        def __new__(
            metacls,
            cls,
            bases,
            classdict,
            *,
            boundary=None,
            _simple=False,
            **kwds,
        ):
            if _is_friend(bases):
                classdict["NOT_SUPPORTED"] = next(
                    (value for base, value in NOT_SUPPORTED_VALUES.items() if base in bases),
                    NOT_SUPPORTED,
                )

            classdict["_missing_"] = classmethod(BaseEnumMeta._member_missing)
            return super().__new__(metacls, cls, bases, classdict, boundary=boundary, _simple=_simple, **kwds)


ENUM_FRIENDS: typing.Final = (str, int, float, StrEnum, IntEnum, FloatEnum)
NOT_SUPPORTED_VALUES: typing.Final = {
    str: NOT_SUPPORTED,
    int: sys.maxsize,
    float: math.inf,
    StrEnum: NOT_SUPPORTED,
    IntEnum: sys.maxsize,
    FloatEnum: math.inf,
    enum.StrEnum: NOT_SUPPORTED,
    enum.IntEnum: sys.maxsize,
}


__all__ = ("BaseEnumMeta", "FloatEnum", "IntEnum", "StrEnum")
