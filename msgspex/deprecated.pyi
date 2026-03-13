import typing
from warnings import deprecated as field_deprecated
from warnings import deprecated as model_deprecated

def warn_deprecation(
    *,
    message: str,
    category: type[Warning] = ...,
    stacklevel: int = ...,
) -> None: ...

@typing.overload
def is_field_deprecated(field: property, /) -> bool: ...
@typing.overload
def is_field_deprecated(type: type[typing.Any], field_name: str | None, /) -> bool: ...
@typing.overload
def is_field_deprecated(obj: typing.Any, field_name: str | None, /) -> bool: ...

def is_model_deprecated(model: typing.Any, /) -> bool: ...

class WarningDeprecationMeta(typing.TypedDict):
    message: str
    category: type[Warning]
    stacklevel: int

def get_model_warning_deprecation_meta(model: typing.Any, /) -> WarningDeprecationMeta | None: ...

__all__ = (
    "field_deprecated",
    "get_model_warning_deprecation_meta",
    "is_field_deprecated",
    "is_model_deprecated",
    "model_deprecated",
    "warn_deprecation",
)
