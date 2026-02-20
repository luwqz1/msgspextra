from msgspextra.custom_types.hostname import Hostname, IDNHostname
from msgspextra.encoder import encoder


@encoder.add_enc_hook(IDNHostname)
@encoder.add_enc_hook(Hostname)
def hostname_enc_hook(obj: Hostname | IDNHostname, /) -> str:
    return str(obj)


__all__ = ("hostname_enc_hook",)
