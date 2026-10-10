"""PostgreSQL deterministic text ordering from generated glibc locale data.

The table reader is independently implemented. Locale data provenance and
format references are recorded in docs/source-attribution.md.
"""

import base64
import json
import struct
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _tables():
    data = json.loads(
        (Path(__file__).resolve().parents[1] / "shared/postgres-collation-data.json").read_text(
            encoding="utf-8"
        )
    )
    return {
        name: base64.b64decode(data[name])
        for name in ("rules", "table", "weights", "extra", "indirect")
    }


def _integer(data, offset):
    return struct.unpack_from("<i", data, offset)[0]


def _tokens(value, data):
    raw = value.encode("utf-8")
    cursor, result = 0, []
    while cursor < len(raw):
        packed = _integer(data["table"], raw[cursor] * 4)
        cursor += 1
        if packed < 0:
            offset = -packed
            while True:
                target = _integer(data["extra"], offset)
                length = data["extra"][offset + 4]
                start = offset + 5
                low = data["extra"][start : start + length]
                current = raw[cursor : cursor + length]
                if target >= 0 and current == low:
                    packed = target
                    cursor += length
                    break
                if target < 0:
                    high = data["extra"][start + length : start + 2 * length]
                    if len(current) == length and low <= current <= high:
                        difference = int.from_bytes(current, "big") - int.from_bytes(low, "big")
                        packed = _integer(data["indirect"], (-target + difference) * 4)
                        cursor += length
                        break
                offset = (start + length * (1 if target >= 0 else 2) + 3) & ~3
        levels, offset = [], packed & 0xFFFFFF
        for _ in range(4):
            length = data["weights"][offset]
            offset += 1
            levels.append(data["weights"][offset : offset + length])
            offset += length
        result.append((packed >> 24, levels))
    return result


def text_key(value, locale="en_US.utf8"):
    name = locale.lower().replace("-", "").replace("_", "").replace(".", "")
    if name in {"c", "posix", "cutf8"}:
        return value.encode("utf-8")
    if name != "enusutf8":
        raise ValueError("Unsupported PostgreSQL collation: " + locale)
    data = _tables()
    tokens = _tokens(value, data)
    levels = []
    for level in range(4):
        ordered, cursor = [], 0
        while cursor < len(tokens):
            end = cursor + 1
            if data["rules"][tokens[cursor][0] * 4 + level] & 2:
                while end < len(tokens) and data["rules"][tokens[end][0] * 4 + level] & 2:
                    end += 1
                run = list(reversed(tokens[cursor:end]))
                # libc strcoll skips the penultimate backward element when a
                # forward element follows the run; strxfrm does not.
                if end < len(tokens) and len(run) > 1:
                    del run[1]
                ordered.extend(run)
            else:
                ordered.append(tokens[cursor])
            cursor = end
        output, distance = [], 0
        for _, weights in ordered:
            distance += 1
            if not weights[level]:
                continue
            if data["rules"][level] & 4:
                output.append((distance, *weights[level]))
                distance = 0
            else:
                output.extend(weights[level])
        levels.append(tuple(output))
    return (bool(value), *levels, value.encode("utf-8"))
