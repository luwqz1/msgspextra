import typing

from msgspex.custom_types.literal import _Literal  # type: ignore
from msgspex.decoder import decoder


@decoder.add_abstract_dec_hook(_Literal)
def literal_dec_hook(literal: type[_Literal], obj: typing.Any, /) -> typing.Any:
    if obj in literal.__args__:
        return obj

    raise TypeError(
        "Invalid literal value {!r} of either {}.".format(
            obj,
            literal.__args__[0] if len(literal.__args__) == 1 else (", ".join(f"`{x}`" for x in literal.__args__[:-1])) + f" or `{literal.__args__[-1]}`",
        )
    )


__all__ = ("literal_dec_hook",)
