import typing

from msgspex.custom_types.enum import BaseEnumMeta
from msgspex.encoder import encoder


@encoder.add_abstract_enc_hook(BaseEnumMeta)
def enum_enc_hook(obj: BaseEnumMeta, /) -> typing.Any:
    return getattr(obj, "value")


__all__ = ("enum_enc_hook",)
