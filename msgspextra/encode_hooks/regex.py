from msgspextra.custom_types.regex import Regex
from msgspextra.encoder import encoder


@encoder.add_enc_hook(Regex)
def regex_enc_hook(obj: Regex, /) -> str:
    return str(obj)


__all__ = ("regex_enc_hook",)
