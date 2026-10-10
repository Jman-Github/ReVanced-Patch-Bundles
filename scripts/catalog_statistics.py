"""Compact aggregate index for broad public patch statistics without scanning shards."""

import math

try:
    from scripts.postgres_collation import text_key
except ModuleNotFoundError:
    from postgres_collation import text_key


def patch_statistics(rows, bundles, locale="en_US.utf8"):
    # Validate the configured profile even when the catalog is empty.
    text_key("", locale)
    profile = locale.lower().replace("-", "").replace("_", "").replace(".", "")
    binary_locale = profile in {"c", "posix", "cutf8"}
    records = [
        {
            **row,
            "catalog_id": row["id"],
            "id": row["legacy_id"],
            "bundle_fk": bundles[row["bundle_id"]]["legacy_id"],
        }
        for row in rows
    ]
    columns = [
        "id",
        "catalog_id",
        "bundle_fk",
        "bundle_id",
        "source_id",
        "name",
        "description",
        "metadata_status",
        "patch_metadata_version",
        "use",
    ]
    result = {
        "count": len(records),
        "distinct": {},
        "nonnull": {},
        "aggregate": {},
        "columns": columns,
        "null_masks": {},
        "text_extrema": {name: {"min": {}, "max": {}} for name in ("C", "en_US.utf8")},
    }
    for row in records:
        mask = sum(1 << index for index, field in enumerate(columns) if row.get(field) is None)
        key = str(mask)
        result["null_masks"][key] = result["null_masks"].get(key, 0) + 1
    for field in columns:
        values = [row[field] for row in records if row.get(field) is not None]
        result["distinct"][field] = len(set(values))
        result["nonnull"][field] = len(values)
        # Histories repeat patch text across releases. Calculate each distinct
        # text key once, and reuse it for both extrema.
        extrema = {}
        if values:
            unique = set(values)
            if all(isinstance(value, str) for value in unique):
                keyed = [(text_key(value), value) for value in unique]
                utf8 = {"min": min(keyed)[1], "max": max(keyed)[1]}
                binary = {"min": min(unique), "max": max(unique)}
                for name, selected in (("C", binary), ("en_US.utf8", utf8)):
                    for op, value in selected.items():
                        result["text_extrema"][name][op][field] = value
                extrema = binary if binary_locale else utf8
            else:
                extrema = {"min": min(unique), "max": max(unique)}

        for op in [
            "min",
            "max",
            "sum",
            "avg",
            "variance",
            "var_pop",
            "var_samp",
            "stddev",
            "stddev_pop",
            "stddev_samp",
        ]:
            value = None
            if values:
                if op == "min":
                    value = extrema["min"]
                elif op == "max":
                    value = extrema["max"]
                elif all(isinstance(item, int | float) for item in values):
                    total = sum(values)
                    average = total / len(values)
                    squares = sum((item - average) ** 2 for item in values)
                    sample = op in {"variance", "var_samp", "stddev", "stddev_samp"}
                    variance = (
                        None
                        if sample and len(values) < 2
                        else (squares / (len(values) - int(sample)))
                    )
                    value = total if op == "sum" else average if op == "avg" else variance
                    if op.startswith("stddev") and variance is not None:
                        value = math.sqrt(variance)
            result["aggregate"].setdefault(op, {})[field] = value
    return result
