from msgspex.custom_types.json_pointer import JsonPointer, RelativeJsonPointer
from msgspex.encoder import encoder


@encoder.add_enc_hook(RelativeJsonPointer)
@encoder.add_enc_hook(JsonPointer)
def json_pointer_enc_hook(obj: JsonPointer | RelativeJsonPointer, /) -> str:
    return str(obj)


__all__ = ("json_pointer_enc_hook",)
