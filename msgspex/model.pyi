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
    """Base model built on the `msgspec` struct class."""

    __model_fields__: typing.ClassVar[typing.Mapping[str, msgspec.inspect.Field]]
    """All fields of the model, including `dataclasses.InitVar` fields."""
    __model_accessible_fields__: typing.ClassVar[typing.Mapping[str, msgspec.inspect.Field]]
    """All fields of the model, excluding `dataclasses.InitVar` fields."""
    __model_aliases_fields__: typing.ClassVar[typing.Mapping[str, str]]
    """Aliases of fields via `field(name=...)` or `field(alias=...)`."""
    __model_meta_deprecated_fields__: typing.ClassVar[typing.Mapping[str, str | None]]
    """All fields of the model marked as deprecated via `Deprecated` meta-annotation."""
    __model_optional_fields__: typing.ClassVar[typing.Iterable[str]]
    """All fields of the model marked as optional via `Option` type."""
    __model_nullable_optional_fields__: typing.ClassVar[typing.Iterable[str]]
    """All fields of the model marked as nullable optional via `NullableOption` meta-annotation."""
    __model_init_only_fields__: typing.ClassVar[typing.Iterable[str]]
    """All fields of the model marked as init only via `dataclasses.InitVar` type."""
    __model_deprecated_fields__: typing.ClassVar[typing.Iterable[str]]
    """All fields of the model marked as deprecated via `@property` with a `@field_deprecated` decorator."""
    @classmethod
    def initialize[**P, T](cls: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """The method of calling a model, which pass the arguments without validation to the `__init__`."""
    @classmethod
    def from_data[**P, T](cls: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """The old method of calling a model, which validates the arguments passed to the model constructor.

        note: A direct call to the model behaves in the same way.
        """
    @classmethod
    def from_mapping(cls, mapping: typing.Mapping[str, typing.Any], /) -> typing.Self:
        """The method of calling a model, which validates passed mapping to the model constructor."""
    @classmethod
    def from_dict(cls, obj: dict[str, typing.Any], /) -> typing.Self:
        """The method of calling a model, which validates passed dict to the model constructor."""
    @classmethod
    def from_raw(cls, raw: str | bytes, /) -> typing.Self:
        """The method of calling a model, which validates passed raw json to the model constructor."""
    def to_raw(self) -> str:
        """The method to converting a model to a raw json."""
    def to_dict(
        self,
        *,
        exclude_fields: set[str] | None = None,
    ) -> dict[str, typing.Any]:
        """The method to converting a model to a dict without encoding."""
    def to_full_dict(
        self,
        *,
        exclude_fields: set[str] | None = None,
    ) -> dict[str, typing.Any]:
        """The method to converting a model to a dict with encoding."""

__all__ = ("UNSET", "Deprecated", "From", "InitVar", "Model", "ModelMeta", "field")
