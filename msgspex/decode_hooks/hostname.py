import typing

from msgspex.custom_types.hostname import Hostname, IDNHostname
from msgspex.decoder import decoder


@decoder.add_dec_hook(IDNHostname)
@decoder.add_dec_hook(Hostname)
def hostname_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    return obj if isinstance(obj, tp) else tp(obj)


__all__ = ("hostname_dec_hook",)
