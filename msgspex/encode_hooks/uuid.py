from msgspex.custom_types.uuid import UUID4
from msgspex.encoder import encoder


@encoder.add_enc_hook(UUID4)
def uuid4_enc_hook(__obj: UUID4) -> str:
    return str(__obj)


__all__ = ("uuid4_enc_hook",)
