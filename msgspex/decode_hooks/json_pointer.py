import typing

from msgspex.custom_types.json_pointer import JsonPointer, RelativeJsonPointer
from msgspex.decoder import decoder


@decoder.add_dec_hook(RelativeJsonPointer)
@decoder.add_dec_hook(JsonPointer)
def json_pointer_dec_hook(tp: typing.Any, obj: typing.Any, /) -> typing.Any:
    return obj if isinstance(obj, tp) else tp(obj)


__all__ = ("json_pointer_dec_hook",)
