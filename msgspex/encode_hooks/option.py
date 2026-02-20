import typing

import kungfu

from msgspex.encoder import encoder


@encoder.add_enc_hook(kungfu.Some)
@encoder.add_enc_hook(kungfu.Nothing)
def option_enc_hook(obj: kungfu.Option[typing.Any], /) -> typing.Any:
    return obj.unwrap_or_none()


__all__ = ("option_enc_hook",)
