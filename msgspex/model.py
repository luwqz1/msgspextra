import dataclasses
import keyword
import types
import typing
import warnings
from functools import cache, wraps
from reprlib import recursive_repr

import msgspec
from kungfu.library.monad.option import NOTHING
from msgspec import UNSET

from msgspex.custom_types.option import Option
from msgspex.decoder import decoder
from msgspex.deprecated import get_model_warning_deprecation_meta, is_field_deprecated, warn_deprecation
from msgspex.encoder import encoder
from msgspex.tools import struct_asdict
from msgspex.tools.bundle import bundle

type From[T] = T
type InitOnly[T] = typing.Annotated[T, msgspec.Meta(extra=dict(init_only=True))]
type Factory = typing.Callable[[], typing.Any]

_SENTINEL: typing.Final = object()
_FROM_CALL_SENTINEL: typing.Final = object()
_MARK_MODEL_WARNED_DEPRECATION_ATTR: typing.Final = "__model_warned_deprecation__"


def get_fields_by_meta(
    model: type[Model],
    meta_key: str,
    predicate: typing.Callable[[typing.Any], bool] = lambda value: value,
) -> dict[str, msgspec.inspect.Field]:
    return {
        f.name: f
        for f in model.__model_fields__.values()
        if isinstance(f.type, msgspec.inspect.Metadata)
        and f.type.extra  # type: ignore
        and meta_key in f.type.extra  # type: ignore
        and predicate(f.type.extra[meta_key]) is True  # type: ignore
    }


def warn_model_deprecated(*, stacklevel: int) -> typing.Callable[..., typing.Any]:
    def decorator(f: typing.Callable[..., Model], /) -> typing.Callable[..., typing.Any]:
        @wraps(f)
        def wrapper(
            cls: type[typing.Any],
            __from_call: typing.Any = _SENTINEL,
            /,
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> Model:
            model = f(cls, __from_call, *args, **kwargs)
            model._warn_deprecation_if_deprecated(stacklevel=stacklevel, is_from_call=(__from_call is _FROM_CALL_SENTINEL))  # type: ignore
            return model

        return wrapper

    return decorator


def field(**kwargs: typing.Any) -> typing.Any:
    if kwargs.get("default") is Ellipsis:
        kwargs["default"] = UNSET

    if "alias" in kwargs:
        kwargs["name"] = kwargs.pop("alias")

    kwargs.pop("converter", None)
    return msgspec.field(**kwargs)


@dataclasses.dataclass(kw_only=True)
class DefaultFactory:
    on_init: Factory
    on_decode: typing.Any = msgspec.NODEFAULT
    default: typing.Any = msgspec.NODEFAULT

    def __call__(self) -> typing.NoReturn:
        raise NotImplementedError


class Deprecated:
    def __class_getitem__(cls, item: typing.Any, /) -> typing.Any:
        annotation = typing.Any
        message = stacklevel = None

        if not isinstance(item, tuple):
            annotation = item

        elif len(items := typing.cast("tuple[typing.Any, ...]", item)) > 1:
            annotation = items[0]
            message = items[1]
            stacklevel = None if len(items) < 3 else items[2]

            if stacklevel is None and isinstance(message, int):
                message, stacklevel = None, message

        elif len(items) == 1:
            annotation = items[0]
            message = stacklevel = None

        return typing.Annotated[
            annotation,
            msgspec.Meta(
                extra=dict(  # type: ignore
                    deprecated=True,
                    deprecation_message=message,
                    deprecation_stacklevel=stacklevel,
                ),
            ),
        ]


class ModelMeta(msgspec.StructMeta):
    def __new__(
        mcls: type[typing.Any],
        name: str,
        bases: tuple[type[typing.Any], ...],
        namespace: dict[str, typing.Any],
        /,
        **kwargs: typing.Any,
    ) -> typing.Any:
        init_default_factory_map: dict[str, Factory] = {}

        for n, v in namespace.copy().items():
            if isinstance(v, msgspec._Field) and isinstance(v.default_factory, DefaultFactory):  # type: ignore
                init_default_factory_map[n] = v.default_factory.on_init
                namespace[n] = msgspec.field(  # type: ignore
                    name=v.name,
                    default=v.default_factory.default,
                    default_factory=msgspec.NODEFAULT if v.default_factory.default is not msgspec.NODEFAULT else v.default_factory.on_decode,
                )

        namespace["__model_init_default_factory_map__"] = types.MappingProxyType(mapping=init_default_factory_map)
        cls = msgspec.StructMeta.__new__(mcls, name, bases, namespace, **kwargs)

        for annname, annval in cls.__annotations__.copy().items():
            if isinstance(annval, dataclasses.InitVar):
                cls.__annotations__[annname] = InitOnly[annval.type]  # type: ignore

        return cls

    def __call__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        return cls.from_data(_FROM_CALL_SENTINEL, *args, **kwargs)  # type: ignore

    def __getattribute__(cls, name: str, /) -> typing.Any:
        getter = super().__getattribute__

        if name == "__model_initialized__":
            return getter(name)

        if name.startswith("__model_") and getter("__model_initialized__") is False:
            getter("__init_model__")()
            return getter(name)

        if name == "__post_init__":
            user_post_init = getter(name)

            if user_post_init != ModelMeta.__post_init__:
                return lambda self: ModelMeta.model_post_init(self, user_post_init)  # type: ignore

            return user_post_init

        return getter(name)

    def __post_init__(cls, model: Model) -> None:
        cls.model_post_init(model)

    @staticmethod
    def model_post_init(model: Model, user_post_init: typing.Callable[..., None] | None = None, /) -> None:
        model_cls = type(model)

        optional_fields = model_cls.__model_optional_fields__
        nullable_optional_fields = model_cls.__model_nullable_optional_fields__
        init_only_fields = model_cls.__model_init_only_fields__

        if user_post_init is None and not (optional_fields and nullable_optional_fields and init_only_fields):
            return

        struct: msgspec.Struct = model  # type: ignore
        post_init_data: dict[str, typing.Any] = {}

        for field_name, field_value in struct_asdict(struct).items():
            value = set_value = _SENTINEL

            if field_name in nullable_optional_fields and field_value is None:
                value = set_value = NOTHING

            elif field_name in optional_fields and (field_value is None or field_value is NOTHING):
                value = set_value = UNSET

            if field_name in init_only_fields:
                set_value = UNSET
                post_init_data[field_name] = field_value if value is _SENTINEL else value

            if set_value is not _SENTINEL:
                msgspec.structs.force_setattr(model, field_name, set_value)

        if user_post_init is not None:
            try:
                bundle(user_post_init, post_init_data)(model)
            except msgspec.ValidationError:
                raise
            except Exception as exc:
                raise msgspec.ValidationError(exc) from None

    def model_initialize(cls, *args: typing.Any, **kwds: typing.Any) -> typing.Any:
        if default_fact_map := cls.__model_init_default_factory_map__:
            pos_args: dict[str, typing.Any] = {}

            if args:
                pos_args = cls.__signature__.bind_partial(*args).arguments
                kwds.update(pos_args)

            for field_name in cls.__model_fields__:
                if field_name not in kwds and field_name in default_fact_map:
                    kwds[field_name] = default_fact_map[field_name]()

            return super().__call__(*tuple(kwds.pop(name) for name in pos_args), **kwds)

        return super().__call__(*args, **kwds)


class Model(msgspec.Struct, metaclass=ModelMeta, dict=True, rename={kw + "_": kw for kw in keyword.kwlist}):
    __model_initialized__: typing.ClassVar[bool] = False
    __model_warned_deprecation__: typing.ClassVar[bool]
    __model_fields__: typing.ClassVar[types.MappingProxyType[str, msgspec.inspect.Field]]
    __model_accessible_fields__: typing.ClassVar[types.MappingProxyType[str, msgspec.inspect.Field]]
    __model_aliases_fields__: typing.ClassVar[types.MappingProxyType[str, str]]
    __model_optional_fields__: typing.ClassVar[frozenset[str]]
    __model_nullable_optional_fields__: typing.ClassVar[frozenset[str]]
    __model_init_only_fields__: typing.ClassVar[frozenset[str]]
    __model_init_default_factory_map__: typing.ClassVar[types.MappingProxyType[str, Factory]]
    __model_deprecated_fields__: typing.ClassVar[frozenset[str]]
    __model_meta_deprecated_fields__: typing.ClassVar[types.MappingProxyType[str, tuple[str | None, int | None]]]
    __model_warned_meta_deprecated_fields__: typing.ClassVar[set[str]]

    def __getattribute__(self, name: str, /) -> typing.Any:
        class_ = type(self)
        val = object.__getattribute__(self, name)

        if name not in class_.__model_fields__:
            return val

        if name in class_.__model_optional_fields__:
            return NOTHING if val is UNSET else val

        if val is UNSET:
            raise AttributeError(f"{class_.__name__!r} object has no attribute {name!r}")

        return val

    def __str__(self) -> str:
        return self.__repr__()

    @recursive_repr()
    def __repr__(self) -> str:
        init_only_fields = self.__model_init_only_fields__
        optional_fields = self.__model_optional_fields__
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
    def __init_model__(cls) -> None:
        cls.__model_initialized__ = True
        cls.__model_warned_deprecation__ = False
        cls.__model_warned_meta_deprecated_fields__ = set()
        cls.__model_fields__ = types.MappingProxyType(
            mapping={f.name: f for f in msgspec.inspect.type_info(cls).fields},  # type: ignore
        )
        cls.__model_init_only_fields__ = frozenset(get_fields_by_meta(cls, "init_only"))
        cls.__model_nullable_optional_fields__ = frozenset(
            f.name
            for f in get_fields_by_meta(cls, "nullable").values()
            if isinstance(f.type.type, msgspec.inspect.CustomType)  # type: ignore
            and issubclass(f.type.type.cls, Option)  # type: ignore
        )
        cls.__model_optional_fields__ = (
            frozenset(
                f.name
                for f in cls.__model_fields__.values()
                if (isinstance(f.type, msgspec.inspect.CustomType) and issubclass(f.type.cls, Option))  # type: ignore
                or (
                    isinstance(f.type, msgspec.inspect.Metadata) and isinstance(f.type.type, msgspec.inspect.CustomType) and issubclass(f.type.type.cls, Option)  # type: ignore
                )
            )
            - cls.__model_nullable_optional_fields__
        )
        cls.__model_meta_deprecated_fields__ = types.MappingProxyType(
            mapping={
                name: (
                    None if (msg := field.type.extra.get("deprecation_message")) in (None, ...) else str(msg),  # type: ignore
                    field.type.extra.get("deprecation_stacklevel"),  # type: ignore
                )
                for name, field in get_fields_by_meta(cls, "deprecated").items()
            },
        )
        cls.__model_accessible_fields__ = types.MappingProxyType(
            mapping={name: f for name, f in cls.__model_fields__.items() if name not in cls.__model_init_only_fields__},
        )
        cls.__model_aliases_fields__ = types.MappingProxyType(
            mapping={name: value.encode_name for name, value in cls.__model_fields__.items()},
        )
        cls.__model_deprecated_fields__ = frozenset(name for name, value in cls.__dict__.items() if isinstance(value, property) and is_field_deprecated(value))

    @classmethod
    def _warn_deprecation_if_deprecated(cls, stacklevel: int = 3, is_from_call: bool = False) -> None:
        if cls.__model_warned_deprecation__:
            return

        if warning_deprecation_meta := get_model_warning_deprecation_meta(cls):
            warning_deprecation_meta["stacklevel"] = warning_deprecation_meta.get("stacklevel", stacklevel) + is_from_call
            warn_deprecation(**warning_deprecation_meta)
            cls.__model_warned_deprecation__ = True

    @classmethod
    def _warn_deprecated_fields(cls, fields: set[str], stacklevel: int = 1) -> None:
        deprecated_fields = cls.__model_meta_deprecated_fields__
        warned_meta_deprecated_fields = cls.__model_warned_meta_deprecated_fields__
        deprecated = fields & (set(deprecated_fields) - warned_meta_deprecated_fields)

        if not deprecated:
            return

        with warnings.catch_warnings(action="module", category=PendingDeprecationWarning):
            for field in deprecated:
                message, stacklevel_ = deprecated_fields[field]
                warnings.warn(
                    message=message or f"Field `{field}` of `{cls.__name__}` is deprecated and will be removed in future releases.",
                    category=PendingDeprecationWarning,
                    stacklevel=stacklevel if stacklevel_ is None else stacklevel_,
                )
                warned_meta_deprecated_fields.add(field)

    @classmethod
    def initialize(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        return ModelMeta.model_initialize(cls, *args, **kwargs)

    @classmethod
    @warn_model_deprecated(stacklevel=4)
    def from_data(
        cls,
        __from_call: typing.Any = _SENTINEL,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> typing.Self:
        is_from_call = __from_call is _FROM_CALL_SENTINEL
        is_just_arg = not (is_from_call or __from_call is _SENTINEL)

        data = (
            cls.__signature__.bind_partial(__from_call).arguments
            if is_just_arg and not args
            else cls.__signature__.bind_partial(__from_call, *args).arguments
            if is_just_arg
            else cls.__signature__.bind_partial(*args).arguments
            if args
            else kwargs
        )

        if data is not kwargs:
            data.update(kwargs)

        if default_fact_map := cls.__model_init_default_factory_map__:
            for field_name in cls.__model_fields__:
                if field_name not in data and field_name in default_fact_map:
                    data[field_name] = default_fact_map[field_name]()

        try:
            aliases = cls.__model_aliases_fields__
            model = decoder.convert({aliases.get(name, name): value for name, value in data.items()}, type=cls)
        except msgspec.ValidationError as exc:
            raise TypeError(exc) from None

        cls._warn_deprecated_fields(set(data), stacklevel=4 + is_from_call)
        return model

    @classmethod
    @warn_model_deprecated(stacklevel=4)
    def from_mapping(cls, mapping: typing.Mapping[str, typing.Any], /) -> typing.Self:
        return decoder.convert(mapping, type=cls)

    @classmethod
    @warn_model_deprecated(stacklevel=4)
    def from_raw(cls, raw: str | bytes, /) -> typing.Self:
        return decoder.decode(raw, type=cls)

    from_dict = from_mapping

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


__all__ = ("UNSET", "Deprecated", "From", "Model", "ModelMeta", "field")
