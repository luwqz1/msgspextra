import typing
from annotationlib import type_repr

import msgspec
from kungfu.library import Error, Ok, Sum

from msgspex.decoder import convert, decoder
from msgspex.tools import fullname, get_origin, is_common_type, type_check


@decoder.add_dec_hook(Sum)
def sum_dec_hook(tp: type[typing.Any], obj: typing.Any, /) -> typing.Any:
    union_types = typing.get_args(tp)

    if isinstance(obj, dict):
        reverse = False
        models_fields_count: dict[type[msgspec.Struct], int] = {
            m: sum(1 for k in obj if k in m.__struct_fields__)  # type: ignore
            for m in union_types
            if issubclass(get_origin(m), msgspec.Struct)
        }
        union_types = tuple(t for t in union_types if t not in models_fields_count)

        if len(set(models_fields_count.values())) != len(models_fields_count.values()):
            models_fields_count = {m: len(m.__struct_fields__) for m in models_fields_count}
            reverse = True

        union_types = (
            *sorted(
                models_fields_count,
                key=lambda k: models_fields_count[k],
                reverse=reverse,
            ),
            *union_types,
        )

    if not isinstance(obj, dict | list) and any(is_common_type(t) and type_check(obj, t) for t in union_types):
        return tp(obj)  # type: ignore

    for t in union_types:
        match convert(obj, t):
            case Ok(value):
                return tp(value)  # type: ignore
            case Error(_):
                continue
            case _ as arg:  # type: ignore
                typing.assert_never(arg)

    raise TypeError(
        "Object of type `{}` doesn't belong to `{}[{}]`.".format(
            fullname(obj),
            "kungfu.Sum",
            ", ".join(type_repr(x) for x in union_types),
        )
    )


__all__ = ("sum_dec_hook",)
