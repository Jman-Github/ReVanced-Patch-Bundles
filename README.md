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

For the actual patch contents, use the [Patch List Catalog](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md) or [Patch Explorer](https://paresh-maheshwari.github.io/patch-explorer/) by [Paresh-Maheshwari](https://github.com/Paresh-Maheshwari).

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
### 📦 Nk521-Patches-Bundle [API v4]:
[🧩 Nk521 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-nk521-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nk521-patch-bundles/nk521-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nk521-patch-bundles/nk521-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/nk521-patch-bundles/nk521-dev-patches-bundle.json```
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
### 📦 Areteruhiro-Patches-Bundle [API v4]:
[🧩 Areteruhiro Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-areteruhiro-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/areteruhiro-patch-bundles/areteruhiro-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/areteruhiro-patch-bundles/areteruhiro-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/areteruhiro-patch-bundles/areteruhiro-dev-patches-bundle.json```
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
### 📦 Aniketshinde007-Patches-Bundle [Morphe]:
[🧩 Aniketshinde007 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-aniketshinde007-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aniketshinde007-patch-bundles/aniketshinde007-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aniketshinde007-patch-bundles/aniketshinde007-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/aniketshinde007-patch-bundles/aniketshinde007-dev-patches-bundle.json```
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
### 📦 Ajstrick81-Patches-Bundle [Morphe]:
[🧩 Ajstrick81 Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-ajstrick81-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ajstrick81-patch-bundles/ajstrick81-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ajstrick81-patch-bundles/ajstrick81-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/ajstrick81-patch-bundles/ajstrick81-dev-patches-bundle.json```
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
### 📦 RaiuSky-Patches-Bundle [Morphe]:
[🧩 RaiuSky Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-raiusky-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/raiusky-patch-bundles/raiusky-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/raiusky-patch-bundles/raiusky-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/raiusky-patch-bundles/raiusky-dev-patches-bundle.json```
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
### 📦 Joganubaid-Patches-Bundle [Morphe]:
[🧩 Joganubaid Bundle Patch List](https://github.com/Jman-Github/ReVanced-Patch-Bundles/blob/bundles/patch-bundles/PATCH-LIST-CATALOG.md#-joganubaid-bundle-patch-list)
<details>
<summary><i>Expand For Links</i></summary>

**Latest:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/joganubaid-patch-bundles/joganubaid-latest-patches-bundle.json```

**Stable:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/joganubaid-patch-bundles/joganubaid-stable-patches-bundle.json```

**Dev:** ```https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/joganubaid-patch-bundles/joganubaid-dev-patches-bundle.json```
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

#### 🏷️ [Brosssh-Patches-Bundle](https://github.com/brosssh/revanced-patches)

#### 🏷️ [Hoo-dles-Patches-Bundle](https://github.com/hoo-dles/revanced-custom-patches)

#### 🏷️ [VinceTheProgrammer-Patches-Bundle](https://github.com/vinceTheProgrammer/sticknodes-patches)

#### 🏷️ [Hepolise-Patches-Bundle](https://github.com/Hepolise/LuckyToolPatches)

#### 🏷️ [Kangrio-Patches-Bundle](https://github.com/kangrio/MicroG-Patches-Re)

#### 🏷️ [Nk521-Patches-Bundle](https://github.com/nk521/revanced-patches)

#### 🏷️ [Tosox-Patches-Bundle](https://github.com/Tosox/revanced-patches)

#### 🏷️ [HZbutcoding-Patches-Bundle](https://github.com/HZbutcoding/sn-patching)

#### 🏷️ [Lluni-Patches-Bundle](https://github.com/lluni/custom-revanced-patches)

#### 🏷️ [Bawr-Patches-Bundle](https://github.com/bawr/revanced-patches)

#### 🏷️ [Burgers1312-Patches-Bundle](https://github.com/burgers1312/revanced-patches)

#### 🏷️ [AmpleReVanced-Patches-Bundle](https://github.com/AmpleReVanced/revanced-patches)

#### 🏷️ [Liaralabs-Patches-Bundle](https://github.com/liaralabs/revanced-patches)

#### 🏷️ [Areteruhiro-Patches-Bundle](https://github.com/areteruhiro/linegms)

#### 🏷️ [Morphe-Patches-Bundle](https://github.com/MorpheApp/morphe-patches)

#### 🏷️ [Patcheddit-Patches-Bundle](https://github.com/wchill/patcheddit)

#### 🏷️ [RVX-Morphed-Patches-Bundle](https://github.com/wchill/rvx-morphed)

#### 🏷️ [Blazskufca-Patches-Bundle](https://github.com/blazskufca/revanced-patch)

#### 🏷️ [IMXEren-Patches-Bundle](https://github.com/IMXEren/mix-patches)

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

#### 🏷️ [Paresh-Maheshwari-Patches-Bundle](https://github.com/paresh-maheshwari/paresh-patches)

#### 🏷️ [Aniketshinde007-Patches-Bundle](https://github.com/aniketshinde007/morphe-patches-ani)

#### 🏷️ [Binarymend-Patches-Bundle](https://github.com/binarymend/morphe-patches)

#### 🏷️ [Polka-Bear-Patches-Bundle](https://github.com/polka-bear/morphe-patches)

#### 🏷️ [Ajstrick81-Patches-Bundle](https://github.com/ajstrick81/peacock-atv-patches)

#### 🏷️ [Eyalm2000-Patches-Bundle](https://github.com/eyalm2000/tidal-debug-menu)

#### 🏷️ [Vladon-Patches-Bundle](https://github.com/vladon/morphe-patches-navi)

#### 🏷️ [RaiuSky-Patches-Bundle](https://github.com/RaiuSky/patches-repo)

#### 🏷️ [Ariecos-Patches-Bundle](https://github.com/ariecos/gemini-patches)

#### 🏷️ [Joganubaid-Patches-Bundle](https://github.com/joganubaid/adguard-morphe-patches)

#### 🏷️ [Alim-Zanibekov-Patches-Bundle](https://github.com/joganubaid/alim-zanibekov/ultrasandbox)

#### 🏷️ [Daboynb-Patches-Bundle](https://github.com/daboynb/revanced-instagram-viewonce)

#### 🏷️ [Joristdh-Patches-Bundle](https://github.com/Joristdh/Platypatch)

#### 🏷️ [Meridianfresco-Patches-Bundle](https://github.com/meridianfresco/morphe-meta-patches)

#### 🏷️ [Loskutov-Patches-Bundle](https://github.com/loskutov/youtube-domain-fronting-patch)

</details>

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

<a href="https://www.star-history.com/?repos=Jman-Github%2FRevanced-Patch-Bundlestype=date&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=Jman-Github/Revanced-Patch-Bundles&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=Jman-Github/Revanced-Patch-Bundles&type=date&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=Jman-Github/Revanced-Patch-Bundles&type=date&legend=top-left" />
  </picture>
</a>
