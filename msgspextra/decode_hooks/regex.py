import re
import typing

from msgspextra.custom_types.regex import Regex
from msgspextra.decoder import decoder


@decoder.add_dec_hook(Regex)
def regex_dec_hook(tp: type[Regex], obj: typing.Any, /) -> Regex:
    if isinstance(obj, tp):
        return obj

    if isinstance(obj, re.Pattern):
        return tp(obj.pattern)  # type: ignore

    return tp(obj)


__all__ = ("regex_dec_hook",)
