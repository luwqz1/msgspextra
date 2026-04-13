import typing

from kungfu.library import Sum

from msgspex.encoder import encoder


@encoder.add_enc_hook(Sum)
def sum_enc_hook(obj: typing.Any, /) -> typing.Any:
    return getattr(obj, "v")


__all__ = ("sum_enc_hook",)
