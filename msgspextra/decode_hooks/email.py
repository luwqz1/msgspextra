import typing

from msgspextra.custom_types.email import Email, IDNEmail
from msgspextra.decoder import decoder


@decoder.add_dec_hook(IDNEmail)
@decoder.add_dec_hook(Email)
def email_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    return obj if isinstance(obj, tp) else tp(obj)


__all__ = ("email_dec_hook",)
