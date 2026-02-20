from msgspex.custom_types.datetime import timedelta
from msgspex.encoder import encoder


@encoder.add_enc_hook(timedelta)
def timedelta_enc_hook(obj: timedelta, /) -> int | float:
    return int(obj.total_seconds()) if getattr(obj, "is_from_int", False) is True else obj.total_seconds()


__all__ = ("timedelta_enc_hook",)
