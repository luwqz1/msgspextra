import ipaddress
import typing

from msgspextra.custom_types.ip import IPv4, IPv6
from msgspextra.decoder import decoder


@decoder.add_dec_hook(IPv6)
@decoder.add_dec_hook(IPv4)
def ip_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    if isinstance(obj, tp):
        return obj

    if isinstance(obj, ipaddress.IPv4Address | ipaddress.IPv6Address):
        return tp(str(obj))

    return tp(obj)


__all__ = ("ip_dec_hook",)
