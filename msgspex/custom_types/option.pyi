from kungfu.library.monad import option

type NullableOption[T] = option.Option[T]
"""A type for annotating a value that is optional, but it `should NOT` be `excluded` when
converting to raw `JSON` if the value is `nullable`."""

type Option[T] = option.Option[T]
"""A type for annotating a value that is optional, but it `should` be `excluded` when
converting to raw `JSON` if the value is `nullable`."""

__all__ = ("NullableOption", "Option")
