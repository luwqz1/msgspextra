import typing

from msgspex.custom_types.numeric import Float32, Float64, Int32, Int64
from msgspex.decoder import decoder
from msgspex.tools import fullname


def _raise_type_error(
    tp: typing.Any,
    obj: typing.Any,
    /,
    *,
    ex: Exception | None = None,
) -> typing.NoReturn:
    message = f"Cannot validate object of type `{fullname(obj)}` into `{fullname(tp)}`."
    if ex is None:
        raise TypeError(message)
    raise TypeError(message) from ex


@decoder.add_dec_hook(Int64)
@decoder.add_dec_hook(Int32)
def int_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    if isinstance(obj, tp):
        return obj

    if isinstance(obj, bool):
        _raise_type_error(tp, obj)

    if isinstance(obj, str):
        obj = obj.strip()

    try:
        return tp(obj)
    except (TypeError, ValueError) as ex:
        _raise_type_error(tp, obj, ex=ex)


@decoder.add_dec_hook(Float64)
@decoder.add_dec_hook(Float32)
def float_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    if isinstance(obj, tp):
        return obj

    if isinstance(obj, bool):
        _raise_type_error(tp, obj)

    if isinstance(obj, str):
        obj = obj.strip()

    try:
        return tp(obj)
    except (TypeError, ValueError) as ex:
        _raise_type_error(tp, obj, ex=ex)


__all__ = ("float_dec_hook", "int_dec_hook")
