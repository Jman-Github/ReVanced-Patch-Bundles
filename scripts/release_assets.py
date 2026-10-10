"""Release asset rules independently implemented from External Bundles behavior.

Reference: https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/integrations/common/GitHostClient.kt
No upstream backend source is incorporated. See docs/source-attribution.md.
"""

import re
from collections.abc import Mapping
from pathlib import PurePosixPath
from urllib.parse import urlsplit

BUNDLE_TYPES = {".rvp": "ReVanced:V4", ".mpp": "Morphe:V1", ".jar": "ReVanced:V3"}


def release_assets(release):
    assets = release.get("assets", [])
    if isinstance(assets, Mapping):
        assets = assets.get("links", [])
    result = []
    for asset in assets if isinstance(assets, list) else []:
        if not isinstance(asset, Mapping):
            continue
        url = asset.get("browser_download_url") or asset.get("direct_asset_url") or asset.get("url")
        if not isinstance(url, str):
            continue
        parsed = urlsplit(url)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            result.append(
                {
                    "url": url,
                    "name": str(asset.get("name") or ""),
                    "provider_digest": asset.get("digest"),
                }
            )
    return result


def asset_extension(asset):
    """A concrete URL suffix wins over a host's human-readable asset title."""
    filename = urlsplit(asset["url"]).path.rsplit("/", 1)[-1]
    extension = PurePosixPath(filename).suffix.lower()
    if extension or ("." in filename[1:] and not filename.endswith(".")):
        return extension
    return PurePosixPath(asset.get("name", "").split("?", 1)[0].split("#", 1)[0]).suffix.lower()


def choose_patch_bundle(assets):
    """Prefer the first explicit bundle in provider order, then the first JAR."""
    for extensions in ({".rvp", ".mpp"}, {".jar"}):
        for asset in assets:
            if asset_extension(asset) in extensions:
                return asset
    return None


def _resource(url):
    parsed = urlsplit(url)
    return parsed.scheme.lower(), parsed.netloc.lower(), parsed.path


def _filename(asset, extension):
    path = urlsplit(asset["url"]).path
    if PurePosixPath(path).suffix.lower() == extension:
        return path.rsplit("/", 1)[-1]
    if asset_extension(asset) == extension:
        return asset.get("name", "").split("?", 1)[0].split("#", 1)[0].rsplit("/", 1)[-1]
    return None


def artifact_signature(download, assets):
    """Match URL/query first, then an unambiguous name; never guess across bundles."""
    assets = [{"url": item, "name": ""} if isinstance(item, str) else item for item in assets]
    candidates = [item for item in assets if asset_extension(item) in BUNDLE_TYPES]
    signatures = [item for item in assets if asset_extension(item) == ".asc"]
    bundle = next((item for item in candidates if item["url"] == download), None)
    if bundle is None:
        return None
    parsed = urlsplit(download)
    if PurePosixPath(parsed.path).suffix.lower() in BUNDLE_TYPES:
        exact = parsed._replace(path=parsed.path + ".asc").geturl()
        matches = [item for item in signatures if item["url"] == exact]
        if matches:
            return matches[0]["url"] if len(matches) == 1 else None
        path = _resource(download)
        expected = (*path[:2], path[2] + ".asc")
        matches = [item for item in signatures if _resource(item["url"]) == expected]
        same_query = [item for item in matches if urlsplit(item["url"]).query == parsed.query]
        if same_query:
            return same_query[0]["url"] if len(same_query) == 1 else None
        unique_path = sum(_resource(item["url"]) == path for item in candidates) == 1
        if matches:
            return matches[0]["url"] if len(matches) == 1 and unique_path else None
    name = _filename(bundle, asset_extension(bundle))
    if (
        name
        and sum(
            (_filename(item, asset_extension(item)) or "").lower() == name.lower()
            for item in candidates
        )
        == 1
    ):
        matches = [
            item
            for item in signatures
            if (_filename(item, ".asc") or "").lower() == name.lower() + ".asc"
        ]
        if matches:
            return matches[0]["url"] if len(matches) == 1 else None
    return signatures[0]["url"] if len(candidates) == 1 and signatures else None


def release_date(release):
    """Match each provider's release timestamp semantics."""
    if "released_at" in release:  # GitLab
        return release.get("released_at") or release.get("created_at")
    return release.get("created_at") or release.get("published_at")


def digest_matches(expected, actual, recorded=None):
    """Only a provider SHA-256 can be compared with our binary SHA-256."""
    if not isinstance(expected, str) or not expected.strip():
        return True
    value = expected.strip().lower()
    if value.startswith("sha256:"):
        value = value[7:]
    if not re.fullmatch(r"[a-f0-9]{64}", value):
        return expected == recorded
    return isinstance(actual, str) and value == actual.lower()
