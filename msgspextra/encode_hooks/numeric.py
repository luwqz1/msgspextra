from msgspextra.custom_types.numeric import Float32, Float64, Int32, Int64
from msgspextra.encoder import encoder


@encoder.add_enc_hook(Int64)
@encoder.add_enc_hook(Int32)
def int_enc_hook(obj: Int32 | Int64, /) -> int:
    return int(obj)


@encoder.add_enc_hook(Float64)
@encoder.add_enc_hook(Float32)
def float_enc_hook(obj: Float32 | Float64, /) -> float:
    return float(obj)


__all__ = ("float_enc_hook", "int_enc_hook")
