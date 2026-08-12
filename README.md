# msgspex

A collection of [`msgspec`](https://github.com/jcrist/msgspec) extensions: custom types, cast helpers, `decode hooks`, `encode hooks` and deprecation system.

## Quick Start

```python
import msgspex
from msgspex.custom_types import Email, datetime

value = msgspex.decoder.decode('"user@example.com"', type=Email)
dt = msgspex.decoder.decode('"2024-01-02T03:04:05Z"', type=datetime)
payload = msgspex.encoder.encode(dt)
```

### Installing
```shell
pip install msgspex
uv add msgspex
poetry add msgspex
```

After `import msgspex`, all hooks and types are registered automatically.

## Custom Types

### 1. Types from kungfu

- `Option[T]` — optional value type based on `kungfu` (`Some | Nothing | msgspec.UnsetType`).

There is also decode-hook integration for `kungfu.Sum` (not a custom type, but supported by the decoder).

### 2. Types Derived from stdlib

- `date` — re-export of `datetime.date`.
- `datetime` — meta-type that covers `StringTimestampDatetime` (alias: `stimestamp`), `IntTimestampDatetime` (alias: `itimestamp`), `FloatTimestampDatetime` (alias: `ftimestamp`), `ISODatetime` (alias: `isodatetime`), and `datetime.datetime`.
- `timedelta` — subclass of `datetime.timedelta` with cast support.
- `StrEnum`, `IntEnum`, `FloatEnum`, `Enum` and `EnumMeta` — `enum` extensions for stable handling of unknown values.
- `Literal` — runtime type conceptually compatible with `typing.Literal`.
- `dataclasses.InitVar` — Passing vars to a `__post_init__` method.

### 3. OpenAPI-Oriented Types

- `Email` — `format: email`
- `IDNEmail` — `format: idn-email`
- `URI` — `format: uri`
- `URIReference` — `format: uri-reference`
- `IRI` — `format: iri`
- `IRIReference` — `format: iri-reference`
- `Hostname` — `format: hostname`
- `IDNHostname` — `format: idn-hostname`
- `IPv4` — `format: ipv4`
- `IPv6` — `format: ipv6`
- `JsonPointer` — `format: json-pointer`
- `RelativeJsonPointer` — `format: relative-json-pointer`
- `Regex` — `format: regex`
- `Int32`, `Int64` — range-limited integer types
- `Float32`, `Float64` — finite, range-limited floating-point types
- `UUID4` — uuid v4

`UUID`, `Decimal`, `date` and `time` already supported by `msgspec`.

## License
msgspex is [MIT licensed](https://github.com/luwqz1/msgspextra/blob/main/LICENSE)
