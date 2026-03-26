import typing
from contextlib import contextmanager

import msgspec
from kungfu.library import Error, Ok, Result

from msgspex.tools import bundle, fullname, get_origin

type Context = dict[str, typing.Any]
type DecHook = typing.Callable[typing.Concatenate[typing.Any, typing.Any, ...], typing.Any]


def convert[T](
    obj: typing.Any,
    t: type[T],
    /,
    *,
    strict: bool = True,
    context: Context | None = None,
) -> Result[T, str]:
    try:
        return Ok(decoder.convert(obj, type=t, strict=strict, context=context))
    except msgspec.ValidationError:
        return Error(
            "Expected object of type `{}`, got `{}`.".format(
                fullname(t),
                fullname(obj),
            ),
        )


class Decoder:
    dec_hooks: dict[typing.Any, DecHook]
    abstract_dec_hooks: dict[typing.Any, DecHook]
    default_dec_hook: DecHook | None

    __slots__ = ("dec_hooks", "abstract_dec_hooks", "default_dec_hook")

    def __init__(self) -> None:
        self.dec_hooks = {}
        self.abstract_dec_hooks = {}
        self.default_dec_hook = None

    def __repr__(self) -> str:
        return "<{}: dec_hooks={!r}, abstract_dec_hooks={!r}, default_dec_hook={!r}>".format(
            type(self).__name__,
            self.dec_hooks,
            self.abstract_dec_hooks,
            self.default_dec_hook,
        )

    @typing.overload
    def __call__[T](
        self,
        type: type[T],
        context: Context | None = None,
    ) -> typing.ContextManager[msgspec.json.Decoder[T]]: ...

    @typing.overload
    def __call__(
        self,
        type: typing.Any,
        context: Context | None = None,
    ) -> typing.ContextManager[msgspec.json.Decoder[typing.Any]]: ...

    @typing.overload
    def __call__[T](
        self,
        type: type[T],
        *,
        strict: bool = True,
        context: Context | None = None,
    ) -> typing.ContextManager[msgspec.json.Decoder[T]]: ...

    @typing.overload
    def __call__(
        self,
        type: typing.Any,
        *,
        strict: bool = True,
        context: Context | None = None,
    ) -> typing.ContextManager[msgspec.json.Decoder[typing.Any]]: ...

    @contextmanager
    def __call__(
        self,
        type: typing.Any = object,
        *,
        strict: bool = True,
        context: Context | None = None,
    ) -> typing.Generator[msgspec.json.Decoder[typing.Any], typing.Any, None]:
        """Context manager returns an `msgspec.json.Decoder` object with passed the `dec_hook`."""
        yield msgspec.json.Decoder(
            type=typing.Any if type is object else type,
            strict=strict,
            dec_hook=self.dec_hook(context),
        )

    def add_dec_hook[T: DecHook](self, t: typing.Any, /) -> typing.Callable[[T], T]:
        def decorator(func: T, /) -> T:
            return self.dec_hooks.setdefault(get_origin(t), func)  # type: ignore

        return decorator

    def set_default_dec_hook[T: DecHook](self, dec_hook: T, /) -> T:
        self.default_dec_hook = dec_hook
        return dec_hook

    def add_abstract_dec_hook[T: DecHook](self, abstract_type: typing.Any, /) -> typing.Callable[[T], T]:
        def decorator(func: T, /) -> T:
            return self.abstract_dec_hooks.setdefault(get_origin(abstract_type), func)  # type: ignore

        return decorator

    def get_abstract_dec_hook(self, subtype: type[typing.Any], /) -> DecHook | None:
        for abstract, dec_hook in self.abstract_dec_hooks.items():
            if issubclass(subtype, abstract) or issubclass(type(subtype), abstract):
                return dec_hook

        return None

    def dec_hook(self, context: Context | None = None, /) -> DecHook:
        def inner(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
            origin_type = get_origin(tp)

            if (dec_hook_func := self.dec_hooks.get(origin_type)) is None and (
                dec_hook_func := (self.get_abstract_dec_hook(origin_type) or self.default_dec_hook)
            ) is None:
                raise NotImplementedError(
                    f"Not implemented decode hook for type `{fullname(origin_type)}`. You can implement decode hook for this type.",
                )

            return bundle(dec_hook_func, context or {}, start_idx=2)(tp, obj)

        return inner

    def convert[T](
        self,
        obj: typing.Any,
        /,
        *,
        type: type[T] = dict,
        strict: bool = True,
        from_attributes: bool = False,
        builtin_types: typing.Iterable[type[typing.Any]] | None = None,
        str_keys: bool = False,
        context: Context | None = None,
    ) -> T:
        return msgspec.convert(
            obj,
            type,
            strict=strict,
            from_attributes=from_attributes,
            dec_hook=self.dec_hook(context),
            builtin_types=builtin_types,
            str_keys=str_keys,
        )

    @typing.overload
    def decode(
        self,
        buf: str | bytes,
        /,
        *,
        context: Context | None = None,
    ) -> typing.Any: ...

    @typing.overload
    def decode[T](
        self,
        buf: str | bytes,
        /,
        *,
        type: type[T],
        context: Context | None = None,
    ) -> T: ...

    @typing.overload
    def decode(
        self,
        buf: str | bytes,
        /,
        *,
        type: typing.Any,
        context: Context | None = None,
    ) -> typing.Any: ...

    @typing.overload
    def decode[T](
        self,
        buf: str | bytes,
        /,
        *,
        type: type[T],
        strict: bool = True,
        context: Context | None = None,
    ) -> T: ...

    @typing.overload
    def decode(
        self,
        buf: str | bytes,
        /,
        *,
        type: typing.Any,
        strict: bool = True,
        context: Context | None = None,
    ) -> typing.Any: ...

    def decode(
        self,
        buf: str | bytes,
        /,
        *,
        type: typing.Any = object,
        strict: bool = True,
        context: Context | None = None,
    ) -> typing.Any:
        context = context or {}
        context["strict"] = strict
        return msgspec.json.decode(
            buf,
            type=typing.Any if type is object else type,
            strict=strict,
            dec_hook=self.dec_hook(context),
        )


decoder: typing.Final = Decoder()


__all__ = ("Decoder", "convert", "decoder")
