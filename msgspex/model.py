import dataclasses
import keyword
import types
import typing
from functools import cache
from reprlib import recursive_repr

import msgspec
from kungfu.library.monad.option import NOTHING
from msgspec import UNSET

from msgspex.custom_types.option import Option
from msgspex.decoder import decoder
from msgspex.deprecated import get_model_warning_deprecation_meta, is_field_deprecated, warn_deprecation
from msgspex.encoder import encoder
from msgspex.tools import is_none, struct_asdict
from msgspex.tools.bundle import bundle

type From[T] = T
type InitOnly[T] = typing.Annotated[T, msgspec.Meta(extra=dict(init_only=True))]

_SENTINEL: typing.Final = object


def field(**kwargs: typing.Any) -> typing.Any:
    if kwargs.get("default") is Ellipsis:
        kwargs["default"] = UNSET

    if "alias" in kwargs:
        kwargs["name"] = kwargs.pop("alias")

    kwargs.pop("converter", None)
    return msgspec.field(**kwargs)


class ModelMeta(msgspec.StructMeta):
    def __new__(
        mcls: type[typing.Any],
        name: str,
        bases: tuple[type[typing.Any], ...],
        namespace: dict[str, typing.Any],
        /,
        **kwargs: typing.Any,
    ) -> typing.Any:
        cls = msgspec.StructMeta.__new__(mcls, name, bases, namespace, **kwargs)

        for annname, annval in cls.__annotations__.copy().items():
            if isinstance(annval, dataclasses.InitVar):
                cls.__annotations__[annname] = InitOnly[annval.type]  # type: ignore

        return cls

    def __getattribute__(cls, name: str, /) -> typing.Any:
        if name == "__post_init__":
            post_init = super().__getattribute__(name)
            if post_init != ModelMeta.__post_init__:
                return lambda self: ModelMeta.pre_post_init(self, post_init)  # type: ignore

        return super().__getattribute__(name)

    def __post_init__(cls, model: Model) -> None:
        cls.pre_post_init(model)

    @staticmethod
    def pre_post_init(model: Model, post_post_init: typing.Callable[..., None] | None = None, /) -> None:
        model._warn_deprecation_if_deprecated()  # type: ignore

        optional_fields = model.get_optional_fields()
        nullable_optional_fields = model.get_nullable_optional_fields()
        init_only_fields = model.get_init_only_fields()

        struct: msgspec.Struct = model  # type: ignore
        post_init_data: dict[str, typing.Any] = {}

        for field_name, field_value in struct_asdict(struct).items():
            value = set_value = _SENTINEL

            if field_name in nullable_optional_fields and field_value is None:
                value = set_value = NOTHING

            elif field_name in optional_fields and is_none(field_value):
                value = set_value = UNSET

            if field_name in init_only_fields:
                set_value = UNSET
                post_init_data[field_name] = field_value if value is _SENTINEL else value

            if set_value is not _SENTINEL:
                msgspec.structs.force_setattr(model, field_name, set_value)

        if post_post_init is not None:
            try:
                bundle(post_post_init, post_init_data)(model)
            except Exception as exc:
                raise msgspec.ValidationError(exc) from None


class Model(msgspec.Struct, metaclass=ModelMeta, dict=True, rename={kw + "_": kw for kw in keyword.kwlist}):
    def __getattribute__(self, name: str, /) -> typing.Any:
        class_ = type(self)
        val = object.__getattribute__(self, name)

        if name not in class_.__struct_fields__:
            return val

        if name in class_.get_optional_fields():
            return NOTHING if val is UNSET else val

        if val is UNSET:
            raise AttributeError(f"{class_.__name__!r} object has no attribute {name!r}")

        return val

    @recursive_repr()
    def __repr__(self) -> str:
        init_only_fields = self.get_init_only_fields()
        optional_fields = self.get_optional_fields()
        return "{}({})".format(
            type(self).__name__,
            ", ".join(
                f"{f}={'Nothing()' if val is UNSET and f in optional_fields else repr(val)}"
                for f, val in struct_asdict(self, exclude_unset=False).items()
                if f not in init_only_fields
            ),
        )

    @classmethod
    @cache
    def _warn_deprecation_if_deprecated(cls) -> None:
        if warning_deprecation_meta := get_model_warning_deprecation_meta(cls):
            warn_deprecation(**warning_deprecation_meta)

    @classmethod
    @cache
    def get_all_fields(cls) -> types.MappingProxyType[str, msgspec.inspect.Field]:
        return types.MappingProxyType(
            mapping={f.name: f for f in msgspec.inspect.type_info(cls).fields},  # type: ignore
        )

    @classmethod
    @cache
    def get_init_only_fields(cls) -> frozenset[str]:
        return frozenset(
            f.name
            for f in cls.get_all_fields().values()
            if isinstance(f.type, msgspec.inspect.Metadata)
            and f.type.extra  # type: ignore
            and f.type.extra.get("init_only") is True  # type: ignore
        )

    @classmethod
    @cache
    def get_fields(cls) -> types.MappingProxyType[str, msgspec.inspect.Field]:
        init_only_fields = cls.get_init_only_fields()
        return types.MappingProxyType(
            mapping={name: f for name, f in cls.get_all_fields().items() if name not in init_only_fields},
        )

    @classmethod
    @cache
    def get_optional_fields(cls) -> frozenset[str]:
        optional_fields = frozenset(
            f.name
            for f in cls.get_all_fields().values()
            if (isinstance(f.type, msgspec.inspect.CustomType) and issubclass(f.type.cls, Option))  # type: ignore
            or (
                isinstance(f.type, msgspec.inspect.Metadata) and isinstance(f.type.type, msgspec.inspect.CustomType) and issubclass(f.type.type.cls, Option)  # type: ignore
            )
        )
        return cls.get_nullable_optional_fields() ^ optional_fields

    @classmethod
    @cache
    def get_nullable_optional_fields(cls) -> frozenset[str]:
        return frozenset(
            f.name
            for f in cls.get_all_fields().values()
            if isinstance(f.type, msgspec.inspect.Metadata)
            and f.type.extra  # type: ignore
            and f.type.extra.get("nullable") is True  # type: ignore
            and isinstance(f.type.type, msgspec.inspect.CustomType)
            and issubclass(f.type.type.cls, Option)  # type: ignore
        )

    @classmethod
    @cache
    def get_aliases_fields(cls) -> types.MappingProxyType[str, str]:
        return types.MappingProxyType(
            mapping={name: value.encode_name for name, value in cls.get_all_fields().items()},
        )

    @classmethod
    @cache
    def get_deprecated_fields(cls) -> frozenset[str]:
        return frozenset(name for name, value in cls.__dict__.items() if isinstance(value, property) and is_field_deprecated(value))

    @classmethod
    def from_data(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        aliases = cls.get_aliases_fields()
        return cls.from_dict(
            {aliases.get(name, name): value for name, value in (cls.__signature__.bind_partial(*args).arguments | kwargs).items()},
        )

    @classmethod
    def from_dict(cls, obj: dict[str, typing.Any], /) -> typing.Self:
        return cls.from_mapping(obj)

    @classmethod
    def from_mapping(cls, mapping: typing.Mapping[str, typing.Any], /) -> typing.Self:
        return decoder.convert(mapping, type=cls)

    @classmethod
    def from_raw(cls, raw: str | bytes, /) -> typing.Self:
        return decoder.decode(raw, type=cls)

    def _to_dict(
        self,
        dct_name: str,
        exclude_fields: set[str],
        full: bool,
    ) -> dict[str, typing.Any]:
        if dct_name not in self.__dict__:
            self.__dict__[dct_name] = (  # type: ignore
                struct_asdict(self) if not full else encoder.to_builtins(self.to_dict(exclude_fields=exclude_fields))
            )

        if not exclude_fields:
            return self.__dict__[dct_name]

        return {key: value for key, value in self.__dict__[dct_name].items() if key not in exclude_fields}

    def to_raw(self) -> str:
        return encoder.encode(self)

    def to_dict(
        self,
        *,
        exclude_fields: set[str] | None = None,
    ) -> dict[str, typing.Any]:
        return self._to_dict("model_as_dict", exclude_fields or set(), full=False)

    def to_full_dict(
        self,
        *,
        exclude_fields: set[str] | None = None,
    ) -> dict[str, typing.Any]:
        return self._to_dict("model_as_full_dict", exclude_fields or set(), full=True)


__all__ = ("UNSET", "From", "Model", "ModelMeta", "field")
