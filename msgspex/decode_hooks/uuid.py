import re
import typing
import uuid

from msgspex.custom_types.uuid import UUID4
from msgspex.decoder import decoder
from msgspex.tools import fullname

UUID4_PATTERN: typing.Final = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")


@decoder.add_dec_hook(UUID4)
def uuid4_dec_hook(__tp: type[UUID4], __obj: typing.Any) -> UUID4:
    try:
        obj = (
            __tp(bytes=__obj.bytes)
            if isinstance(__obj, uuid.UUID)
            else __tp(hex=__obj)
            if isinstance(__obj, str)
            else __tp(bytes=__obj)
            if isinstance(__obj, bytes)
            else None
        )
    except ValueError:
        raise TypeError("Invalid UUID format") from None

    if obj is None:
        raise TypeError(f"Excepted object of `str`, `bytes` or `uuid.UUID`, got `{fullname(__obj)}`")

    elif (obj.version is None and UUID4_PATTERN.match(str(obj)) is None) or (obj.version is not None and obj.version != 4):
        raise TypeError(f"Excepted `UUIDv4` format{f', got `UUIDv{obj.version}`' if obj.version is not None else ''}")

    return obj


__all__ = ("uuid4_dec_hook",)
