import dataclasses
import typing
from annotationlib import type_repr
from collections import OrderedDict
from functools import cache

import msgspec
from kungfu.library import Ok, Sum

from msgspex.decoder import Context, convert, decoder
from msgspex.tools import fullname, get_origin


@cache
def get_sum_types_info(sum: typing.Any) -> SumTypesInfo:
    map: dict[type[typing.Any], tuple[typing.Any, ...]] = {}
    tagged_structs: dict[str, list[type[msgspec.Struct]]] = {}

    for arg in typing.get_args(sum):
        origin_arg = get_origin(arg)

        if issubclass(origin_arg, msgspec.Struct) and origin_arg.__struct_config__.tag_field is not None:
            tagged_structs.setdefault(origin_arg.__struct_config__.tag_field, []).append(origin_arg)
            continue

        if origin_arg not in map:
            map[origin_arg] = (arg,)
        else:
            map[origin_arg] += (arg,)

    return SumTypesInfo(
        map,
        typing.cast("dict[str, type[typing.Any]]", {k: typing.Union[*args] for k, args in tagged_structs.items()}),
    )


def order_args_by_suitable_structs(
    obj: dict[str, typing.Any],
    sum_args: tuple[typing.Any, ...],
) -> tuple[typing.Any, ...]:
    reverse = False
    models_fields_count: dict[type[msgspec.Struct], int] = {
        struct: sum(1 for k in obj if k in struct.__struct_fields__)  # type: ignore
        for arg in sum_args
        if issubclass(struct := get_origin(arg), msgspec.Struct)
    }
    sum_args = tuple(arg for arg in sum_args if arg not in models_fields_count)

    if len(set(models_fields_count.values())) != len(models_fields_count.values()):
        models_fields_count = {m: len(m.__struct_fields__) for m in models_fields_count}
        reverse = True

    return (
        *sorted(
            models_fields_count,
            key=lambda model: models_fields_count[model],
            reverse=reverse,
        ),
        *sum_args,
    )


@decoder.add_dec_hook(Sum)
def sum_dec_hook(
    tp: typing.Any,
    obj: typing.Any,
    /,
    context: Context,
    strict: bool = True,
) -> typing.Any:
    sum_args = args = typing.get_args(tp)
    sum_types_info = get_sum_types_info(tp)

    if isinstance(obj, dict):
        found_tagged_union = None

        for tag_field, tagged_union in sum_types_info.tagged_unions.items():
            if tag_field in obj:
                found_tagged_union = tagged_union
                break

        sum_args = typing.cast(
            "typing.Iterable[typing.Any]",
            order_args_by_suitable_structs(typing.cast("dict[str, typing.Any]", obj), sum_args)
            if found_tagged_union is None
            else (
                found_tagged_union,
                *(x for a in sum_types_info.map.values() for x in a),
            ),
        )
    elif head := sum_types_info.map.get(type(obj)):  # type: ignore
        sum_args = typing.cast("typing.Iterable[typing.Any]", OrderedDict.fromkeys((*head, *sum_args)))

    for candidate in sum_args:
        match convert(obj, candidate, strict=strict, context=context):
            case Ok(value):
                return tp(value)
            case _:
                pass

    raise TypeError(
        "Object of type `{}` doesn't belong to `{}[{}]`.".format(
            fullname(obj),
            "kungfu.Sum",
            ", ".join(type_repr(arg) for arg in args),
        )
    )


@dataclasses.dataclass(frozen=True, slots=True)
class SumTypesInfo:
    map: dict[type[typing.Any], tuple[typing.Any, ...]]
    tagged_unions: dict[str, type[typing.Any]]


__all__ = ("sum_dec_hook",)
