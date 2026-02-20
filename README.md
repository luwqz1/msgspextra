# msgspextra

A collection of `msgspec` extensions: custom types, cast helpers, `decode hooks`, and `encode hooks`.

## Quick Start

```python
import msgspextra
from msgspextra.custom_types import Email, datetime

value = msgspextra.decoder.decode('"user@example.com"', type=Email)
dt = msgspextra.decoder.decode('"2024-01-02T03:04:05Z"', type=datetime)
payload = msgspextra.encoder.encode(dt)
```

After `import msgspextra`, all hooks and types are registered automatically.

## Custom Types

### 1. Types from kungfu

- `Option[T]` — optional value type based on `kungfu` (`Some | Nothing | msgspec.UnsetType`).

There is also decode-hook integration for `kungfu.Sum` (not a custom type, but supported by the decoder).

### 2. Types Derived from stdlib

- `date` — re-export of `datetime.date`.
- `datetime` — meta-type that covers `StringTimestampDatetime`, `IntTimestampDatetime`, `FloatTimestampDatetime`, `ISODatetime` (alias: `isodatetime`), and `datetime.datetime`.
- `timedelta` — subclass of `datetime.timedelta` with cast support.
- `StrEnum`, `IntEnum`, `FloatEnum`, `BaseEnumMeta` — `enum` extensions for stable handling of unknown values.
- `Literal` — runtime type conceptually compatible with `typing.Literal`.

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

`UUID` is not redefined here, because it is already supported by `msgspec`.
