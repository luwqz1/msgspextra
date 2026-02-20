from msgspex.custom_types.ip import IPv4, IPv6
from msgspex.encoder import encoder


@encoder.add_enc_hook(IPv6)
@encoder.add_enc_hook(IPv4)
def ip_enc_hook(obj: IPv4 | IPv6, /) -> str:
    return str(obj)


__all__ = ("ip_enc_hook",)
