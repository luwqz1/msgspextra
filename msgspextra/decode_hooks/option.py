import typing

import msgspec
from kungfu.library import Sum
from kungfu.library.monad.option import NOTHING, Nothing, Some

from msgspextra.custom_types.option import Option
from msgspextra.decoder import decoder
from msgspextra.tools import fullname, is_common_type, type_check


@decoder.add_dec_hook(Some)
@decoder.add_dec_hook(Nothing)
@decoder.add_dec_hook(Option)
def option_dec_hook(
    tp: typing.Any,
    obj: typing.Any,
    /,
) -> Option[typing.Any] | msgspec.UnsetType:
    if obj is msgspec.UNSET or obj is NOTHING:
        return obj

    if obj is None:
        return NOTHING

    (value_type,) = typing.get_args(tp) or (typing.Any,)
    orig_value_type = typing.get_origin(value_type) or value_type
    orig_obj = obj

    if not isinstance(orig_obj, dict | list) and is_common_type(orig_value_type):
        if orig_value_type is Sum:
            obj = value_type(orig_obj)  # type: ignore
            orig_value_type = typing.get_args(value_type)

        if not type_check(orig_obj, orig_value_type):
            raise TypeError(
                f"Expected `{fullname(orig_value_type)}` or `builtins.None`, got `{fullname(orig_obj)}`.",
            )

        return Some(obj)  # type: ignore

    return Some(decoder.convert(orig_obj, type=value_type))  # type: ignore


__all__ = ("option_dec_hook",)
