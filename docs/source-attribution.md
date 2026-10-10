# Source attribution and licensing

The website is adapted from [ReVanced External Bundles](https://github.com/brosssh/revanced-external-bundles) by brosssh and its contributors, at revision `3a59398d667c83cd7033f859f3cb59237da92b3f`.

## Website

| File | Upstream source |
| --- | --- |
| `web/index.html` | [HTML](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/static/index.html) |
| `web/style.css` | [Stylesheet](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/static/style.css) |
| `web/app.js` | [JavaScript](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/static/app.js) |

The original layout and virtualized cards are retained. Catalog loading, search, patch details, import URLs, and source management have been adapted for this project. Unused administrative controls and styles have been removed.

These adapted files retain their original authorship and use **GPL-3.0-only**. The license text is included in [web/COPYING](../web/COPYING) and the published website. Source notices and upstream permalinks appear in each file.

The corresponding website source is available in `web/`, `shared/catalog.js`, and the site-generation scripts and configuration in this repository. Third-party fonts and JavaScript dependencies retain their own licenses.

## Other project code

The independently written API, catalog generator, and runtime integration retain the project's [Unlicense](../LICENSE). The shared catalog module is independently written under that license and is GPL-compatible when distributed with the website. No reference backend source or compiled patcher runtime is included; runtime dependencies retain their upstream licenses.

Thanks to **indrastorms** for helping automate updates and **brosssh** for patch serialization and the original External Bundles website.

## Reference behavior

Host routing, paginated release-history discovery, historical extraction scheduling and public API compatibility follow the behavior of the same upstream revision:

- [Release asset and detached-signature behavior](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/integrations/common/GitHostClient.kt): independently implemented in `scripts/release_assets.py`, shared by current-channel and historical discovery.
- [Release date column types](https://github.com/brosssh/revanced-external-bundles/tree/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/db/tables): the independent GraphQL implementation retains upstream text dates for bundles and repository metadata, and timestamp dates for refresh jobs.
- [Latest stable/prerelease ranking](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/db/functions/BundleFunctions.kt): independently implemented by the catalog generator.
- [HostResolver](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/integrations/HostResolver.kt)
- [Worker restart and shared-deadline behavior](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/workers/PatchWorkerClient.kt): independently implemented in the isolated parser workers.
- [Background workers](https://github.com/brosssh/revanced-external-bundles/tree/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/workers)
- [Legacy ReVanced loader behavior](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/workers/loaders/revanced/v3/ReVancedV3PatchLoader.kt) and [runtime fallback configuration](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/patcher-runtimes.toml): independently implemented reflection and bytecode readers; no upstream backend source is included.
- [API routes](https://github.com/brosssh/revanced-external-bundles/tree/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/api)
- [Hasura public-role metadata](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/hasura/metadata.json)

These backend behaviors are independently implemented for immutable JSON snapshots and the Worker API. No AGPL backend source has been copied. The adapted website package/version filtering remains covered by its existing GPL notice.

Interactive documentation uses Swagger UI (Apache-2.0), GraphiQL and React (MIT). These dependencies retain their own licenses. PostgreSQL regex matching is independently implemented from the [official pattern-matching documentation](https://www.postgresql.org/docs/17/functions-matching.html). The ASCII character-name mapping in `worker/src/postgres-character-names.js` is adapted from [PostgreSQL regc_locale.c](https://github.com/postgres/postgres/blob/35c508af520963bf1245b86f437c21f834cc2be0/src/backend/regex/regc_locale.c) and retains its original Scriptics copyright and permissive license notice. `worker/src/postgres-locales.json` contains generated character-class and case-conversion results from PostgreSQL with the libc `en_US.utf8` collation. It contains lookup data, not PostgreSQL implementation code. No reference backend code is copied.

Streaming cursor behavior follows the [Hasura streaming-subscription documentation](https://hasura.io/docs/2.0/subscriptions/postgres/streaming/index/); its schema and snapshot implementation are independently written.

`shared/postgres-collation-data.json` contains generated collation lookup data from Debian's `locales-all_2.36-9+deb12u14_amd64.deb`, using glibc's `en_US.utf8` locale. The [locale definitions](https://github.com/bminor/glibc/blob/glibc-2.36/localedata/locales/iso14651_t1_common) state that the Free Software Foundation claims no copyright interest in the locale data. The JavaScript and Python table readers are independently written, using the documented PostgreSQL deterministic-collation behavior and the glibc locale data format as references; no glibc implementation code is incorporated. Their ordering is checked against native libc `strcoll` with the pinned locale data, including backward runs where libc's `strxfrm` sort keys produce different results.

Release replacement and digest invalidation follow [BundleRepository](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/repositories/BundleRepository.kt). Source availability and persistent job-status behavior follow [RefreshBundlesJobService](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/domain/services/jobs/RefreshBundlesJobService.kt) and [RefreshJobRepository](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/repositories/RefreshJobRepository.kt). These behaviors are independently implemented; no backend source is copied.

Nullable patch names/descriptions, iterable compatibility collections, null-versus-empty version restrictions and successful empty extraction results follow [PatchSnapshotMapper](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/workers/loaders/common/PatchSnapshotMapper.kt). Permanent rejection classification and rescheduling follow [PatchWorkerManager](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/workers/PatchWorkerManager.kt) and [RefreshPatchesJobService](https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/domain/services/jobs/RefreshPatchesJobService.kt). These behaviors are independently implemented for this project's snapshot pipeline; no upstream backend source is copied.

Repeated package compatibility entries and latest-before-history extraction scheduling also follow the linked PatchSnapshotMapper and RefreshPatchesJobService behavior. These are independent implementations for the catalog pipeline.
