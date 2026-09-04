# ReVanced Patch Bundles

Patch bundle sources for ReVanced, Morphe, and related Android patching projects.

## Quick Links

- [Patch bundle URLs](#-patch-bundles-urls)
- [Compatible managers](#-compatible-managers)
- [Patch repositories](#-patch-repositories-in-use)
- [Integration repositories](#-integrations-repositories-in-use)
- [Suggestions, questions, and issues](#-suggestions-questions--issues)

## ❓ Overview

This repository tracks patch bundle sources for ReVanced, Morphe, and related patch ecosystems. It automatically checks the repositories listed [below](#-patch-bundles-urls) every 30 minutes and publishes bundle JSON links that can be imported into compatible managers.

Each bundle link points at the current metadata for one source. Depending on the bundle format, that metadata may reference patches plus integrations, or patches plus extensions. Importing one of these links lets the manager refresh the bundle whenever the tracked source updates.

## Bundle Labels

| Label | Meaning |
| --- | --- |
| `API v4` | Uses the newer ReVanced patch bundle format. |
| `Morphe` | Uses Morphe-compatible bundle metadata. |
| `Legacy` | Uses the older integration-based format and may not work in managers that only support newer bundle formats. |

## Patch Lists

For the actual patch contents, use the [Patch List Catalog](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md) or [Patch Explorer](https://patch-explorer.web.app/) by [Paresh-Maheshwari](https://gitlab.com/Paresh-Maheshwari).

If you know of another working ReVanced or Morphe patch repository that is not listed here, please open an [issue](https://github.com/Jman-Github/ReVanced-Patch-Bundles/issues).

## Release Channels

| Channel | Behavior |
| --- | --- |
| `Latest` | Tracks the newest release, including prereleases. If the newest release is a prerelease, this channel uses it. |
| `Stable` | Tracks the newest regular release and skips prereleases. |
| `Dev` | Tracks the newest prerelease and skips regular releases. |

> [!WARNING]
> Some stable or dev bundle links may be unavailable when the upstream repository has never published the matching release type. Those entries are marked as `N/A` in their respective `patch-bundle.json` files.

## 📋 Patch Bundles URLs

### 📦 ReVanced-Patches-Bundle [API v4]:
[🧩 ReVanced Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-revanced-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/revanced-patch-bundles/revanced-latest-patches-bundle.json```

**Stable:** ```N/A (No need for this, already built in to all ReVanced Managers)```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/revanced-patch-bundles/revanced-dev-patches-bundle.json```
</details>

---
### 📦 Inotia00-Patches-Bundle [API v4]:
[🧩 Inotia00 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-inotia00-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/inotia00-patch-bundles/inotia00-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/inotia00-patch-bundles/inotia00-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/inotia00-patch-bundles/inotia00-dev-patches-bundle.json```
</details>

---
### 📦 ProGuard-Patches-Bundle [Morphe]:
[🧩 ProGuard Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-proguard-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/proguard-patch-bundles/proguard-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/proguard-patch-bundles/proguard-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/proguard-patch-bundles/proguard-dev-patches-bundle.json```
</details>

---
### 📦 MTGA-Patches-Bundle [API v4]:
[🧩 MTGA Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-mtga-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/mtga-patch-bundles/mtga-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/mtga-patch-bundles/mtga-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/mtga-patch-bundles/mtga-dev-patches-bundle.json```
</details>

---
### 📦 Lain-Patches-Bundle [Morphe]:
[🧩 Lain Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-lain-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lain-patch-bundles/lain-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lain-patch-bundles/lain-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lain-patch-bundles/lain-dev-patches-bundle.json```
</details>

---
### 📦 Edge-Morphe-Patches-Bundle [Morphe]:
[🧩 Edge-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-edge-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/edge-morphe-patch-bundles/edge-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/edge-morphe-patch-bundles/edge-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/edge-morphe-patch-bundles/edge-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Anddea-Patches-Bundle [Morphe]:
[🧩 Anddea Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-anddea-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anddea-patch-bundles/anddea-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anddea-patch-bundles/anddea-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anddea-patch-bundles/anddea-dev-patches-bundle.json```
</details>

---
### 📦 Piko-Patches-Bundle [Morphe]:
[🧩 Piko Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-piko-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/piko-patch-bundles/piko-latest-patches-bundle.json``` - API v4

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/piko-patch-bundles/piko-stable-patches-bundle.json``` - API v3

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/piko-patch-bundles/piko-dev-patches-bundle.json``` - API v4
</details>

---
### 📦 BiliRoamingM-Patches-Bundle [Legacy]:
[🧩 BiliRoamingM Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-biliroamingm-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/biliroamingm-patch-bundles/biliroamingm-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/biliroamingm-patch-bundles/biliroamingm-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/biliroamingm-patch-bundles/biliroamingm-dev-patches-bundle.json```
</details>

---
### 📦 Slenderman00-Patches-Bundle [API v4]:
[🧩 Slenderman00 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-slenderman00-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/slenderman00-patch-bundles/slenderman00-latest-patches-bundle.json``` - API v4

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/slenderman00-patch-bundles/slenderman00-stable-patches-bundle.json``` - API v3

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/slenderman00-patch-bundles/slenderman00-dev-patches-bundle.json``` - API v4
</details>

---
### 📦 Privacy-Patches-Bundle [API v4]:
[🧩 Privacy Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-privacy-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/privacy-patch-bundles/privacy-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/privacy-patch-bundles/privacy-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/privacy-patch-bundles/privacy-dev-patches-bundle.json```
</details>

---
### 📦 Experimental-Patches-Bundle [API v4]:
[🧩 Experimental Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-experimental-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/experimental-patch-bundles/experimental-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/experimental-patch-bundles/experimental-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/experimental-patch-bundles/experimental-dev-patches-bundle.json```
</details>

---
### 📦 Dropped-Patches-Bundle [API v4]:
[🧩 Dropped Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dropped-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dropped-patch-bundles/dropped-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dropped-patch-bundles/dropped-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dropped-patch-bundles/dropped-dev-patches-bundle.json```
</details>

---
### 📦 Kitadai31-Patches-Bundle [API v4]:
[🧩 Kitadai31 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kitadai31-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kitadai31-patch-bundles/kitadai31-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kitadai31-patch-bundles/kitadai31-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kitadai31-patch-bundles/kitadai31-dev-patches-bundle.json```
</details>

---
### 📦 BholeyKaBhakt-Patches-Bundle [Morphe]:
[🧩 BholeyKaBhakt Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bholeykabhakt-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bholeykabhakt-patch-bundles/bholeykabhakt-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bholeykabhakt-patch-bundles/bholeykabhakt-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bholeykabhakt-patch-bundles/bholeykabhakt-dev-patches-bundle.json```
</details>

---
### 📦 Andronedev-Patches-Bundle [Morphe]:
[🧩 Andronedev Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-andronedev-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/andronedev-patch-bundles/andronedev-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/andronedev-patch-bundles/andronedev-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/andronedev-patch-bundles/andronedev-dev-patches-bundle.json```
</details>

---
### 📦 ReX-Patches-Bundle [API v4]:
[🧩 ReX Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rex-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rex-patch-bundles/rex-latest-patches-bundle.json``` - API v4

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rex-patch-bundles/rex-stable-patches-bundle.json``` - API v3

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rex-patch-bundles/rex-dev-patches-bundle.json``` - API v4
</details>

---
### 📦 Rufusin-Patches-Bundle [API v4]:
[🧩 Rufusin Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rufusin-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rufusin-patch-bundles/rufusin-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rufusin-patch-bundles/rufusin-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rufusin-patch-bundles/rufusin-dev-patches-bundle.json```
</details>

---
### 📦 Twitter-Patches-Bundle [Legacy]:
[🧩 Twitter Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-twitter-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/twitter-patch-bundles/twitter-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/twitter-patch-bundles/twitter-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/twitter-patch-bundles/twitter-dev-patches-bundle.json```
</details>

---
### 📦 Wyse--Patches-Bundle [Legacy]:
[🧩 Wyse- Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-wyse--bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/wyse--patch-bundles/wyse--latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/wyse--patch-bundles/wyse--stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/wyse--patch-bundles/wyse--dev-patches-bundle.json```
</details>

---
### 📦 1fexd-Patches-Bundle [Legacy]:
[🧩 1fexd Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-1fexd-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/1fexd-patch-bundles/1fexd-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/1fexd-patch-bundles/1fexd-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/1fexd-patch-bundles/1fexd-dev-patches-bundle.json```
</details>

---
### 📦 Xrogers-Patches-Bundle [Legacy]:
[🧩 Xrogers Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-xrogers-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xrogers-patch-bundles/xrogers-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xrogers-patch-bundles/xrogers-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xrogers-patch-bundles/xrogers-dev-patches-bundle.json```
</details>

---
### 📦 D4n3436-Patches-Bundle [Legacy]:
[🧩 D4n3436 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-d4n3436-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d4n3436-patch-bundles/d4n3436-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d4n3436-patch-bundles/d4n3436-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d4n3436-patch-bundles/d4n3436-dev-patches-bundle.json```
</details>

---
### 📦 AyushTNM-Patches-Bundle [Legacy]:
[🧩 AyushTNM Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ayushtnm-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ayushtnm-patch-bundles/ayushtnm-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ayushtnm-patch-bundles/ayushtnm-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ayushtnm-patch-bundles/ayushtnm-dev-patches-bundle.json```
</details>

---
### 📦 Arsclib-Patches-Bundle [Legacy]:
[🧩 Arsclib Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-arsclib-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/arsclib-patch-bundles/arsclib-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/arsclib-patch-bundles/arsclib-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/arsclib-patch-bundles/arsclib-dev-patches-bundle.json```
</details>

---
### 📦 LennyRBLX-Patches-Bundle [API v4]:
[🧩 LennyRBLX Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-lennyrblx-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lennyRBLX-patch-bundles/lennyRBLX-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lennyRBLX-patch-bundles/lennyRBLX-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lennyRBLX-patch-bundles/lennyRBLX-dev-patches-bundle.json```
</details>

---
### 📦 Korhelyleves-Patches-Bundle [API v4]:
[🧩 Korhelyleves Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-korhelyleves-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/korhelyleves-patch-bundles/korhelyleves-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/korhelyleves-patch-bundles/korhelyleves-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/korhelyleves-patch-bundles/korhelyleves-dev-patches-bundle.json```
</details>

---
### 📦 Taknok-Patches-Bundle [API v4]:
[🧩 Taknok Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-taknok-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/taknok-patch-bundles/taknok-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/taknok-patch-bundles/taknok-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/taknok-patch-bundles/taknok-dev-patches-bundle.json```
</details>

---
### 📦 Faith001-Patches-Bundle [API v4]:
[🧩 Faith001 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-faith001-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/faith001-patch-bundles/faith001-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/faith001-patch-bundles/faith001-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/faith001-patch-bundles/faith001-dev-patches-bundle.json```
</details>

---
### 📦 Forsyth47-Patches-Bundle [API v4]:
[🧩 Forsyth47 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-forsyth47-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/forsyth47-patch-bundles/forsyth47-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/forsyth47-patch-bundles/forsyth47-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/forsyth47-patch-bundles/forsyth47-dev-patches-bundle.json```
</details>

---
### 📦 Brosssh-Patches-Bundle [Morphe]:
[🧩 Brosssh Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-brosssh-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/brosssh-patch-bundles/brosssh-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/brosssh-patch-bundles/brosssh-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/brosssh-patch-bundles/brosssh-dev-patches-bundle.json```
</details>

---
### 📦 Quantro100-Patches-Bundle [Morphe]:
[🧩 Quantro100 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-quantro100-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/quantro100-patch-bundles/quantro100-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/quantro100-patch-bundles/quantro100-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/quantro100-patch-bundles/quantro100-dev-patches-bundle.json```
</details>

---
### 📦 4831c0-Patches-Bundle [API v4]:
[🧩 4831c0 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-4831c0-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/4831c0-patch-bundles/4831c0-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/4831c0-patch-bundles/4831c0-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/4831c0-patch-bundles/4831c0-dev-patches-bundle.json```
</details>

---
### 📦 Chiggi-Patches-Bundle [Morphe]:
[🧩 Chiggi Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-chiggi-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chiggi-patch-bundles/chiggi-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chiggi-patch-bundles/chiggi-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chiggi-patch-bundles/chiggi-dev-patches-bundle.json```
</details>

---
### 📦 Bakasura-Patches-Bundle [API v4]:
[🧩 Bakasura Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bakasura-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bakasura-patch-bundles/bakasura-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bakasura-patch-bundles/bakasura-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bakasura-patch-bundles/bakasura-dev-patches-bundle.json```
</details>

---
### 📦 LaKaka-Patches-Bundle [Morphe]:
[🧩 LaKaka Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-lakaka-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lakaka-patch-bundles/lakaka-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lakaka-patch-bundles/lakaka-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lakaka-patch-bundles/lakaka-dev-patches-bundle.json```
</details>

---
### 📦 LeeeeT-Patches-Bundle [API v4]:
[🧩 LeeeeT Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-leeeet-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/leeeet-patch-bundles/leeeet-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/leeeet-patch-bundles/leeeet-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/leeeet-patch-bundles/leeeet-dev-patches-bundle.json```
</details>

---
### 📦 Vernoxvernax-Patches-Bundle [API v4]:
[🧩 Vernoxvernax Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-vernoxvernax-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vernoxvernax-patch-bundles/vernoxvernax-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vernoxvernax-patch-bundles/vernoxvernax-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vernoxvernax-patch-bundles/vernoxvernax-dev-patches-bundle.json```
</details>

---
### 📦 EE-Morphe-Patches-Bundle [Morphe]:
[🧩 EE-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ee-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ee-morphe-patch-bundles/ee-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ee-morphe-patch-bundles/ee-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ee-morphe-patch-bundles/ee-morphe-dev-patches-bundle.json```
</details>

---
### 📦 X-Shim-Patches-Bundle [Morphe]:
[🧩 X-Shim Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-x-shim-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/x-shim-patch-bundles/x-shim-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/x-shim-patch-bundles/x-shim-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/x-shim-patch-bundles/x-shim-dev-patches-bundle.json```
</details>

---
### 📦 Pepper-Morphe-Patches-Bundle [Morphe]:
[🧩 Pepper-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-pepper-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pepper-morphe-patch-bundles/pepper-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pepper-morphe-patch-bundles/pepper-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pepper-morphe-patch-bundles/pepper-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Fin-Tweaks-Patches-Bundle [Morphe]:
[🧩 Fin-Tweaks Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-fin-tweaks-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/fin-tweaks-patch-bundles/fin-tweaks-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/fin-tweaks-patch-bundles/fin-tweaks-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/fin-tweaks-patch-bundles/fin-tweaks-dev-patches-bundle.json```
</details>

---
### 📦 Kondratjev-Patches-Bundle [Morphe]:
[🧩 Kondratjev Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kondratjev-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kondratjev-patch-bundles/kondratjev-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kondratjev-patch-bundles/kondratjev-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kondratjev-patch-bundles/kondratjev-dev-patches-bundle.json```
</details>

---
### 📦 Hoo-dles-Patches-Bundle [Morphe]:
[🧩 Hoo-dles Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hoo-dles-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hoo-dles-patch-bundles/hoo-dles-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hoo-dles-patch-bundles/hoo-dles-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hoo-dles-patch-bundles/hoo-dles-dev-patches-bundle.json```
</details>

---
### 📦 VinceTheProgrammer-Patches-Bundle [API v4]:
[🧩 VinceTheProgrammer Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-vincetheprogrammer-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vinceTheProgrammer-patch-bundles/vinceTheProgrammer-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vinceTheProgrammer-patch-bundles/vinceTheProgrammer-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vinceTheProgrammer-patch-bundles/vinceTheProgrammer-dev-patches-bundle.json```
</details>

---
### 📦 Hepolise-Patches-Bundle [Legacy]:
[🧩 Hepolise Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hepolise-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hepolise-patch-bundles/hepolise-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hepolise-patch-bundles/hepolise-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hepolise-patch-bundles/hepolise-dev-patches-bundle.json```
</details>

---
### 📦 Kangrio-Patches-Bundle [API v4]:
[🧩 Kangrio Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kangrio-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kangrio-patch-bundles/kangrio-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kangrio-patch-bundles/kangrio-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kangrio-patch-bundles/kangrio-dev-patches-bundle.json```
</details>

---
### 📦 Tosox-Patches-Bundle [API v4]:
[🧩 Tosox Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-tosox-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tosox-patch-bundles/tosox-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tosox-patch-bundles/tosox-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tosox-patch-bundles/tosox-dev-patches-bundle.json```
</details>

---
### 📦 HZbutcoding-Patches-Bundle [API v4]:
[🧩 HZbutcoding Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hzbutcoding-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hzbutcoding-patch-bundles/hzbutcoding-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hzbutcoding-patch-bundles/hzbutcoding-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hzbutcoding-patch-bundles/hzbutcoding-dev-patches-bundle.json```
</details>

---
### 📦 Lluni-Patches-Bundle [API v4]:
[🧩 Lluni Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-lluni-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lluni-patch-bundles/lluni-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lluni-patch-bundles/lluni-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lluni-patch-bundles/lluni-dev-patches-bundle.json```
</details>

---
### 📦 Bawr-Patches-Bundle [API v4]:
[🧩 Bawr Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bawr-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bawr-patch-bundles/bawr-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bawr-patch-bundles/bawr-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bawr-patch-bundles/bawr-dev-patches-bundle.json```
</details>

---
### 📦 Burgers1312-Patches-Bundle [API v4]:
[🧩 Burgers1312 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-burgers1312-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/burgers1312-patch-bundles/burgers1312-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/burgers1312-patch-bundles/burgers1312-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/burgers1312-patch-bundles/burgers1312-dev-patches-bundle.json```
</details>

---
### 📦 AmpleReVanced-Patches-Bundle [Morphe]:
[🧩 AmpleReVanced Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-amplerevanced-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/amplerevanced-patch-bundles/amplerevanced-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/amplerevanced-patch-bundles/amplerevanced-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/amplerevanced-patch-bundles/amplerevanced-dev-patches-bundle.json```
</details>

---
### 📦 Liaralabs-Patches-Bundle [API v4]:
[🧩 Liaralabs Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-liaralabs-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/liaralabs-patch-bundles/liaralabs-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/liaralabs-patch-bundles/liaralabs-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/liaralabs-patch-bundles/liaralabs-dev-patches-bundle.json```
</details>

---
### 📦 Morphe-Patches-Bundle [Morphe]:
[🧩 Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-patch-bundles/morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-patch-bundles/morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-patch-bundles/morphe-dev-patches-bundle.json```
</details>

---
### 📦 Patcheddit-Patches-Bundle [Morphe]:
[🧩 Patcheddit Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-patcheddit-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/patcheddit-patch-bundles/patcheddit-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/patcheddit-patch-bundles/patcheddit-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/patcheddit-patch-bundles/patcheddit-dev-patches-bundle.json```
</details>

---
### 📦 RVX-Morphed-Patches-Bundle [Morphe]:
[🧩 RVX-Morphed Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rvx-morphed-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rvx-morphed-patch-bundles/rvx-morphed-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rvx-morphed-patch-bundles/rvx-morphed-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rvx-morphed-patch-bundles/rvx-morphed-dev-patches-bundle.json```
</details>

---
### 📦 Blazskufca-Patches-Bundle [API v4]:
[🧩 Blazskufca Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-blazskufca-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/blazskufca-patch-bundles/blazskufca-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/blazskufca-patch-bundles/blazskufca-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/blazskufca-patch-bundles/blazskufca-dev-patches-bundle.json```
</details>

---
### 📦 IMXEren-Patches-Bundle [Morphe]:
[🧩 IMXEren Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-imxeren-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imxeren-patch-bundles/imxeren-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imxeren-patch-bundles/imxeren-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imxeren-patch-bundles/imxeren-dev-patches-bundle.json```
</details>

---
### 📦 Almewty-Patches-Bundle [Morphe]:
[🧩 Almewty Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-almewty-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/almewty-patch-bundles/almewty-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/almewty-patch-bundles/almewty-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/almewty-patch-bundles/almewty-dev-patches-bundle.json```
</details>

---
### 📦 Anddea-Morphed-Patches-Bundle [Morphe]:
[🧩 Anddea-Morphed Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-anddea-morphed-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anddea-morphed-patch-bundles/anddea-morphed-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anddea-morphed-patch-bundles/anddea-morphed-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anddea-morphed-patch-bundles/anddea-morphed-dev-patches-bundle.json```
</details>

---
### 📦 RookieEnough-Patches-Bundle [Morphe]:
[🧩 RookieEnough Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rookieenough-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rookieenough-patch-bundles/rookieenough-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rookieenough-patch-bundles/rookieenough-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rookieenough-patch-bundles/rookieenough-dev-patches-bundle.json```
</details>

---
### 📦 Adobo-Patches-Bundle [Morphe]:
[🧩 Adobo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-adobo-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/adobo-patch-bundles/adobo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/adobo-patch-bundles/adobo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/adobo-patch-bundles/adobo-dev-patches-bundle.json```
</details>

---
### 📦 Alexvbp-Patches-Bundle [API v4]:
[🧩 Alexvbp Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-alexvbp-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alexvbp-patch-bundles/alexvbp-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alexvbp-patch-bundles/alexvbp-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alexvbp-patch-bundles/alexvbp-dev-patches-bundle.json```
</details>

---
### 📦 Docbt-Patches-Bundle [Morphe]:
[🧩 Docbt Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-docbt-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/docbt-patch-bundles/docbt-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/docbt-patch-bundles/docbt-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/docbt-patch-bundles/docbt-dev-patches-bundle.json```
</details>

---
### 📦 LoV432-Patches-Bundle [API v4]:
[🧩 LoV432 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-lov432-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lov432-patch-bundles/lov432-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lov432-patch-bundles/lov432-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lov432-patch-bundles/lov432-dev-patches-bundle.json```
</details>

---
### 📦 PixelPusher247-Patches-Bundle [Morphe]:
[🧩 PixelPusher247 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-pixelpusher247-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pixelpusher247-patch-bundles/pixelpusher247-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pixelpusher247-patch-bundles/pixelpusher247-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pixelpusher247-patch-bundles/pixelpusher247-dev-patches-bundle.json```
</details>

---
### 📦 Rabilrbl-Patches-Bundle [Morphe]:
[🧩 Rabilrbl Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rabilrbl-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rabilrbl-patch-bundles/rabilrbl-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rabilrbl-patch-bundles/rabilrbl-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rabilrbl-patch-bundles/rabilrbl-dev-patches-bundle.json```
</details>

---
### 📦 Jasonwu1994-Patches-Bundle [Morphe]:
[🧩 Jasonwu1994 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jasonwu1994-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jasonwu1994-patch-bundles/jasonwu1994-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jasonwu1994-patch-bundles/jasonwu1994-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jasonwu1994-patch-bundles/jasonwu1994-dev-patches-bundle.json```
</details>

---
### 📦 RealCyberwash-Patches-Bundle [Morphe]:
[🧩 RealCyberwash Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-realcyberwash-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/realcyberwash-patch-bundles/realcyberwash-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/realcyberwash-patch-bundles/realcyberwash-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/realcyberwash-patch-bundles/realcyberwash-dev-patches-bundle.json```
</details>

---
### 📦 Paresh-Maheshwari-Patches-Bundle [Morphe]:
[🧩 Paresh-Maheshwari Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-paresh-maheshwari-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/paresh-maheshwari-patch-bundles/paresh-maheshwari-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/paresh-maheshwari-patch-bundles/paresh-maheshwari-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/paresh-maheshwari-patch-bundles/paresh-maheshwari-dev-patches-bundle.json```
</details>

---
### 📦 Binarymend-Patches-Bundle [Morphe]:
[🧩 Binarymend Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-binarymend-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/binarymend-patch-bundles/binarymend-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/binarymend-patch-bundles/binarymend-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/binarymend-patch-bundles/binarymend-dev-patches-bundle.json```
</details>

---
### 📦 Polka-Bear-Patches-Bundle [Morphe]:
[🧩 Polka-Bear Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-polka-bear-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/polka-bear-patch-bundles/polka-bear-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/polka-bear-patch-bundles/polka-bear-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/polka-bear-patch-bundles/polka-bear-dev-patches-bundle.json```
</details>

---
### 📦 Eyalm2000-Patches-Bundle [Morphe]:
[🧩 Eyalm2000 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-eyalm2000-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/eyalm2000-patch-bundles/eyalm2000-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/eyalm2000-patch-bundles/eyalm2000-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/eyalm2000-patch-bundles/eyalm2000-dev-patches-bundle.json```
</details>

---
### 📦 Vladon-Patches-Bundle [Morphe]:
[🧩 Vladon Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-vladon-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vladon-patch-bundles/vladon-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vladon-patch-bundles/vladon-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vladon-patch-bundles/vladon-dev-patches-bundle.json```
</details>

---
### 📦 Ariecos-Patches-Bundle [Morphe]:
[🧩 Ariecos Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ariecos-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ariecos-patch-bundles/ariecos-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ariecos-patch-bundles/ariecos-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ariecos-patch-bundles/ariecos-dev-patches-bundle.json```
</details>

---
### 📦 Alim-Zanibekov-Patches-Bundle [API v4]:
[🧩 Alim-Zanibekov Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-alim-zanibekov-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alim-zanibekov-patch-bundles/alim-zanibekov-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alim-zanibekov-patch-bundles/alim-zanibekov-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alim-zanibekov-patch-bundles/alim-zanibekov-dev-patches-bundle.json```
</details>

---
### 📦 Daboynb-Patches-Bundle [API v4]:
[🧩 Daboynb Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-daboynb-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/daboynb-patch-bundles/daboynb-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/daboynb-patch-bundles/daboynb-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/daboynb-patch-bundles/daboynb-dev-patches-bundle.json```
</details>

---
### 📦 Joristdh-Patches-Bundle [Morphe]:
[🧩 Joristdh Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-joristdh-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/joristdh-patch-bundles/joristdh-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/joristdh-patch-bundles/joristdh-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/joristdh-patch-bundles/joristdh-dev-patches-bundle.json```
</details>

---
### 📦 Meridianfresco-Patches-Bundle [Morphe]:
[🧩 Meridianfresco Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-meridianfresco-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/meridianfresco-patch-bundles/meridianfresco-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/meridianfresco-patch-bundles/meridianfresco-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/meridianfresco-patch-bundles/meridianfresco-dev-patches-bundle.json```
</details>

---
### 📦 Loskutov-Patches-Bundle [Morphe]:
[🧩 Loskutov Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-loskutov-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/loskutov-patch-bundles/loskutov-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/loskutov-patch-bundles/loskutov-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/loskutov-patch-bundles/loskutov-dev-patches-bundle.json```
</details>

---
### 📦 Kareemlukitomo-Patches-Bundle [Morphe]:
[🧩 Kareemlukitomo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kareemlukitomo-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kareemlukitomo-patch-bundles/kareemlukitomo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kareemlukitomo-patch-bundles/kareemlukitomo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kareemlukitomo-patch-bundles/kareemlukitomo-dev-patches-bundle.json```
</details>

---
### 📦 Abhis1n-Patches-Bundle [Morphe]:
[🧩 Abhis1n Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-abhis1n-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abhis1n-patch-bundles/abhis1n-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abhis1n-patch-bundles/abhis1n-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abhis1n-patch-bundles/abhis1n-dev-patches-bundle.json```
</details>

---
### 📦 PawiX25-Patches-Bundle [Morphe]:
[🧩 PawiX25 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-PawiX25-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/PawiX25-patch-bundles/PawiX25-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/PawiX25-patch-bundles/PawiX25-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/PawiX25-patch-bundles/PawiX25-dev-patches-bundle.json```
</details>

---
### 📦 Ameenalasady-Patches-Bundle [Morphe]:
[🧩 Ameenalasady Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-Ameenalasady-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/Ameenalasady-patch-bundles/Ameenalasady-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/Ameenalasady-patch-bundles/Ameenalasady-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/Ameenalasady-patch-bundles/Ameenalasady-dev-patches-bundle.json```
</details>

---
### 📦 Xob0t-Patches-Bundle [Morphe]:
[🧩 Xob0t Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-xob0t-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xob0t-patch-bundles/xob0t-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xob0t-patch-bundles/xob0t-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xob0t-patch-bundles/xob0t-dev-patches-bundle.json```
</details>

---
### 📦 Bannerhub-Patches-Bundle [Morphe]:
[🧩 Bannerhub Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bannerhub-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bannerhub-patch-bundles/bannerhub-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bannerhub-patch-bundles/bannerhub-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bannerhub-patch-bundles/bannerhub-dev-patches-bundle.json```
</details>

---
### 📦 Eksi-Patches-Bundle [Morphe]:
[🧩 Eksi Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-eksi-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/eksi-patch-bundles/eksi-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/eksi-patch-bundles/eksi-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/eksi-patch-bundles/eksi-dev-patches-bundle.json```
</details>

---
### 📦 Ameen-Morphe-Patches-Bundle [Morphe]:
[🧩 Ameen-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ameen-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ameen-morphe-patch-bundles/ameen-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ameen-morphe-patch-bundles/ameen-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ameen-morphe-patch-bundles/ameen-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Kolaron-Patches-Bundle [Morphe]:
[🧩 Kolaron Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kolaron-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kolaron-patch-bundles/kolaron-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kolaron-patch-bundles/kolaron-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kolaron-patch-bundles/kolaron-dev-patches-bundle.json```
</details>

---
### 📦 ImmortalZeus-Patches-Bundle [Morphe]:
[🧩 ImmortalZeus Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-immortalzeus-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ImmortalZeus-patch-bundles/ImmortalZeus-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ImmortalZeus-patch-bundles/ImmortalZeus-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ImmortalZeus-patch-bundles/ImmortalZeus-dev-patches-bundle.json```

</details>

### 📦 Ajstrick81-AndroidTV-Patches-Bundle [Morphe]:
[🧩 Ajstrick81-AndroidTV Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ajstrick81-androidtv-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ajstrick81-androidtv-patch-bundles/ajstrick81-androidtv-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ajstrick81-androidtv-patch-bundles/ajstrick81-androidtv-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ajstrick81-androidtv-patch-bundles/ajstrick81-androidtv-dev-patches-bundle.json```
</details>

---
### 📦 Icysymmetra-TikTok-Patches-Bundle [Morphe]:
[🧩 Icysymmetra-TikTok Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-icysymmetra-tiktok-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/icysymmetra-tiktok-patch-bundles/icysymmetra-tiktok-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/icysymmetra-tiktok-patch-bundles/icysymmetra-tiktok-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/icysymmetra-tiktok-patch-bundles/icysymmetra-tiktok-dev-patches-bundle.json```
</details>

---
### 📦 AlexNaga-Patches-Bundle [Morphe]:
[🧩 AlexNaga Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-alexnaga-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/AlexNaga-patch-bundles/AlexNaga-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/AlexNaga-patch-bundles/AlexNaga-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/AlexNaga-patch-bundles/AlexNaga-dev-patches-bundle.json```
</details>

---
### 📦 Rushiranpise-Patches-Bundle [Morphe]:
[🧩 Rushiranpise Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rushiranpise-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rushiranpise-patch-bundles/rushiranpise-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rushiranpise-patch-bundles/rushiranpise-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rushiranpise-patch-bundles/rushiranpise-dev-patches-bundle.json```
</details>

---
### 📦 Sjshb57-PairIP-Patches-Bundle [Morphe]:
[🧩 Sjshb57-PairIP Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-sjshb57-pairip-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/sjshb57-pairip-patch-bundles/sjshb57-pairip-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/sjshb57-pairip-patch-bundles/sjshb57-pairip-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/sjshb57-pairip-patch-bundles/sjshb57-pairip-dev-patches-bundle.json```
</details>

---
### 📦 MojiRS-RIF-Patches-Bundle [API v4]:
[🧩 MojiRS-RIF Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-mojirs-rif-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/mojirs-rif-patch-bundles/mojirs-rif-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/mojirs-rif-patch-bundles/mojirs-rif-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/mojirs-rif-patch-bundles/mojirs-rif-dev-patches-bundle.json```
</details>

---
### 📦 Realme-Link-Patches-Bundle [Morphe]:
[🧩 Realme-Link Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-realme-link-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/realme-link-patch-bundles/realme-link-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/realme-link-patch-bundles/realme-link-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/realme-link-patch-bundles/realme-link-dev-patches-bundle.json```
</details>

---
### 📦 HK-Morphe-Patches-Bundle [Morphe]:
[🧩 HK-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hk-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hk-morphe-patch-bundles/hk-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hk-morphe-patch-bundles/hk-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hk-morphe-patch-bundles/hk-morphe-dev-patches-bundle.json```
</details>

---
---
### 📦 BrayDog2010-Patches-Bundle [Morphe]:
[🧩 BrayDog2010 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-braydog2010-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/braydog2010-patch-bundles/braydog2010-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/braydog2010-patch-bundles/braydog2010-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/braydog2010-patch-bundles/braydog2010-dev-patches-bundle.json```
</details>

---
### 📦 TS2-Patches-Bundle [Morphe]:
[🧩 TS2 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ts2-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ts2-patch-bundles/ts2-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ts2-patch-bundles/ts2-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ts2-patch-bundles/ts2-dev-patches-bundle.json```
</details>

---
### 📦 Samsung-Morphe-Patches-Bundle [Morphe]:
[🧩 Samsung-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-samsung-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/samsung-morphe-patch-bundles/samsung-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/samsung-morphe-patch-bundles/samsung-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/samsung-morphe-patch-bundles/samsung-morphe-dev-patches-bundle.json```
</details>

---
### 📦 YT-YA-Voiceover-Patches-Bundle [Morphe]:
[🧩 YT-YA-Voiceover Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-yt-ya-voiceover-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/yt-ya-voiceover-patch-bundles/yt-ya-voiceover-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/yt-ya-voiceover-patch-bundles/yt-ya-voiceover-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/yt-ya-voiceover-patch-bundles/yt-ya-voiceover-dev-patches-bundle.json```
</details>

---
### 📦 Perplexity-STT-Patches-Bundle [Morphe]:
[🧩 Perplexity-STT Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-perplexity-stt-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/perplexity-stt-patch-bundles/perplexity-stt-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/perplexity-stt-patch-bundles/perplexity-stt-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/perplexity-stt-patch-bundles/perplexity-stt-dev-patches-bundle.json```
</details>

---
### 📦 Browzomje-Patches-Bundle [Morphe]:
[🧩 Browzomje Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-browzomje-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/browzomje-patch-bundles/browzomje-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/browzomje-patch-bundles/browzomje-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/browzomje-patch-bundles/browzomje-dev-patches-bundle.json```
</details>

---
### 📦 Morphe-Portal-Patches-Bundle [Morphe]:
[🧩 Morphe-Portal Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-morphe-portal-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-portal-patch-bundles/morphe-portal-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-portal-patch-bundles/morphe-portal-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-portal-patch-bundles/morphe-portal-dev-patches-bundle.json```
</details>

---
### 📦 Zpatches-Patches-Bundle [Morphe]:
[🧩 Zpatches Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-zpatches-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/zpatches-patch-bundles/zpatches-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/zpatches-patch-bundles/zpatches-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/zpatches-patch-bundles/zpatches-dev-patches-bundle.json```
</details>

---
### 📦 iHealth-Morphe-Patches-Bundle [Morphe]:
[🧩 iHealth-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ihealth-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ihealth-morphe-patch-bundles/ihealth-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ihealth-morphe-patch-bundles/ihealth-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ihealth-morphe-patch-bundles/ihealth-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Hoomans-Morphe-Patches-Bundle [Morphe]:
[🧩 Hoomans-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hoomans-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hoomans-morphe-patch-bundles/hoomans-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hoomans-morphe-patch-bundles/hoomans-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hoomans-morphe-patch-bundles/hoomans-morphe-dev-patches-bundle.json```
</details>

---
### 📦 AppleMusic-Patches-Bundle [API v4]:
[🧩 AppleMusic Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-applemusic-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/applemusic-patch-bundles/applemusic-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/applemusic-patch-bundles/applemusic-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/applemusic-patch-bundles/applemusic-dev-patches-bundle.json```
</details>

---
### 📦 Ynotzort-Patches-Bundle [Morphe]:
[🧩 Ynotzort Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ynotzort-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ynotzort-patch-bundles/ynotzort-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ynotzort-patch-bundles/ynotzort-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ynotzort-patch-bundles/ynotzort-dev-patches-bundle.json```
</details>

---
### 📦 Prathxm-Patches-Bundle [Morphe]:
[🧩 Prathxm Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-prathxm-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/prathxm-patch-bundles/prathxm-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/prathxm-patch-bundles/prathxm-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/prathxm-patch-bundles/prathxm-dev-patches-bundle.json```
</details>

---
### 📦 Telegram-Morphe-Patches-Bundle [Morphe]:
[🧩 Telegram-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-telegram-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/telegram-morphe-patch-bundles/telegram-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/telegram-morphe-patch-bundles/telegram-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/telegram-morphe-patch-bundles/telegram-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Morphe-Screenshot-Patches-Bundle [Morphe]:
[🧩 Morphe-Screenshot Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-morphe-screenshot-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-screenshot-patch-bundles/morphe-screenshot-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-screenshot-patch-bundles/morphe-screenshot-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-screenshot-patch-bundles/morphe-screenshot-dev-patches-bundle.json```
</details>

---
### 📦 NPCI-BHIM-Patches-Bundle [Morphe]:
[🧩 NPCI-BHIM Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-npci-bhim-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/npci-bhim-patch-bundles/npci-bhim-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/npci-bhim-patch-bundles/npci-bhim-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/npci-bhim-patch-bundles/npci-bhim-dev-patches-bundle.json```
</details>

---
### 📦 Prathxm-YTMusic-Patches-Bundle [Morphe]:
[🧩 Prathxm-YTMusic Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-prathxm-ytmusic-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/prathxm-ytmusic-patch-bundles/prathxm-ytmusic-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/prathxm-ytmusic-patch-bundles/prathxm-ytmusic-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/prathxm-ytmusic-patch-bundles/prathxm-ytmusic-dev-patches-bundle.json```
</details>

---
### 📦 Nai64-Patches-Bundle [Morphe]:
[🧩 Nai64 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-nai64-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nai64-patch-bundles/nai64-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nai64-patch-bundles/nai64-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nai64-patch-bundles/nai64-dev-patches-bundle.json```
</details>

---
### 📦 Morphe-Google-Patches-Bundle [Morphe]:
[🧩 Morphe-Google Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-morphe-google-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-google-patch-bundles/morphe-google-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-google-patch-bundles/morphe-google-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morphe-google-patch-bundles/morphe-google-dev-patches-bundle.json```
</details>

---
### 📦 Xhehab-Patches-Bundle [Morphe]:
[🧩 Xhehab Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-xhehab-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xhehab-patch-bundles/xhehab-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xhehab-patch-bundles/xhehab-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xhehab-patch-bundles/xhehab-dev-patches-bundle.json```
</details>

---
### 📦 Okish-Morphe-Patches-Bundle [Morphe]:
[🧩 Okish-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-okish-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/okish-morphe-patch-bundles/okish-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/okish-morphe-patch-bundles/okish-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/okish-morphe-patch-bundles/okish-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Bufferk-Patches-Bundle [Morphe]:
[🧩 Bufferk Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bufferk-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bufferk-patch-bundles/bufferk-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bufferk-patch-bundles/bufferk-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bufferk-patch-bundles/bufferk-dev-patches-bundle.json```
</details>

---
### 📦 Franticg33k-Patches-Bundle [Morphe]:
[🧩 Franticg33k Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-franticg33k-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/franticg33k-patch-bundles/franticg33k-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/franticg33k-patch-bundles/franticg33k-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/franticg33k-patch-bundles/franticg33k-dev-patches-bundle.json```
</details>

---
### 📦 Gryphous-Morphe-Patches-Bundle [Morphe]:
[🧩 Gryphous-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-gryphous-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gryphous-morphe-patch-bundles/gryphous-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gryphous-morphe-patch-bundles/gryphous-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gryphous-morphe-patch-bundles/gryphous-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Coronenic-Patches-Bundle [API v4]:
[🧩 Coronenic Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-coronenic-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/coronenic-patch-bundles/coronenic-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/coronenic-patch-bundles/coronenic-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/coronenic-patch-bundles/coronenic-dev-patches-bundle.json```
</details>

---
### 📦 Shaun-Sheep-Patches-Bundle [Morphe]:
[🧩 Shaun-Sheep Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-shaun-sheep-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/shaun-sheep-patch-bundles/shaun-sheep-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/shaun-sheep-patch-bundles/shaun-sheep-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/shaun-sheep-patch-bundles/shaun-sheep-dev-patches-bundle.json```
</details>

---
### 📦 Movistar-Block-Ads-Patches-Bundle [Morphe]:
[🧩 Movistar-Block-Ads Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-movistar-block-ads-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/movistar-block-ads-patch-bundles/movistar-block-ads-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/movistar-block-ads-patch-bundles/movistar-block-ads-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/movistar-block-ads-patch-bundles/movistar-block-ads-dev-patches-bundle.json```
</details>

---
### 📦 Pinterest-Morphed-Patches-Bundle [Morphe]:
[🧩 Pinterest-Morphed Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-pinterest-morphed-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pinterest-morphed-patch-bundles/pinterest-morphed-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pinterest-morphed-patch-bundles/pinterest-morphed-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pinterest-morphed-patch-bundles/pinterest-morphed-dev-patches-bundle.json```
</details>

---
### 📦 Miguel-Patches-Bundle [Morphe]:
[🧩 Miguel Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-miguel-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/miguel-patch-bundles/miguel-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/miguel-patch-bundles/miguel-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/miguel-patch-bundles/miguel-dev-patches-bundle.json```
</details>

---
### 📦 Pichiwa-Patches-Bundle [Morphe]:
[🧩 Pichiwa Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-pichiwa-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pichiwa-patch-bundles/pichiwa-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pichiwa-patch-bundles/pichiwa-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pichiwa-patch-bundles/pichiwa-dev-patches-bundle.json```
</details>

---
### 📦 Saiesh-Patches-Bundle [Morphe]:
[🧩 Saiesh Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-saiesh-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/saiesh-patch-bundles/saiesh-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/saiesh-patch-bundles/saiesh-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/saiesh-patch-bundles/saiesh-dev-patches-bundle.json```
</details>

---
### 📦 Letterboxd-Stremio-Patches-Bundle [Morphe]:
[🧩 Letterboxd-Stremio Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-letterboxd-stremio-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/letterboxd-stremio-patch-bundles/letterboxd-stremio-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/letterboxd-stremio-patch-bundles/letterboxd-stremio-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/letterboxd-stremio-patch-bundles/letterboxd-stremio-dev-patches-bundle.json```
</details>

---
### 📦 Cobalt-Morphe-Patches-Bundle [Morphe]:
[🧩 Cobalt-Morphe Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-cobalt-morphe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/cobalt-morphe-patch-bundles/cobalt-morphe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/cobalt-morphe-patch-bundles/cobalt-morphe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/cobalt-morphe-patch-bundles/cobalt-morphe-dev-patches-bundle.json```
</details>

---
### 📦 Proxma-Patches-Bundle [Morphe]:
[🧩 Proxma Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-proxma-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/proxma-patch-bundles/proxma-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/proxma-patch-bundles/proxma-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/proxma-patch-bundles/proxma-dev-patches-bundle.json```
</details>

---
### 📦 Jouss-Patches-Bundle [Morphe]:
[🧩 Jouss Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jouss-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jouss-patch-bundles/jouss-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jouss-patch-bundles/jouss-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jouss-patch-bundles/jouss-dev-patches-bundle.json```
</details>

---
### 📦 ItsTheJoker-Patches-Bundle [Morphe]:
[🧩 ItsTheJoker Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-itsthejoker-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/itsthejoker-patch-bundles/itsthejoker-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/itsthejoker-patch-bundles/itsthejoker-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/itsthejoker-patch-bundles/itsthejoker-dev-patches-bundle.json```
</details>

---
### 📦 Gmaps-Patches-Bundle [Morphe]:
[🧩 Gmaps Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-gmaps-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gmaps-patch-bundles/gmaps-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gmaps-patch-bundles/gmaps-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gmaps-patch-bundles/gmaps-dev-patches-bundle.json```
</details>

---
### 📦 Seobject-Patches-Bundle [Morphe]:
[🧩 Seobject Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-seobject-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/seobject-patch-bundles/seobject-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/seobject-patch-bundles/seobject-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/seobject-patch-bundles/seobject-dev-patches-bundle.json```
</details>

---
### 📦 Abeja-Patches-Bundle [Morphe]:
[🧩 Abeja Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-abeja-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abeja-patch-bundles/abeja-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abeja-patch-bundles/abeja-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abeja-patch-bundles/abeja-dev-patches-bundle.json```
</details>

---
### 📦 RIVanced-Universal-Patches-Bundle [Morphe]:
[🧩 RIVanced-Universal Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rivanced-universal-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rivanced-universal-patch-bundles/rivanced-universal-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rivanced-universal-patch-bundles/rivanced-universal-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rivanced-universal-patch-bundles/rivanced-universal-dev-patches-bundle.json```
</details>

---
### 📦 Variablenine-Patches-Bundle [Morphe]:
[🧩 Variablenine Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-variablenine-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/variablenine-patch-bundles/variablenine-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/variablenine-patch-bundles/variablenine-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/variablenine-patch-bundles/variablenine-dev-patches-bundle.json```
</details>

---
### 📦 Stylus-Patches-Bundle [Morphe]:
[🧩 Stylus Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-stylus-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/stylus-patch-bundles/stylus-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/stylus-patch-bundles/stylus-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/stylus-patch-bundles/stylus-dev-patches-bundle.json```
</details>

---
### 📦 HXReborn-Patches-Bundle [Morphe]:
[🧩 HXReborn Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hxreborn-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hxreborn-patch-bundles/hxreborn-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hxreborn-patch-bundles/hxreborn-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hxreborn-patch-bundles/hxreborn-dev-patches-bundle.json```
</details>

---
### 📦 Ikura-Patches-Bundle [Morphe]:
[🧩 Ikura Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ikura-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ikura-patch-bundles/ikura-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ikura-patch-bundles/ikura-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ikura-patch-bundles/ikura-dev-patches-bundle.json```
</details>


---
### 📦 DH6K-Patches-Bundle [Morphe]:
[🧩 DH6K Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dh6k-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dh6k-patch-bundles/dh6k-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dh6k-patch-bundles/dh6k-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dh6k-patch-bundles/dh6k-dev-patches-bundle.json```
</details>

---
### 📦 AndrewLiang25-Patches-Bundle [Morphe]:
[🧩 AndrewLiang25 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-andrewliang25-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/andrewliang25-patch-bundles/andrewliang25-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/andrewliang25-patch-bundles/andrewliang25-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/andrewliang25-patch-bundles/andrewliang25-dev-patches-bundle.json```
</details>

---
### 📦 Morning-Entree-Patches-Bundle [Morphe]:
[🧩 Morning-Entree Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-morning-entree-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morning-entree-patch-bundles/morning-entree-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morning-entree-patch-bundles/morning-entree-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/morning-entree-patch-bundles/morning-entree-dev-patches-bundle.json```
</details>

---
### 📦 VocaColle-Patches-Bundle [Morphe]:
[🧩 VocaColle Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-vocacolle-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vocacolle-patch-bundles/vocacolle-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vocacolle-patch-bundles/vocacolle-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/vocacolle-patch-bundles/vocacolle-dev-patches-bundle.json```
</details>

---
### 📦 DBTCoach-Patches-Bundle [Morphe]:
[🧩 DBTCoach Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dbtcoach-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dbtcoach-patch-bundles/dbtcoach-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dbtcoach-patch-bundles/dbtcoach-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dbtcoach-patch-bundles/dbtcoach-dev-patches-bundle.json```
</details>

---
### 📦 Yandex-VoT-Patches-Bundle [Morphe]:
[🧩 Yandex-VoT Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-yandex-vot-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/yandex-vot-patch-bundles/yandex-vot-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/yandex-vot-patch-bundles/yandex-vot-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/yandex-vot-patch-bundles/yandex-vot-dev-patches-bundle.json```
</details>


---
### 📦 Watch-Later-Patches-Bundle [Morphe]:
[🧩 Watch-Later Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-watch-later-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/watch-later-patch-bundles/watch-later-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/watch-later-patch-bundles/watch-later-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/watch-later-patch-bundles/watch-later-dev-patches-bundle.json```
</details>


---
### 📦 SofaTime-Patches-Bundle [Morphe]:
[🧩 SofaTime Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-sofatime-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/sofatime-patch-bundles/sofatime-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/sofatime-patch-bundles/sofatime-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/sofatime-patch-bundles/sofatime-dev-patches-bundle.json```
</details>


---
### 📦 Hiosdra-Patches-Bundle [Morphe]:
[🧩 Hiosdra Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hiosdra-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hiosdra-patch-bundles/hiosdra-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hiosdra-patch-bundles/hiosdra-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hiosdra-patch-bundles/hiosdra-dev-patches-bundle.json```
</details>


---
### 📦 Jl4cTuk-Patches-Bundle [Morphe]:
[🧩 Jl4cTuk Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jl4ctuk-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jl4ctuk-patch-bundles/jl4ctuk-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jl4ctuk-patch-bundles/jl4ctuk-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jl4ctuk-patch-bundles/jl4ctuk-dev-patches-bundle.json```
</details>

---
### 📦 Edge-ReVanced-Patches-Bundle [API v4]:
[🧩 Edge-ReVanced Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-edge-revanced-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/edge-revanced-patch-bundles/edge-revanced-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/edge-revanced-patch-bundles/edge-revanced-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/edge-revanced-patch-bundles/edge-revanced-dev-patches-bundle.json```
</details>
---
### 📦 LaBlazer-Patches-Bundle [Morphe]:
[🧩 LaBlazer Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-lablazer-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lablazer-patch-bundles/lablazer-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lablazer-patch-bundles/lablazer-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/lablazer-patch-bundles/lablazer-dev-patches-bundle.json```
</details>

---
### 📦 D0NJ-Patches-Bundle [Morphe]:
[🧩 D0NJ Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-d0nj-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d0nj-patch-bundles/d0nj-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d0nj-patch-bundles/d0nj-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d0nj-patch-bundles/d0nj-dev-patches-bundle.json```
</details>

---
### 📦 TIDAL-Patches-Bundle [Morphe]:
[🧩 TIDAL Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-tidal-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tidal-patch-bundles/tidal-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tidal-patch-bundles/tidal-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tidal-patch-bundles/tidal-dev-patches-bundle.json```
</details>

---
### 📦 Zarko-Patches-Bundle [Morphe]:
[🧩 Zarko Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-zarko-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/zarko-patch-bundles/zarko-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/zarko-patch-bundles/zarko-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/zarko-patch-bundles/zarko-dev-patches-bundle.json```
</details>

---
### 📦 Niconico-YT-Patches-Bundle [Morphe]:
[🧩 Niconico-YT Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-niconico-yt-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/niconico-yt-patch-bundles/niconico-yt-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/niconico-yt-patch-bundles/niconico-yt-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/niconico-yt-patch-bundles/niconico-yt-dev-patches-bundle.json```
</details>

---
### 📦 Alastor-Kaneki-Patches-Bundle [Morphe]:
[🧩 Alastor-Kaneki Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-alastor-kaneki-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alastor-kaneki-patch-bundles/alastor-kaneki-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alastor-kaneki-patch-bundles/alastor-kaneki-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alastor-kaneki-patch-bundles/alastor-kaneki-dev-patches-bundle.json```
</details>

---
### 📦 NuvioTV-Patches-Bundle [Morphe]:
[🧩 NuvioTV Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-nuviotv-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nuviotv-patch-bundles/nuviotv-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nuviotv-patch-bundles/nuviotv-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nuviotv-patch-bundles/nuviotv-dev-patches-bundle.json```
</details>

---
### 📦 GoldRift-Patches-Bundle [Morphe]:
[🧩 GoldRift Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-goldrift-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/goldrift-patch-bundles/goldrift-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/goldrift-patch-bundles/goldrift-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/goldrift-patch-bundles/goldrift-dev-patches-bundle.json```
</details>

---
### 📦 RoundSalmon4-Patches-Bundle [Morphe]:
[🧩 RoundSalmon4 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-roundsalmon4-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/roundsalmon4-patch-bundles/roundsalmon4-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/roundsalmon4-patch-bundles/roundsalmon4-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/roundsalmon4-patch-bundles/roundsalmon4-dev-patches-bundle.json```
</details>

---
### 📦 HU-Liberator-Patches-Bundle [Morphe]:
[🧩 HU-Liberator Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hu-liberator-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hu-liberator-patch-bundles/hu-liberator-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hu-liberator-patch-bundles/hu-liberator-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hu-liberator-patch-bundles/hu-liberator-dev-patches-bundle.json```
</details>

---
### 📦 JonnyVR1-Patches-Bundle [Morphe]:
[🧩 JonnyVR1 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jonnyvr1-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jonnyvr1-patch-bundles/jonnyvr1-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jonnyvr1-patch-bundles/jonnyvr1-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jonnyvr1-patch-bundles/jonnyvr1-dev-patches-bundle.json```
</details>

---
### 📦 Logm1lo-Patches-Bundle [Morphe]:
[🧩 Logm1lo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-logm1lo-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/logm1lo-patch-bundles/logm1lo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/logm1lo-patch-bundles/logm1lo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/logm1lo-patch-bundles/logm1lo-dev-patches-bundle.json```
</details>

---
### 📦 SpookyEXE-Patches-Bundle [Morphe]:
[🧩 SpookyEXE Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-spookyexe-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/spookyexe-patch-bundles/spookyexe-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/spookyexe-patch-bundles/spookyexe-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/spookyexe-patch-bundles/spookyexe-dev-patches-bundle.json```
</details>

---
### 📦 PetalMaps-NonHuawei-Patches-Bundle [Morphe]:
[🧩 PetalMaps-NonHuawei Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-petalmaps-nonhuawei-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/petalmaps-nonhuawei-patch-bundles/petalmaps-nonhuawei-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/petalmaps-nonhuawei-patch-bundles/petalmaps-nonhuawei-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/petalmaps-nonhuawei-patch-bundles/petalmaps-nonhuawei-dev-patches-bundle.json```
</details>

---
### 📦 Dbhavsar76-Patches-Bundle [API v4]:
[🧩 Dbhavsar76 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dbhavsar76-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dbhavsar76-patch-bundles/dbhavsar76-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dbhavsar76-patch-bundles/dbhavsar76-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dbhavsar76-patch-bundles/dbhavsar76-dev-patches-bundle.json```
</details>

---
### 📦 FTL-Patches-Bundle [Morphe]:
[🧩 FTL Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ftl-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ftl-patch-bundles/ftl-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ftl-patch-bundles/ftl-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ftl-patch-bundles/ftl-dev-patches-bundle.json```
</details>

---
### 📦 braiNtropy-Patches-Bundle [Morphe]:
[🧩 braiNtropy Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-braintropy-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/braintropy-patch-bundles/braintropy-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/braintropy-patch-bundles/braintropy-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/braintropy-patch-bundles/braintropy-dev-patches-bundle.json```
</details>

---
### 📦 Ang3lo-Patches-Bundle [Morphe]:
[🧩 Ang3lo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ang3lo-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ang3lo-patch-bundles/ang3lo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ang3lo-patch-bundles/ang3lo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ang3lo-patch-bundles/ang3lo-dev-patches-bundle.json```
</details>

---
### 📦 ChMate-ReVanced-Patches-Bundle [API v4]:
[🧩 ChMate-ReVanced Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-chmate-revanced-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chmate-revanced-patch-bundles/chmate-revanced-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chmate-revanced-patch-bundles/chmate-revanced-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chmate-revanced-patch-bundles/chmate-revanced-dev-patches-bundle.json```
</details>

---
### 📦 Simnple-Patches-Bundle [API v4]:
[🧩 Simnple Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-simnple-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/simnple-patch-bundles/simnple-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/simnple-patch-bundles/simnple-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/simnple-patch-bundles/simnple-dev-patches-bundle.json```
</details>

---
### 📦 Heval99-Patches-Bundle [Morphe]:
[🧩 Heval99 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-heval99-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/heval99-patch-bundles/heval99-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/heval99-patch-bundles/heval99-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/heval99-patch-bundles/heval99-dev-patches-bundle.json```
</details>

---
### 📦 Atharv-Patches-Bundle [Morphe]:
[🧩 Atharv Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-atharv-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/atharv-patch-bundles/atharv-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/atharv-patch-bundles/atharv-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/atharv-patch-bundles/atharv-dev-patches-bundle.json```
</details>

---
### 📦 Tiaruebar-Patches-Bundle [Morphe]:
[🧩 Tiaruebar Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-tiaruebar-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tiaruebar-patch-bundles/tiaruebar-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tiaruebar-patch-bundles/tiaruebar-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tiaruebar-patch-bundles/tiaruebar-dev-patches-bundle.json```
</details>

---
### 📦 FTL-Portal-Patches-Bundle [Morphe]:
[🧩 FTL-Portal Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ftl-portal-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ftl-portal-patch-bundles/ftl-portal-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ftl-portal-patch-bundles/ftl-portal-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ftl-portal-patch-bundles/ftl-portal-dev-patches-bundle.json```
</details>

---
### 📦 D4NZ-Patches-Bundle [API v4]:
[🧩 D4NZ Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-d4nz-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d4nz-patch-bundles/d4nz-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d4nz-patch-bundles/d4nz-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/d4nz-patch-bundles/d4nz-dev-patches-bundle.json```
</details>

---
### 📦 Imgur-Patches-Bundle [Morphe]:
[🧩 Imgur Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-imgur-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imgur-patch-bundles/imgur-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imgur-patch-bundles/imgur-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imgur-patch-bundles/imgur-dev-patches-bundle.json```
</details>

---
### 📦 aapam-Patches-Bundle [Morphe]:
[🧩 aapam Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-aapam-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aapam-patch-bundles/aapam-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aapam-patch-bundles/aapam-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aapam-patch-bundles/aapam-dev-patches-bundle.json```
</details>

---
### 📦 RabehX-Patches-Bundle [Morphe]:
[🧩 RabehX Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rabehx-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rabehx-patch-bundles/rabehx-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rabehx-patch-bundles/rabehx-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rabehx-patch-bundles/rabehx-dev-patches-bundle.json```
</details>

---
### 📦 Tiaruebar1024-Patches-Bundle [Morphe]:
[🧩 Tiaruebar1024 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-tiaruebar1024-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tiaruebar1024-patch-bundles/tiaruebar1024-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tiaruebar1024-patch-bundles/tiaruebar1024-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/tiaruebar1024-patch-bundles/tiaruebar1024-dev-patches-bundle.json```
</details>

---
### 📦 Slight-Patches-Bundle [Morphe]:
[🧩 Slight Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-slight-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/slight-patch-bundles/slight-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/slight-patch-bundles/slight-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/slight-patch-bundles/slight-dev-patches-bundle.json```
</details>

---
### 📦 Riky-Patches-Bundle [Morphe]:
[🧩 Riky Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-riky-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/riky-patch-bundles/riky-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/riky-patch-bundles/riky-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/riky-patch-bundles/riky-dev-patches-bundle.json```
</details>

---
### 📦 iPusnas-Patches-Bundle [Morphe]:
[🧩 iPusnas Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ipusnas-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ipusnas-patch-bundles/ipusnas-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ipusnas-patch-bundles/ipusnas-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ipusnas-patch-bundles/ipusnas-dev-patches-bundle.json```
</details>

---
### 📦 HXReborn-TikTok-Patches-Bundle [Morphe]:
[🧩 HXReborn-TikTok Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hxreborn-tiktok-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hxreborn-tiktok-patch-bundles/hxreborn-tiktok-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hxreborn-tiktok-patch-bundles/hxreborn-tiktok-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hxreborn-tiktok-patch-bundles/hxreborn-tiktok-dev-patches-bundle.json```
</details>

---
### 📦 Flexboard-Patches-Bundle [Morphe]:
[🧩 Flexboard Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-flexboard-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/flexboard-patch-bundles/flexboard-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/flexboard-patch-bundles/flexboard-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/flexboard-patch-bundles/flexboard-dev-patches-bundle.json```
</details>

---
### 📦 Cricinfo-Tweaks-Patches-Bundle [Morphe]:
[🧩 Cricinfo-Tweaks Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-cricinfo-tweaks-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/cricinfo-tweaks-patch-bundles/cricinfo-tweaks-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/cricinfo-tweaks-patch-bundles/cricinfo-tweaks-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/cricinfo-tweaks-patch-bundles/cricinfo-tweaks-dev-patches-bundle.json```
</details>

---
### 📦 RuStore-Privacy-Patches-Bundle [Morphe]:
[🧩 RuStore-Privacy Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rustore-privacy-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rustore-privacy-patch-bundles/rustore-privacy-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rustore-privacy-patch-bundles/rustore-privacy-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rustore-privacy-patch-bundles/rustore-privacy-dev-patches-bundle.json```
</details>

---
### 📦 Abhishek-Bhujang-Patches-Bundle [Morphe]:
[🧩 Abhishek-Bhujang Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-abhishek-bhujang-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abhishek-bhujang-patch-bundles/abhishek-bhujang-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abhishek-bhujang-patch-bundles/abhishek-bhujang-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/abhishek-bhujang-patch-bundles/abhishek-bhujang-dev-patches-bundle.json```
</details>

---
### 📦 MauroGamerVN-Patches-Bundle [Morphe]:
[🧩 MauroGamerVN Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-maurogamervn-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/maurogamervn-patch-bundles/maurogamervn-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/maurogamervn-patch-bundles/maurogamervn-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/maurogamervn-patch-bundles/maurogamervn-dev-patches-bundle.json```
</details>

---
### 📦 Kveld-Patches-Bundle [Morphe]:
[🧩 Kveld Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kveld-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kveld-patch-bundles/kveld-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kveld-patch-bundles/kveld-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kveld-patch-bundles/kveld-dev-patches-bundle.json```
</details>

---
### 📦 Anime-Witcher-Patches-Bundle [Morphe]:
[🧩 Anime-Witcher Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-anime-witcher-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anime-witcher-patch-bundles/anime-witcher-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anime-witcher-patch-bundles/anime-witcher-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anime-witcher-patch-bundles/anime-witcher-dev-patches-bundle.json```
</details>

---
### 📦 Expose-Like-Status-in-MediaSession-Patches-Bundle [API v4]:
[🧩 Expose-Like-Status-in-MediaSession Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-expose-like-status-in-mediasession-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/expose-like-status-in-mediasession-patch-bundles/expose-like-status-in-mediasession-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/expose-like-status-in-mediasession-patch-bundles/expose-like-status-in-mediasession-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/expose-like-status-in-mediasession-patch-bundles/expose-like-status-in-mediasession-dev-patches-bundle.json```
</details>

---
### 📦 Apos-Patches-Bundle [Morphe]:
[🧩 Apos Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-apos-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/apos-patch-bundles/apos-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/apos-patch-bundles/apos-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/apos-patch-bundles/apos-dev-patches-bundle.json```
</details>

---
### 📦 HH-Patches-Bundle [Morphe]:
[🧩 HH Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-hh-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hh-patch-bundles/hh-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hh-patch-bundles/hh-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/hh-patch-bundles/hh-dev-patches-bundle.json```
</details>

---
### 📦 Anxy-Patches-Bundle [Morphe]:
[🧩 Anxy Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-anxy-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anxy-patch-bundles/anxy-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anxy-patch-bundles/anxy-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/anxy-patch-bundles/anxy-dev-patches-bundle.json```
</details>

---
### 📦 Chicco-Patches-Bundle [Morphe]:
[🧩 Chicco Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-chicco-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chicco-patch-bundles/chicco-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chicco-patch-bundles/chicco-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/chicco-patch-bundles/chicco-dev-patches-bundle.json```
</details>

---
### 📦 XTapped-Patches-Bundle [Morphe]:
[🧩 XTapped Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-xtapped-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xtapped-patch-bundles/xtapped-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xtapped-patch-bundles/xtapped-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/xtapped-patch-bundles/xtapped-dev-patches-bundle.json```
</details>

---
### 📦 ImNoammm-Spotify-Patches-Bundle [Morphe]:
[🧩 ImNoammm-Spotify Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-imnoammm-spotify-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imnoammm-spotify-patch-bundles/imnoammm-spotify-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imnoammm-spotify-patch-bundles/imnoammm-spotify-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imnoammm-spotify-patch-bundles/imnoammm-spotify-dev-patches-bundle.json```
</details>

---
### 📦 Beetle-Patches-Bundle [Morphe]:
[🧩 Beetle Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-beetle-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/beetle-patch-bundles/beetle-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/beetle-patch-bundles/beetle-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/beetle-patch-bundles/beetle-dev-patches-bundle.json```
</details>

---
### 📦 Jancerny2001-Patches-Bundle [Morphe]:
[🧩 Jancerny2001 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jancerny2001-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jancerny2001-patch-bundles/jancerny2001-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jancerny2001-patch-bundles/jancerny2001-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jancerny2001-patch-bundles/jancerny2001-dev-patches-bundle.json```
</details>

---
### 📦 Rhubarbshoelaces-Patches-Bundle [Morphe]:
[🧩 Rhubarbshoelaces Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rhubarbshoelaces-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rhubarbshoelaces-patch-bundles/rhubarbshoelaces-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rhubarbshoelaces-patch-bundles/rhubarbshoelaces-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rhubarbshoelaces-patch-bundles/rhubarbshoelaces-dev-patches-bundle.json```
</details>

---
### 📦 Psychonaut-Wiki-Journal-Patches-Bundle [Morphe]:
[🧩 Psychonaut-Wiki-Journal Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-psychonaut-wiki-journal-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/psychonaut-wiki-journal-patch-bundles/psychonaut-wiki-journal-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/psychonaut-wiki-journal-patch-bundles/psychonaut-wiki-journal-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/psychonaut-wiki-journal-patch-bundles/psychonaut-wiki-journal-dev-patches-bundle.json```
</details>

---
### 📦 RedFlagDeals-Patches-Bundle [API v4]:
[🧩 RedFlagDeals Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-redflagdeals-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/redflagdeals-patch-bundles/redflagdeals-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/redflagdeals-patch-bundles/redflagdeals-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/redflagdeals-patch-bundles/redflagdeals-dev-patches-bundle.json```
</details>

---
### 📦 Dr4w-Patches-Bundle [Morphe]:
[🧩 Dr4w Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dr4w-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dr4w-patch-bundles/dr4w-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dr4w-patch-bundles/dr4w-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dr4w-patch-bundles/dr4w-dev-patches-bundle.json```
</details>

---
### 📦 Aimal-Patches-Bundle [Morphe]:
[🧩 Aimal Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-aimal-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aimal-patch-bundles/aimal-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aimal-patch-bundles/aimal-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aimal-patch-bundles/aimal-dev-patches-bundle.json```
</details>

---
### 📦 Gltieo-Patches-Bundle [API v4]:
[🧩 Gltieo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-gltieo-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gltieo-patch-bundles/gltieo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gltieo-patch-bundles/gltieo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/gltieo-patch-bundles/gltieo-dev-patches-bundle.json```
</details>

---
### 📦 ShuhaibNC-Patches-Bundle [Morphe]:
[🧩 ShuhaibNC Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-shuhaibnc-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/shuhaibnc-patch-bundles/shuhaibnc-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/shuhaibnc-patch-bundles/shuhaibnc-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/shuhaibnc-patch-bundles/shuhaibnc-dev-patches-bundle.json```
</details>

---
### 📦 Stremio-AndroidTV-Patches-Bundle [Morphe]:
[🧩 Stremio-AndroidTV Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-stremio-androidtv-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/stremio-androidtv-patch-bundles/stremio-androidtv-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/stremio-androidtv-patch-bundles/stremio-androidtv-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/stremio-androidtv-patch-bundles/stremio-androidtv-dev-patches-bundle.json```
</details>

---
### 📦 Bluecxt-Instagram-Patches-Bundle [API v4]:
[🧩 Bluecxt-Instagram Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bluecxt-instagram-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bluecxt-instagram-patch-bundles/bluecxt-instagram-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bluecxt-instagram-patch-bundles/bluecxt-instagram-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bluecxt-instagram-patch-bundles/bluecxt-instagram-dev-patches-bundle.json```
</details>

---
### 📦 Imgur-ReVanced-Patches-Bundle [API v4]:
[🧩 Imgur-ReVanced Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-imgur-revanced-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imgur-revanced-patch-bundles/imgur-revanced-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imgur-revanced-patch-bundles/imgur-revanced-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/imgur-revanced-patch-bundles/imgur-revanced-dev-patches-bundle.json```
</details>

---
### 📦 Legendsciber-Patches-Bundle [Morphe]:
[🧩 Legendsciber Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-legendsciber-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/legendsciber-patch-bundles/legendsciber-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/legendsciber-patch-bundles/legendsciber-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/legendsciber-patch-bundles/legendsciber-dev-patches-bundle.json```
</details>

---
### 📦 SteamLink-Patches-Bundle [Morphe]:
[🧩 SteamLink Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-steamlink-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/steamlink-patch-bundles/steamlink-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/steamlink-patch-bundles/steamlink-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/steamlink-patch-bundles/steamlink-dev-patches-bundle.json```
</details>

---
### 📦 Nicomanga-ReVanced-Patches-Bundle [API v4]:
[🧩 Nicomanga-ReVanced Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-nicomanga-revanced-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nicomanga-revanced-patch-bundles/nicomanga-revanced-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nicomanga-revanced-patch-bundles/nicomanga-revanced-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nicomanga-revanced-patch-bundles/nicomanga-revanced-dev-patches-bundle.json```
</details>

---
### 📦 Froggo-Patches-Bundle [Morphe]:
[🧩 Froggo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-froggo-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/froggo-patch-bundles/froggo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/froggo-patch-bundles/froggo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/froggo-patch-bundles/froggo-dev-patches-bundle.json```
</details>

---
### 📦 Kecerim24-Patches-Bundle [Morphe]:
[🧩 Kecerim24 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-kecerim24-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kecerim24-patch-bundles/kecerim24-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kecerim24-patch-bundles/kecerim24-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/kecerim24-patch-bundles/kecerim24-dev-patches-bundle.json```
</details>

---
### 📦 Z-drgon-Patches-Bundle [Morphe]:
[🧩 Z-drgon Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-z-drgon-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/z-drgon-patch-bundles/z-drgon-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/z-drgon-patch-bundles/z-drgon-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/z-drgon-patch-bundles/z-drgon-dev-patches-bundle.json```
</details>

---
### 📦 V4n1X-Patches-Bundle [Morphe]:
[🧩 V4n1X Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-v4n1x-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/v4n1x-patch-bundles/v4n1x-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/v4n1x-patch-bundles/v4n1x-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/v4n1x-patch-bundles/v4n1x-dev-patches-bundle.json```
</details>


---
### 📦 RoadSync-Patches-Bundle [Morphe]:
[🧩 RoadSync Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-roadsync-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/roadsync-patch-bundles/roadsync-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/roadsync-patch-bundles/roadsync-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/roadsync-patch-bundles/roadsync-dev-patches-bundle.json```
</details>

---
### 📦 Jackblk-Patches-Bundle [Morphe]:
[🧩 Jackblk Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jackblk-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jackblk-patch-bundles/jackblk-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jackblk-patch-bundles/jackblk-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jackblk-patch-bundles/jackblk-dev-patches-bundle.json```
</details>

---
### 📦 Educal72-Patches-Bundle [Morphe]:
[🧩 Educal72 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-educal72-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/educal72-patch-bundles/educal72-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/educal72-patch-bundles/educal72-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/educal72-patch-bundles/educal72-dev-patches-bundle.json```
</details>

---
### 📦 Canh0chua-Patches-Bundle [Morphe]:
[🧩 Canh0chua Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-canh0chua-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/canh0chua-patch-bundles/canh0chua-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/canh0chua-patch-bundles/canh0chua-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/canh0chua-patch-bundles/canh0chua-dev-patches-bundle.json```
</details>

---
### 📦 Jaredcat-Patches-Bundle [Morphe]:
[🧩 Jaredcat Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-jaredcat-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jaredcat-patch-bundles/jaredcat-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jaredcat-patch-bundles/jaredcat-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/jaredcat-patch-bundles/jaredcat-dev-patches-bundle.json```
</details>

---
### 📦 Dan1elTheMan1el-Patches-Bundle [Morphe]:
[🧩 Dan1elTheMan1el Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dan1eltheman1el-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dan1eltheman1el-patch-bundles/dan1eltheman1el-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dan1eltheman1el-patch-bundles/dan1eltheman1el-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dan1eltheman1el-patch-bundles/dan1eltheman1el-dev-patches-bundle.json```
</details>

---
### 📦 Csagataj2-Patches-Bundle [Morphe]:
[🧩 Csagataj2 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-csagataj2-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/csagataj2-patch-bundles/csagataj2-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/csagataj2-patch-bundles/csagataj2-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/csagataj2-patch-bundles/csagataj2-dev-patches-bundle.json```

</details>

---
### 📦 Rafag00-Patches-Bundle [Morphe]:
[🧩 Rafag00 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rafag00-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rafag00-patch-bundles/rafag00-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rafag00-patch-bundles/rafag00-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rafag00-patch-bundles/rafag00-dev-patches-bundle.json```

</details>

---
### 📦 NullWaypoint-Patches-Bundle [Morphe]:
[🧩 NullWaypoint Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-nullwaypoint-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nullwaypoint-patch-bundles/nullwaypoint-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nullwaypoint-patch-bundles/nullwaypoint-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nullwaypoint-patch-bundles/nullwaypoint-dev-patches-bundle.json```

</details>

---
### 📦 DiskWala-Patches-Bundle [Morphe]:
[🧩 DiskWala Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-diskwala-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/diskwala-patch-bundles/diskwala-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/diskwala-patch-bundles/diskwala-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/diskwala-patch-bundles/diskwala-dev-patches-bundle.json```

</details>

---
### 📦 IPTV-Patches-Bundle [Morphe]:
[🧩 IPTV Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-iptv-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/iptv-patch-bundles/iptv-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/iptv-patch-bundles/iptv-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/iptv-patch-bundles/iptv-dev-patches-bundle.json```

</details>

---
### 📦 Bruddaa-Patches-Bundle [Morphe]:
[🧩 Bruddaa Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-bruddaa-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bruddaa-patch-bundles/bruddaa-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bruddaa-patch-bundles/bruddaa-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/bruddaa-patch-bundles/bruddaa-dev-patches-bundle.json```

</details>

---
### 📦 Archie9211-Patches-Bundle [Morphe]:
[🧩 Archie9211 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-archie9211-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/archie9211-patch-bundles/archie9211-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/archie9211-patch-bundles/archie9211-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/archie9211-patch-bundles/archie9211-dev-patches-bundle.json```

</details>

---
### 📦 AlecBlance-Patches-Bundle [Morphe]:
[🧩 AlecBlance Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-alecblance-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alecblance-patch-bundles/alecblance-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alecblance-patch-bundles/alecblance-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/alecblance-patch-bundles/alecblance-dev-patches-bundle.json```

</details>

---
### 📦 Enccmp-Patches-Bundle [Morphe]:
[🧩 Enccmp Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-enccmp-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/enccmp-patch-bundles/enccmp-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/enccmp-patch-bundles/enccmp-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/enccmp-patch-bundles/enccmp-dev-patches-bundle.json```

</details>

---
### 📦 Dumketo-Patches-Bundle [Morphe]:
[🧩 Dumketo Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dumketo-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dumketo-patch-bundles/dumketo-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dumketo-patch-bundles/dumketo-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dumketo-patch-bundles/dumketo-dev-patches-bundle.json```

</details>

---
### 📦 Benzophury-Patches-Bundle [Morphe]:
[🧩 Benzophury Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-benzophury-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/benzophury-patch-bundles/benzophury-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/benzophury-patch-bundles/benzophury-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/benzophury-patch-bundles/benzophury-dev-patches-bundle.json```

</details>

---
### 📦 PyFlat-JR-Patches-Bundle [Morphe]:
[🧩 PyFlat-JR Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-pyflat-jr-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pyflat-jr-patch-bundles/pyflat-jr-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pyflat-jr-patch-bundles/pyflat-jr-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/pyflat-jr-patch-bundles/pyflat-jr-dev-patches-bundle.json```

</details>

---
### 📦 Dual-VoT-Patches-Bundle [Morphe]:
[🧩 Dual-VoT Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-dual-vot-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dual-vot-patch-bundles/dual-vot-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dual-vot-patch-bundles/dual-vot-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/dual-vot-patch-bundles/dual-vot-dev-patches-bundle.json```

</details>

---
### 📦 SmartLauncher-Patches-Bundle [Morphe]:
[🧩 SmartLauncher Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-smartlauncher-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/smartlauncher-patch-bundles/smartlauncher-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/smartlauncher-patch-bundles/smartlauncher-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/smartlauncher-patch-bundles/smartlauncher-dev-patches-bundle.json```

</details>

---
### 📦 Rahul9999xda-Telegram-Patches-Bundle [Morphe]:
[🧩 Rahul9999xda-Telegram Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-rahul9999xda-telegram-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rahul9999xda-telegram-patch-bundles/rahul9999xda-telegram-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rahul9999xda-telegram-patch-bundles/rahul9999xda-telegram-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/rahul9999xda-telegram-patch-bundles/rahul9999xda-telegram-dev-patches-bundle.json```

</details>

---
### 📦 6ixfalls-Patches-Bundle [Morphe]:
[🧩 6ixfalls Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-6ixfalls-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/6ixfalls-patch-bundles/6ixfalls-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/6ixfalls-patch-bundles/6ixfalls-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/6ixfalls-patch-bundles/6ixfalls-dev-patches-bundle.json```

</details>

---
### 📦 Letterboxd-Patches-Bundle [Morphe]:
[🧩 Letterboxd Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-letterboxd-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/letterboxd-patch-bundles/letterboxd-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/letterboxd-patch-bundles/letterboxd-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/letterboxd-patch-bundles/letterboxd-dev-patches-bundle.json```

</details>

---
### 📦 YouTube-Studio-Patches-Bundle [Morphe]:
[🧩 YouTube-Studio Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-youtube-studio-bundle-patch-list)
<details>
<summary><b>Bundle URLs</b></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/youtube-studio-patch-bundles/youtube-studio-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/youtube-studio-patch-bundles/youtube-studio-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/youtube-studio-patch-bundles/youtube-studio-dev-patches-bundle.json```

</details>

## 📱 Compatible Managers

| Manager | Best For | Source | Downloads |
| --- | --- | --- | --- |
| Universal ReVanced Manager (my fork) | Importing ReVanced, Morphe, and other third-party patch bundle sources with fewer restrictions. | [Source](https://github.com/Jman-Github/universal-revanced-manager) | [Releases](https://github.com/Jman-Github/universal-revanced-manager/releases) |
| Morphe Manager | Morphe patch bundles and the Morphe patching flow. | [Source](https://github.com/MorpheApp/morphe-manager) | [Releases](https://github.com/MorpheApp/morphe-manager/releases) |
| Official ReVanced Manager | The official ReVanced flow and supported bundle formats. | [Source](https://github.com/ReVanced/revanced-manager) | [Releases](https://github.com/ReVanced/revanced-manager/releases) |

## 🩹 Patch Repositories In Use

<details>
<summary>Expand patch repository links</summary>

#### 🏷️ [ReVanced-Patches-Bundle](https://github.com/revanced/revanced-patches)

#### 🏷️ [Inotia00-Patches-Bundle](https://github.com/inotia00/revanced-Patches)

#### 🏷️ [ProGuard-Patches-Bundle](https://gitlab.com/inotia00/proguard-patches)

#### 🏷️ [MTGA-Patches-Bundle](https://github.com/MaebashiRamens/mtga)

#### 🏷️ [Lain-Patches-Bundle](https://github.com/kiraio-moe/Lain-Patches)

#### 🏷️ [Edge-Morphe-Patches-Bundle](https://github.com/quantavil/edge-morphe-patches)

#### 🏷️ [Anddea-Patches-Bundle](https://github.com/anddea/revanced-patches)

#### 🏷️ [Piko-Patches-Bundle](https://github.com/crimera/piko)

#### 🏷️ [BiliRoamingM-Patches-Bundle](https://github.com/sakarie9/BiliRoamingM)

#### 🏷️ [Slenderman00-Patches-Bundle](https://github.com/Slenderman00/revanced-patches-grindr)

#### 🏷️ [Privacy-Patches-Bundle](https://github.com/jkennethcarino/privacy-revanced-patches)

#### 🏷️ [Experimental-Patches-Bundle](https://github.com/Aunali321/ReVancedExperiments)

#### 🏷️ [Dropped-Patches-Bundle](https://github.com/indrastorms/Dropped-Patches)

#### 🏷️ [Kitadai31-Patches-Bundle](https://github.com/kitadai31/revanced-patches-android6-7)

#### 🏷️ [BholeyKaBhakt-Patches-Bundle](https://github.com/BholeyKaBhakt/android-patches-xtra)

#### 🏷️ [Andronedev-Patches-Bundle](https://github.com/andronedev/morphe-patches)

#### 🏷️ [Korhelyleves-Patches-Bundle](https://github.com/korhelyleves/revanced-patches)

#### 🏷️ [ReX-Patches-Bundle](https://github.com/YT-Advanced/ReX-patches)

#### 🏷️ [Rufusin-Patches-Bundle](https://github.com/rufusin/revanced-patches)

#### 🏷️ [Twitter-Patches-Bundle](https://github.com/IndusAryan/twitter-patches)

#### 🏷️ [Wyse--Patches-Bundle](https://github.com/Wyse-/revanced-patches)

#### 🏷️ [1fexd-Patches-Bundle](https://github.com/1fexd/revanced-patches)

#### 🏷️ [Xrogers-Patches-Bundle](https://github.com/xrogers/revanced-patches-galaxy)

#### 🏷️ [D4n3436-Patches-Bundle](https://github.com/d4n3436/revanced-patches-android5)

#### 🏷️ [AyushTNM-Patches-Bundle](https://github.com/ayushTNM/gmscore-patches)

#### 🏷️ [Arsclib-Patches-Bundle](https://github.com/inotia00/revanced-patches-arsclib)

#### 🏷️ [LennyRBLX-Patches-Bundle](https://github.com/lennyRBLX/apk-patches)

#### 🏷️ [Taknok-Patches-Bundle](https://github.com/Taknok/revanced-patches)

#### 🏷️ [Faith001-Patches-Bundle](https://github.com/Faith001/revanced-molten-glass)

#### 🏷️ [Forsyth47-Patches-Bundle](https://github.com/forsyth47/revanced-patches)

#### 🏷️ [Brosssh-Patches-Bundle](https://github.com/brosssh/morphe-patches)

#### 🏷️ [Quantro100-Patches-Bundle](https://github.com/Quantro100/Morphe-patches)

#### 🏷️ [4831c0-Patches-Bundle](https://github.com/4831c0/custom-revanced-patches)

#### 🏷️ [Chiggi-Patches-Bundle](https://github.com/durgesh0505/chiggi_morphe_patches)

#### 🏷️ [Bakasura-Patches-Bundle](https://github.com/BakasuraRCE/bakasura-patches)

#### 🏷️ [LaKaka-Patches-Bundle](https://github.com/LaKakaReal/LaKakaShitPatches)

#### 🏷️ [LeeeeT-Patches-Bundle](https://github.com/LeeeeT/bt-keepalive-patch)

#### 🏷️ [Vernoxvernax-Patches-Bundle](https://github.com/Vernoxvernax/revanced-patches)

#### 🏷️ [EE-Morphe-Patches-Bundle](https://gitlab.com/early.egg3707/ee-morphe-patches)

#### 🏷️ [X-Shim-Patches-Bundle](https://gitlab.com/inotia00/x-shim)

#### 🏷️ [Pepper-Morphe-Patches-Bundle](https://github.com/PawiX25/pepper-morphe-patches)

#### 🏷️ [Fin-Tweaks-Patches-Bundle](https://github.com/isuruhg/fin-tweaks)

#### 🏷️ [Kondratjev-Patches-Bundle](https://github.com/kondratjev/morphe-patches)

#### 🏷️ [Hoo-dles-Patches-Bundle](https://github.com/hoo-dles/revanced-custom-patches)

#### 🏷️ [VinceTheProgrammer-Patches-Bundle](https://github.com/vinceTheProgrammer/sticknodes-patches)

#### 🏷️ [Hepolise-Patches-Bundle](https://github.com/Hepolise/LuckyToolPatches)

#### 🏷️ [Kangrio-Patches-Bundle](https://github.com/kangrio/MicroG-Patches-Re)

#### 🏷️ [Tosox-Patches-Bundle](https://github.com/Tosox/revanced-patches)

#### 🏷️ [HZbutcoding-Patches-Bundle](https://github.com/HZbutcoding/sn-patching)

#### 🏷️ [Lluni-Patches-Bundle](https://github.com/lluni/custom-revanced-patches)

#### 🏷️ [Bawr-Patches-Bundle](https://github.com/bawr/revanced-patches)

#### 🏷️ [Burgers1312-Patches-Bundle](https://github.com/burgers1312/revanced-patches)

#### 🏷️ [AmpleReVanced-Patches-Bundle](https://github.com/AmpleReVanced/revanced-patches)

#### 🏷️ [Liaralabs-Patches-Bundle](https://github.com/liaralabs/revanced-patches)

#### 🏷️ [Morphe-Patches-Bundle](https://github.com/MorpheApp/morphe-patches)

#### 🏷️ [Patcheddit-Patches-Bundle](https://github.com/wchill/patcheddit)

#### 🏷️ [RVX-Morphed-Patches-Bundle](https://github.com/wchill/rvx-morphed)

#### 🏷️ [Blazskufca-Patches-Bundle](https://github.com/blazskufca/revanced-patch)

#### 🏷️ [IMXEren-Patches-Bundle](https://gitlab.com/IMXEren/mix-patches)

#### 🏷️ [Almewty-Patches-Bundle](https://github.com/Almewty/my-morphe-patches)

#### 🏷️ [Anddea-Morphed-Patches-Bundle](https://github.com/wchill/anddea-rvx-morphed)

#### 🏷️ [RookieEnough-Patches-Bundle](https://github.com/RookieEnough/De-ReVanced)

#### 🏷️ [Adobo-Patches-Bundle](https://github.com/jkennethcarino/adobo)

#### 🏷️ [Alexvbp-Patches-Bundle](https://github.com/Alexvbp/f1tv-patches)

#### 🏷️ [Docbt-Patches-Bundle](https://github.com/Docbt/patched-up)

#### 🏷️ [LoV432-Patches-Bundle](https://github.com/LoV432/revanced-patches)

#### 🏷️ [PixelPusher247-Patches-Bundle](https://github.com/PixelPusher247/morphe-patches)

#### 🏷️ [Rabilrbl-Patches-Bundle](https://github.com/rabilrbl/fluffy-patches)

#### 🏷️ [Jasonwu1994-Patches-Bundle](https://github.com/jasonwu1994/Gboard-patches)

#### 🏷️ [RealCyberwash-Patches-Bundle](https://github.com/realcyberwash/max-patches)

#### 🏷️ [Paresh-Maheshwari-Patches-Bundle](https://gitlab.com/Paresh-Maheshwari/paresh-patches)

#### 🏷️ [Binarymend-Patches-Bundle](https://github.com/binarymend/morphe-patches)

#### 🏷️ [Polka-Bear-Patches-Bundle](https://github.com/polka-bear/morphe-patches)

#### 🏷️ [Eyalm2000-Patches-Bundle](https://github.com/eyalm2000/tidal-debug-menu)

#### 🏷️ [Vladon-Patches-Bundle](https://github.com/vladon/morphe-patches-navi)

#### 🏷️ [Ariecos-Patches-Bundle](https://github.com/ariecos/gemini-patches)

#### 🏷️ [Alim-Zanibekov-Patches-Bundle](https://github.com/alim-zanibekov/ultrasandbox)

#### 🏷️ [Daboynb-Patches-Bundle](https://github.com/daboynb/revanced-instagram-viewonce)

#### 🏷️ [Joristdh-Patches-Bundle](https://github.com/Joristdh/Platypatch)

#### 🏷️ [Meridianfresco-Patches-Bundle](https://github.com/meridianfresco/morphe-meta-patches)

#### 🏷️ [Loskutov-Patches-Bundle](https://github.com/loskutov/youtube-domain-fronting-patch)

#### 🏷️ [Kareemlukitomo-Patches-Bundle](https://github.com/kareemlukitomo/morphe-patches)

#### 🏷️ [Abhis1n-Patches-Bundle](https://github.com/abhis1n/Morphe-Patches)

#### 🏷️ [PawiX25-Patches-Bundle](https://github.com/PawiX25/pepper-revanced-patches)

#### 🏷️ [Ameenalasady-Patches-Bundle](https://github.com/ameenalasady/photogrid-morphe)

#### 🏷️ [Xob0t-Patches-Bundle](https://github.com/xob0t/morphe-patches)

#### 🏷️ [Bannerhub-Patches-Bundle](https://github.com/The412Banner/bannerhub-revanced)

#### 🏷️ [Eksi-Patches-Bundle](https://github.com/HvQ/eksi-morphe)

#### 🏷️ [Ameen-Morphe-Patches-Bundle](https://github.com/ameenalasady/ameen-morphe)

#### 🏷️ [Kolaron-Patches-Bundle](https://github.com/kolaron/morphe-patches)

#### 🏷️ [ImmortalZeus-Patches-Bundle](https://github.com/ImmortalZeus/ImmortalZeus-Morphe-Patches)

#### 🏷️ [Ajstrick81-AndroidTV-Patches-Bundle](https://github.com/ajstrick81/morphe-androidtv-patches)

#### 🏷️ [Icysymmetra-TikTok-Patches-Bundle](https://github.com/icysymmetra/tiktok-patches-for-morphe)

#### 🏷️ [AlexNaga-Patches-Bundle](https://github.com/AlexNaga/android-patches)

#### 🏷️ [Rushiranpise-Patches-Bundle](https://github.com/rushiranpise/morphe-patches)

#### 🏷️ [Sjshb57-PairIP-Patches-Bundle](https://github.com/sjshb57/pairip-patches)

#### 🏷️ [MojiRS-RIF-Patches-Bundle](https://github.com/MojiRS/revanced-rif-patches)

#### 🏷️ [Realme-Link-Patches-Bundle](https://github.com/lyyako/realme-link-patches)

#### 🏷️ [HK-Morphe-Patches-Bundle](https://github.com/humzakh/HK-Morphe-Patches)

#### 🏷️ [BrayDog2010-Patches-Bundle](https://github.com/BrayDog2010/morphe-patches)

#### 🏷️ [TS2-Patches-Bundle](https://github.com/osirisad/teamSnap-patches)

#### 🏷️ [Samsung-Morphe-Patches-Bundle](https://github.com/bigyank/morphe-patches-samsung)

#### 🏷️ [YT-YA-Voiceover-Patches-Bundle](https://github.com/dalapenko/yt-ya.voiceover-android-patches)

#### 🏷️ [Perplexity-STT-Patches-Bundle](https://github.com/dalapenko/perplexity-stt-android-patches)

#### 🏷️ [Browzomje-Patches-Bundle](https://github.com/browzomje/browzomje-patches)

#### 🏷️ [Morphe-Portal-Patches-Bundle](https://github.com/andronedev/morphe-portal-patch)

#### 🏷️ [Zpatches-Patches-Bundle](https://github.com/cesbar/zpatches)

#### 🏷️ [iHealth-Morphe-Patches-Bundle](https://github.com/bdgerszewski/morphe-patches-ihealth)

#### 🏷️ [Hoomans-Morphe-Patches-Bundle](https://github.com/arandomhooman/hoomans-morphe-patches)

#### 🏷️ [AppleMusic-Patches-Bundle](https://github.com/VinkyV/AppleMusicPatches)

#### 🏷️ [Ynotzort-Patches-Bundle](https://github.com/ynotzort/morphe-patches)

#### 🏷️ [Prathxm-Patches-Bundle](https://github.com/PrathxmOp/Prathxm-Patches)

#### 🏷️ [Telegram-Morphe-Patches-Bundle](https://github.com/MoonShadowKeeper/Telegram-patchesMorphe)

#### 🏷️ [Morphe-Screenshot-Patches-Bundle](https://github.com/Pa-kon/morphe-screenshot-patches)

#### 🏷️ [NPCI-BHIM-Patches-Bundle](https://github.com/kun-codes/npci-bhim-morphe-patches)

#### 🏷️ [Prathxm-YTMusic-Patches-Bundle](https://github.com/PrathxmOp/ytmusic-patches)

#### 🏷️ [Nai64-Patches-Bundle](https://github.com/Nai64/Nai64Patches)

#### 🏷️ [Morphe-Google-Patches-Bundle](https://github.com/Ripthulhu/morphe-google-patches)

#### 🏷️ [Xhehab-Patches-Bundle](https://github.com/Xhehab/Xhehab-Patches)

#### 🏷️ [Okish-Morphe-Patches-Bundle](https://github.com/byehi98/okish-morphe-patches)

#### 🏷️ [Bufferk-Patches-Bundle](https://github.com/bufferk/morphe-patches)

#### 🏷️ [Franticg33k-Patches-Bundle](https://github.com/franticg33k/morphe-patches)

#### 🏷️ [Gryphous-Morphe-Patches-Bundle](https://github.com/NekoGryphou/gryphous-morphe-patches)

#### 🏷️ [Coronenic-Patches-Bundle](https://github.com/coronenic/revanced-patches)

#### 🏷️ [Shaun-Sheep-Patches-Bundle](https://github.com/shaun-the-sheep-patches/morphe-patches)

#### 🏷️ [Movistar-Block-Ads-Patches-Bundle](https://github.com/Tornillo2/movistar-block-ads-morphe)

#### 🏷️ [Pinterest-Morphed-Patches-Bundle](https://github.com/SouBryan/pinterest-morphed)

#### 🏷️ [Miguel-Patches-Bundle](https://github.com/MiguelNinja19/miguel-morphe-patches)

#### 🏷️ [Pichiwa-Patches-Bundle](https://github.com/alejandrobellver/pichiwa-patches)

#### 🏷️ [Saiesh-Patches-Bundle](https://github.com/saieshshirodkar/saiesh-morphe-patches)

#### 🏷️ [Letterboxd-Stremio-Patches-Bundle](https://github.com/ethanm6/letterboxd-stremio-morphe-patch)

#### 🏷️ [Cobalt-Morphe-Patches-Bundle](https://github.com/skulldogged/cobalt-morphe)

#### 🏷️ [Proxma-Patches-Bundle](https://github.com/totsiaw/proxma-patches)

#### 🏷️ [Jouss-Patches-Bundle](https://github.com/Joussflls10/Jouss-Patches)

#### 🏷️ [ItsTheJoker-Patches-Bundle](https://github.com/itsthejoker/itsthejoker-patches)

#### 🏷️ [Gmaps-Patches-Bundle](https://github.com/fangkampanat/gmaps-patches)

#### 🏷️ [Seobject-Patches-Bundle](https://github.com/Seobject/Seobject-patches)

#### 🏷️ [Abeja-Patches-Bundle](https://github.com/TheRealCrazyfuy/abeja-morphe-patches)

</details>

#### 🏷️ [RIVanced-Universal-Patches-Bundle](https://github.com/rushiranpise/RI-Vanced-Universal-Morphe-Patches)

#### 🏷️ [Variablenine-Patches-Bundle](https://github.com/variablenine/morphe-patches)

#### 🩹 [Stylus-Patches-Bundle](https://github.com/ch3thanhs/stylus)

#### 🩹 [HXReborn-Patches-Bundle](https://github.com/hxreborn/morphe-patches)

#### 🩹 [Ikura-Patches-Bundle](https://github.com/Ikuradachi/ikura-patches)

#### 🩹 [DH6K-Patches-Bundle](https://github.com/dh6k/morphe-patches)

#### 🩹 [AndrewLiang25-Patches-Bundle](https://github.com/andrewliang25/morphe-patches)

#### 🩹 [Morning-Entree-Patches-Bundle](https://github.com/Entree3k/Morning-Entree-Patches)

#### 🩹 [VocaColle-Patches-Bundle](https://github.com/ilikeadofai/vocacolle-morphe-patches)

#### 🩹 [DBTCoach-Patches-Bundle](https://github.com/mxkrgt/dbtcoach-morphe-patches)

#### 🩹 [Yandex-VoT-Patches-Bundle](https://github.com/MarcaDian/morphe-patches-yavot)


#### 🩹 [Watch-Later-Patches-Bundle](https://github.com/ciraolone/morphe-watch-later)

#### 🩹 [SofaTime-Patches-Bundle](https://github.com/alan7383/sofatime-patches)

#### 🩹 [Hiosdra-Patches-Bundle](https://github.com/Hiosdra/morphe-patches)

#### 🩹 [Jl4cTuk-Patches-Bundle](https://github.com/Jl4cTuk/morphe-patches)

#### 🩹 [Edge-ReVanced-Patches-Bundle](https://github.com/AriesAlex/edge-revanced)

#### 🩹 [LaBlazer-Patches-Bundle](https://github.com/LaBlazer/morphe-patches)

#### 🩹 [D0NJ-Patches-Bundle](https://github.com/d0nj/morphe-patches)

#### 🩹 [TIDAL-Patches-Bundle](https://github.com/chukfinley/tidal-patches)

#### 🩹 [Zarko-Patches-Bundle](https://github.com/eZ4RK0/morphe-patches)

#### 🩹 [Niconico-YT-Patches-Bundle](https://github.com/david419kr/niconico-yt-morphe-patches)

#### 🩹 [Alastor-Kaneki-Patches-Bundle](https://github.com/Alastor-Kaneki/Morphe-Patches)

#### 🩹 [NuvioTV-Patches-Bundle](https://github.com/liongalahad/liongalahad-nuviotv-morphe-patches)

#### 🩹 [GoldRift-Patches-Bundle](https://github.com/GoldRift/morphe-patches)

#### 🩹 [RoundSalmon4-Patches-Bundle](https://github.com/RoundSalmon4/morphe-patches-template)


#### 🩹 [HU-Liberator-Patches-Bundle](https://github.com/hu-liberator/patches)

#### 🩹 [JonnyVR1-Patches-Bundle](https://github.com/JonnyVR1/morph-patches)

#### 🩹 [Logm1lo-Patches-Bundle](https://github.com/logm1lo/logm1lo-patches)

#### 🩹 [SpookyEXE-Patches-Bundle](https://github.com/spookyexe/morphe-patches)

#### 🩹 [PetalMaps-NonHuawei-Patches-Bundle](https://github.com/andersonlucasg3/PetalMaps-NonHuawei)

#### 🩹 [Dbhavsar76-Patches-Bundle](https://github.com/dbhavsar76/revanced-patches)

#### 🩹 [FTL-Patches-Bundle](https://github.com/BlazeFTL/FTL-Patches)

#### 🩹 [braiNtropy-Patches-Bundle](https://github.com/braiNtropy/braintropy-patches)

#### 🩹 [Ang3lo-Patches-Bundle](https://github.com/ang3lo-azevedo/morphe-patches)

#### 🩹 [ChMate-ReVanced-Patches-Bundle](https://github.com/roflsunriz/chmate-revanced)

#### 🩹 [Simnple-Patches-Bundle](https://github.com/simnple/revanced-patches)

#### 🩹 [Heval99-Patches-Bundle](https://github.com/heval99/Heval-Morphe-Patches)

#### 🩹 [Atharv-Patches-Bundle](https://github.com/madhu-gowda6/atharv-patches)

#### 🩹 [Tiaruebar-Patches-Bundle](https://github.com/electiveDev/tiaruebar-patches-vip-fix)

#### 🩹 [FTL-Portal-Patches-Bundle](https://github.com/BlazeFTL/Morphe-Portal-Patches-New)

#### 🩹 [D4NZ-Patches-Bundle](https://github.com/D4NZ-jpg/revanced-patches)

#### 🩹 [Imgur-Patches-Bundle](https://github.com/sushruth/imgur-patches)

#### 🩹 [aapam-Patches-Bundle](https://github.com/WZSE/aapam-patches)

#### 🩹 [RabehX-Patches-Bundle](https://github.com/RabehX/rabehx-patches)

#### 🩹 [Tiaruebar1024-Patches-Bundle](https://github.com/tiaruebar1024/tiaruebar-patches)

#### 🩹 [Slight-Patches-Bundle](https://github.com/HSlightsteel/slight-patches)

#### 🩹 [Riky-Patches-Bundle](https://github.com/riky-dev/morphe-patches)

#### 🩹 [iPusnas-Patches-Bundle](https://github.com/kuchingneko28/ipusnas-patches)

#### 🩹 [HXReborn-TikTok-Patches-Bundle](https://github.com/hxreborn/hxreborn-tiktok-patches)

#### 🩹 [Flexboard-Patches-Bundle](https://github.com/JZ6/Flexboard)

#### 🩹 [Cricinfo-Tweaks-Patches-Bundle](https://github.com/isuruhg/cricinfo-tweaks)

#### 🩹 [RuStore-Privacy-Patches-Bundle](https://github.com/Freeman022026/rustore-privacy-patches)

#### 🩹 [Abhishek-Bhujang-Patches-Bundle](https://github.com/theabhishekbhujang/morphe-patches)

#### 🩹 [MauroGamerVN-Patches-Bundle](https://github.com/MauroGamerVN/morphe-patches)

#### 🩹 [Kveld-Patches-Bundle](https://github.com/kveld9/kveld-morphe-patches)

#### 🩹 [Anime-Witcher-Patches-Bundle](https://github.com/catsmoker/anime-witcher-patches)

#### 🩹 [Expose-Like-Status-in-MediaSession-Patches-Bundle](https://github.com/vasyl91/Expose-like-status-in-MediaSession)

#### 🩹 [Apos-Patches-Bundle](https://github.com/Apostolique/apos-morphe-patches)

#### 🩹 [HH-Patches-Bundle](https://github.com/hhawkinsau/hh-patches)

#### 🩹 [Anxy-Patches-Bundle](https://github.com/anxyis/anxy-patches)

#### 🩹 [Chicco-Patches-Bundle](https://github.com/chicco-carone/morphe-patches-chicco)

#### 🩹 [XTapped-Patches-Bundle](https://github.com/XTapped/morphe-patches)

#### 🩹 [ImNoammm-Spotify-Patches-Bundle](https://github.com/ImNoammm/morphe-spotify-patches)

#### 🩹 [Beetle-Patches-Bundle](https://github.com/homelander11/beetle-patches)

#### 🩹 [Jancerny2001-Patches-Bundle](https://github.com/jancerny2001/morphe-patches)

#### 🩹 [Rhubarbshoelaces-Patches-Bundle](https://github.com/rhubarbshoelaces/morphe-patches)

#### 🩹 [Psychonaut-Wiki-Journal-Patches-Bundle](https://github.com/adderalladmiral/psychonaut-wiki-journal-patches)

#### 🩹 [RedFlagDeals-Patches-Bundle](https://github.com/Deadly-Bytes/redflagdeals-revanced-patches)

#### 🩹 [Dr4w-Patches-Bundle](https://github.com/Dr4w/morphe-patches)

#### 🩹 [Aimal-Patches-Bundle](https://github.com/hashtagbasit/aimal-patches)

#### 🩹 [Gltieo-Patches-Bundle](https://gitlab.com/gltieo/revanced-patches)

#### 🩹 [ShuhaibNC-Patches-Bundle](https://github.com/ShuhaibNC/morphe-patches)

#### 🩹 [Stremio-AndroidTV-Patches-Bundle](https://github.com/liongalahad/liongalahad-stremio-morphe-patches)

#### 🩹 [Bluecxt-Instagram-Patches-Bundle](https://github.com/bluecxt/instagram-revanced-patches)

#### 🩹 [Imgur-ReVanced-Patches-Bundle](https://github.com/roflsunriz/imgur-revanced)

#### 🩹 [Legendsciber-Patches-Bundle](https://github.com/legendsciber/morphe-patches)

#### 🩹 [SteamLink-Patches-Bundle](https://github.com/AngelDark92/steamlink-patches)

#### 🩹 [Nicomanga-ReVanced-Patches-Bundle](https://github.com/roflsunriz/nicomanga-revanced)

#### 🩹 [Froggo-Patches-Bundle](https://github.com/SapitoSucio/FroggoMorphePatches)

#### 🩹 [Kecerim24-Patches-Bundle](https://github.com/Kecerim24/morphe-patches)

#### 🩹 [Z-drgon-Patches-Bundle](https://github.com/Z-drgon/morphe-patches)

#### 🩹 [V4n1X-Patches-Bundle](https://github.com/V4n1X/morphe-patches)

#### 🩹 [RoadSync-Patches-Bundle](https://github.com/subenoeva/roadsync-patches)

#### 🩹 [Jackblk-Patches-Bundle](https://github.com/jackblk/morphe-patches)

#### 🩹 [Educal72-Patches-Bundle](https://github.com/Educal72/educal-patches)

#### 🩹 [Canh0chua-Patches-Bundle](https://github.com/canh0chua/Morphe-patches)

#### 🩹 [Jaredcat-Patches-Bundle](https://github.com/jaredcat/morphe-patches)

#### 🩹 [Dan1elTheMan1el-Patches-Bundle](https://github.com/Dan1elTheMan1el/Morphe-Patches)

#### 🩹 [Csagataj2-Patches-Bundle](https://github.com/csagataj2/morphe-patches)

#### 🩹 [Rafag00-Patches-Bundle](https://github.com/rafag00/morphe-patches)

#### 🩹 [NullWaypoint-Patches-Bundle](https://github.com/NullWaypoint/morphe-patches)

#### 🩹 [DiskWala-Patches-Bundle](https://github.com/kuntal-devrat/diskwala-patches)

#### 🩹 [IPTV-Patches-Bundle](https://github.com/Okazakee/iptv-morphe-patches)

#### 🩹 [Bruddaa-Patches-Bundle](https://github.com/bruddaa/bruddas-morphe-patches)

#### 🩹 [Archie9211-Patches-Bundle](https://github.com/archie9211/morphe-patches)

#### 🩹 [AlecBlance-Patches-Bundle](https://github.com/AlecBlance/android-patches)

#### 🩹 [Enccmp-Patches-Bundle](https://github.com/enccmp/mn-patches)

#### 🩹 [Dumketo-Patches-Bundle](https://github.com/dumketo/multi-app-patches)

#### 🩹 [Benzophury-Patches-Bundle](https://github.com/benzophury/oraimo-health-morphe-patches)

#### 🩹 [PyFlat-JR-Patches-Bundle](https://github.com/PyFlat-JR/Morphe-Patches)

#### 🩹 [Dual-VoT-Patches-Bundle](https://github.com/sashade8-ship-it/dual-vot-patches)

#### 🩹 [SmartLauncher-Patches-Bundle](https://github.com/thejaustin/smartlauncher-morphe-patches)

#### 🩹 [Rahul9999xda-Telegram-Patches-Bundle](https://github.com/rahul9999xda/telegram-morphe-patches)

#### 🩹 [6ixfalls-Patches-Bundle](https://github.com/6ixfalls/revanced-patches)

#### 🩹 [Letterboxd-Patches-Bundle](https://github.com/mvaishak/letterboxd-morphe-patches)

#### 🩹 [YouTube-Studio-Patches-Bundle](https://github.com/HelioFloxZ/YouTube-Studio-Patches)

## 🖇 Integrations Repositories In Use

> [!NOTE]
> This section only applies to legacy integration-based bundles. API v4 and Morphe bundles use newer metadata and are not listed here when they do not rely on a separate integrations repository.

<details>
<summary>Expand integration repository links</summary>

#### ⛓ [BiliRoamingM-Patches-Bundle](https://github.com/sakarie9/BiliRoamingM)

#### ⛓ [Slenderman00-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [ReX-Patches-Bundle](https://github.com/YT-Advanced/ReX-patches)

#### ⛓ [Rufusin-Patches-Bundle](https://github.com/rufusin/revanced-integrations)

#### ⛓ [Twitter-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [Wyse--Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [1fexd-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [Xrogers-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [D4n3436-Patches-Bundle](https://github.com/d4n3436/revanced-integrations)

#### ⛓ [ayushTNM-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [Arsclib-Patches-Bundle](https://github.com/inotia00/revanced-integrations)

#### ⛓ [Hepolise-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

#### ⛓ [Kangrio-Patches-Bundle](https://github.com/ReVanced/revanced-integrations)

</details>

## 📋 Suggestions, Questions & Issues

For issues, suggestions, or questions, open an [issue](https://github.com/Jman-Github/ReVanced-Patch-Bundles/issues/new) or start a [discussion](https://github.com/Jman-Github/ReVanced-Patch-Bundles/discussions). Contributor information is available in [CONTRIBUTING.md](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/CONTRIBUTING.md).

For more patching-related projects and resources, check out [Awesome-ReVanced](https://github.com/Jman-Github/Awesome-ReVanced).

## 🙏 Credits
##### [indrastorms](https://github.com/indrastorms)
Helped with the automation of this repository by using GitHub Actions.

##### [brosssh](https://github.com/brosssh)
Implemented a patch serializer for all `.rvp` (API v4) patch bundles in this
[PR](https://github.com/Jman-Github/ReVanced-Patch-Bundles/pull/85).

## ⭐ Star History

<a href="https://star-history.dera.page/#Jman-Github/Revanced-Patch-Bundles">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=Jman-Github/Revanced-Patch-Bundles&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=Jman-Github/Revanced-Patch-Bundles" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=Jman-Github/Revanced-Patch-Bundles" />
 </picture>
</a>
