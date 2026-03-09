import typing
from contextlib import contextmanager

import kungfu.library
import msgspec

from msgspex.caster import SupportsCast
from msgspex.tools import bundle, fullname, get_origin

type Context = dict[str, typing.Any]
type Order = typing.Literal["deterministic", "sorted"]
type EncHook = typing.Callable[typing.Concatenate[typing.Any, ...], typing.Any]


def to_builtins(
    obj: typing.Any,
    *,
    str_keys: bool = False,
    builtin_types: typing.Iterable[type[typing.Any]] | None = None,
    order: Order | None = None,
    context: Context | None = None,
) -> kungfu.library.Result[typing.Any, msgspec.ValidationError]:
    try:
        return kungfu.library.Ok(
            encoder.to_builtins(
                obj,
                str_keys=str_keys,
                builtin_types=builtin_types,
                order=order,
                context=context,
            ),
        )
    except msgspec.ValidationError as error:
        return kungfu.library.Error(error)


class Encoder:
    cast_types: dict[typing.Any, type[SupportsCast]]
    enc_hooks: dict[typing.Any, EncHook]
    abstract_enc_hooks: dict[typing.Any, EncHook]
    default_enc_hook: EncHook | None
    default_abstract_enc_hook: EncHook | None

    __slots__ = (
        "cast_types",
        "enc_hooks",
        "abstract_enc_hooks",
        "default_enc_hook",
        "default_abstract_enc_hook",
    )

    def __init__(self) -> None:
        self.cast_types = {}
        self.enc_hooks = {}
        self.abstract_enc_hooks = {}
        self.default_enc_hook = None
        self.default_abstract_enc_hook = None

    def __repr__(self) -> str:
        return ("<{}: cast_types={}, enc_hooks={!r}, abstract_enc_hooks={!r}, default_enc_hook={!r}, default_abstract_enc_hook={!r}>").format(
            type(self).__name__,
            f"<{', '.join(f'{fullname(x)} -> {fullname(y)}' for x, y in self.cast_types.items())}>",
            self.enc_hooks,
            self.abstract_enc_hooks,
            self.default_enc_hook,
            self.default_abstract_enc_hook,
        )

    @contextmanager
    def __call__(
        self,
        *,
        decimal_format: typing.Literal["string", "number"] = "string",
        uuid_format: typing.Literal["canonical", "hex"] = "canonical",
        order: Order | None = None,
        context: Context | None = None,
    ) -> typing.Generator[msgspec.json.Encoder, typing.Any, None]:
        """Context manager returns the `msgspec.json.Encoder` object with passed the `enc_hook`."""
        yield msgspec.json.Encoder(
            enc_hook=self.enc_hook(context),
            decimal_format=decimal_format,
            uuid_format=uuid_format,
            order=order,
        )

    def add_cast_type(self, t: typing.Any, caster: type[SupportsCast], /) -> None:
        self.cast_types[t] = caster

    def set_default_enc_hook[T: EncHook](self, enc_hook: T, /) -> T:
        self.default_enc_hook = enc_hook
        return enc_hook

    def set_default_abstract_enc_hook[T: EncHook](self, enc_hook: T, /) -> T:
        self.default_abstract_enc_hook = enc_hook
        return enc_hook

    def add_enc_hook[T: EncHook](self, t: typing.Any, /) -> typing.Callable[[T], T]:
        def decorator(func: T, /) -> T:
            encode_hook = self.enc_hooks.setdefault(get_origin(t), func)
            return func if encode_hook is not func else encode_hook  # type: ignore

        return decorator

    def add_abstract_enc_hook[T: EncHook](self, abstract_type: typing.Any, /) -> typing.Callable[[T], T]:
        def decorator(func: T, /) -> T:
            return self.abstract_enc_hooks.setdefault(get_origin(abstract_type), func)  # type: ignore

        return decorator

    def get_abstract_enc_hook(self, subtype: type[typing.Any], /) -> EncHook | None:
        for abstract, enc_hook in self.abstract_enc_hooks.items():
            if issubclass(subtype, abstract) or issubclass(type(subtype), abstract):
                return enc_hook

        return self.default_abstract_enc_hook

    def enc_hook(self, context: Context | None = None, /) -> EncHook:
        def inner(obj: typing.Any, /) -> typing.Any:
            origin_type = get_origin(obj)

            if (enc_hook_func := self.enc_hooks.get(origin_type, self.default_enc_hook)) is None and (
                enc_hook_func := self.get_abstract_enc_hook(origin_type)
            ) is None:
                raise NotImplementedError(
                    f"Not implemented encode hook for object of type `{fullname(origin_type)}`. You can implement encode hook for this object.",
                )

            return bundle(enc_hook_func, context or {}, start_idx=1)(obj)

        return inner

    @typing.overload
    def encode(
        self,
        obj: typing.Any,
        /,
        *,
        order: Order | None = None,
        context: Context | None = None,
    ) -> str: ...

    @typing.overload
    def encode(
        self,
        obj: typing.Any,
        /,
        *,
        as_str: typing.Literal[True],
        order: Order | None = None,
        context: Context | None = None,
    ) -> str: ...

    @typing.overload
    def encode(
        self,
        obj: typing.Any,
        /,
        *,
        as_str: typing.Literal[False],
        order: Order | None = None,
        context: Context | None = None,
    ) -> bytes: ...

    def encode(
        self,
        obj: typing.Any,
        /,
        *,
        as_str: bool = True,
        order: Order | None = None,
        context: Context | None = None,
    ) -> str | bytes:
        buf = msgspec.json.encode(obj, enc_hook=self.enc_hook(context), order=order)
        return buf.decode() if as_str else buf

    def to_builtins(
        self,
        obj: typing.Any,
        /,
        *,
        str_keys: bool = False,
        builtin_types: typing.Iterable[type[typing.Any]] | None = None,
        order: Order | None = None,
        context: Context | None = None,
    ) -> typing.Any:
        return msgspec.to_builtins(
            obj,
            str_keys=str_keys,
            builtin_types=builtin_types,
            enc_hook=self.enc_hook(context),
            order=order,
        )

    def cast(self, obj: typing.Any, /) -> typing.Any:
        if (caster := self.cast_types.get(get_origin(obj))) is not None:
            return caster.cast(obj)
        return obj


encoder: typing.Final = Encoder()


__all__ = ("Encoder", "encoder", "to_builtins")
