import typing
from dataclasses import InitVar
from typing import Annotated as Deprecated

import msgspec

from msgspex.tools.model import is_none  # type: ignore

UNSET: typing.Final[typing.Any]

@typing.overload
def field() -> typing.Any: ...
@typing.overload
def field(*, alias: str) -> typing.Any: ...
@typing.overload
def field(*, name: str | None = ...) -> typing.Any: ...
@typing.overload
def field(*, default: typing.Any, name: str | None = ...) -> typing.Any: ...
@typing.overload
def field(*, default: typing.Any, alias: str) -> typing.Any: ...
@typing.overload
def field(*, default_factory: typing.Callable[[], typing.Any], name: str | None = None) -> typing.Any: ...
@typing.overload
def field(*, default_factory: typing.Any, alias: str) -> typing.Any: ...
@typing.overload
def field(*, converter: typing.Callable[[typing.Any], typing.Any], name: str | None = ...) -> typing.Any: ...
@typing.overload
def field(*, converter: typing.Callable[[typing.Any], typing.Any], alias: str) -> typing.Any: ...
@typing.overload
def field(*, default: typing.Any, converter: typing.Callable[[typing.Any], typing.Any], name: str | None = ...) -> typing.Any: ...
@typing.overload
def field(*, default: typing.Any, converter: typing.Callable[[typing.Any], typing.Any], alias: str) -> typing.Any: ...
@typing.overload
def field(
    *,
    default_factory: typing.Callable[[], typing.Any],
    converter: typing.Callable[[typing.Any], typing.Any],
    name: str | None = None,
) -> typing.Any: ...
@typing.overload
def field(
    *,
    default_factory: typing.Callable[[], typing.Any],
    converter: typing.Callable[[typing.Any], typing.Any],
    alias: str,
) -> typing.Any: ...

class From[T]:
    def __new__(cls, _: T, /) -> typing.Any: ...

class ModelMeta(msgspec.StructMeta): ...

@typing.dataclass_transform(field_specifiers=(field,))
class Model(msgspec.Struct, metaclass=ModelMeta):
    __model_fields__: typing.ClassVar[typing.Mapping[str, msgspec.inspect.Field]]
    __model_required_fields__: typing.ClassVar[typing.Mapping[str, msgspec.inspect.Field]]
    __model_aliases_fields__: typing.ClassVar[typing.Mapping[str, str]]
    __model_meta_deprecated_fields__: typing.ClassVar[typing.Mapping[str, str | None]]
    __model_optional_fields__: typing.ClassVar[typing.Iterable[str]]
    __model_nullable_optional_fields__: typing.ClassVar[typing.Iterable[str]]
    __model_init_only_fields__: typing.ClassVar[typing.Iterable[str]]
    __model_deprecated_fields__: typing.ClassVar[typing.Iterable[str]]

    @classmethod
    def from_data[**P, T](cls: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T: ...
    @classmethod
    def from_mapping(cls, mapping: typing.Mapping[str, typing.Any], /) -> typing.Self: ...
    @classmethod
    def from_dict(cls, obj: dict[str, typing.Any], /) -> typing.Self: ...
    @classmethod
    def from_raw(cls, raw: str | bytes, /) -> typing.Self: ...
    def to_raw(self) -> str: ...
    def to_dict(
        self,
        *,
        exclude_fields: set[str] | None = None,
    ) -> dict[str, typing.Any]: ...
    def to_full_dict(
        self,
        *,
        exclude_fields: set[str] | None = None,
    ) -> dict[str, typing.Any]: ...

__all__ = ("UNSET", "Deprecated", "From", "InitVar", "Model", "ModelMeta", "field")
