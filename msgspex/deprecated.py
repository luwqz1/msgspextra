import functools
import typing
import warnings

from msgspex.tools import get_origin

_MODEL_FIELD_IS_DEPRECATED_ATTR: typing.Final = "__field_is_deprecated__"
_MODEL_IS_DEPRECATED_ATTR: typing.Final = "__model_is_deprecated__"
_MODEL_WARNING_DEPRECATION_META_ATTR: typing.Final = "__model_warning_deprecation_meta__"


def warn_deprecation(
    *,
    message: str,
    category: type[Warning] = PendingDeprecationWarning,
    stacklevel: int = 1,
) -> None:
    with warnings.catch_warnings(action="module", category=category):
        warnings.warn(message=message, category=category, stacklevel=stacklevel)


def field_deprecated(
    message: str,
    /,
    *,
    category: type[Warning] = PendingDeprecationWarning,
    stacklevel: int = 4,
) -> typing.Callable[..., typing.Any]:
    def decorator(f: typing.Callable[..., typing.Any], /) -> typing.Callable[..., typing.Any]:
        if not hasattr(f, _MODEL_FIELD_IS_DEPRECATED_ATTR):
            setattr(f, _MODEL_FIELD_IS_DEPRECATED_ATTR, True)

        is_warned = False

        @functools.wraps(f)
        def wrapper(obj: typing.Any, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            nonlocal is_warned

            if not is_warned:
                warn_deprecation(message=message, category=category, stacklevel=stacklevel)
                is_warned = True

            return f(obj, *args, **kwargs)

        return wrapper

    return decorator


def is_field_deprecated(obj: typing.Any, /, field_name: str | None = None) -> bool:
    if not field_name and isinstance(obj, property):
        return is_field_deprecated(obj.fget)

    if field_name and isinstance(get_origin(obj), type):
        return is_field_deprecated(getattr(obj, field_name, None))

    if callable(obj):
        return getattr(obj, _MODEL_FIELD_IS_DEPRECATED_ATTR, None) is True

    return False


def model_deprecated(
    message: str,
    /,
    *,
    category: type[Warning] = PendingDeprecationWarning,
    stacklevel: int = 4,
) -> typing.Callable[..., typing.Any]:
    def decorator(model: typing.Any, /) -> typing.Any:
        setattr(model, _MODEL_IS_DEPRECATED_ATTR, True)
        setattr(
            model,
            _MODEL_WARNING_DEPRECATION_META_ATTR,
            dict(
                message=message,
                category=category,
                stacklevel=stacklevel,
            ),
        )
        return model

    return decorator


def is_model_deprecated(model: typing.Any, /) -> bool:
    return getattr(model, _MODEL_IS_DEPRECATED_ATTR, None) is True


def get_model_warning_deprecation_meta(model: typing.Any, /) -> dict[str, typing.Any] | None:
    if not is_model_deprecated(model):
        return None
    return getattr(model, _MODEL_WARNING_DEPRECATION_META_ATTR, None)


__all__ = (
    "field_deprecated",
    "get_model_warning_deprecation_meta",
    "is_field_deprecated",
    "is_model_deprecated",
    "model_deprecated",
    "warn_deprecation",
)
