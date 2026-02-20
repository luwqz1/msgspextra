import typing

from msgspextra.custom_types.enum import BaseEnumMeta
from msgspextra.decoder import decoder


@decoder.add_abstract_dec_hook(BaseEnumMeta)
def enum_dec_hook(tp: type[BaseEnumMeta], obj: typing.Any, /) -> BaseEnumMeta:
    return tp(obj)  # type: ignore


__all__ = ("enum_dec_hook",)
