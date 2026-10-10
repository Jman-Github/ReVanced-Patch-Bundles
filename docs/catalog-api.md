# Catalog API

Browse and try requests in [Swagger UI](https://patch-bundles.jmancentral.com/api-docs/) or explore the GraphQL schema in [GraphiQL](https://patch-bundles.jmancentral.com/graphiql/).

API base: `https://patch-bundles.api.jmancentral.com`. [OpenAPI specification](https://patch-bundles.api.jmancentral.com/api.json).

## REST

| Method and path | Result |
| --- | --- |
| GET `/refresh-jobs` | Recent refresh runs, including queued, running and failed jobs. |
| GET `/api/v1/refresh/status/:jobId` | Refresh status; 202 while pending/running, 200 when finished. |
| GET `/health` | Catalog generation and counts. |
| GET `/sources`, `/sources/:id` | Registered sources, aliases, enabled status and repository metadata. |
| GET `/bundles`, `/releases`, `/bundles/:id` | Current and historical releases. |
| GET `/packages` | Compatible package names and recorded app versions. |
| GET `/patches`, `/bundles/:id/patches` | Patch descriptions and app compatibility. |
| GET `/availability` | Unavailable channels and retired source records. |
| GET `/api/v3/bundle?source_url=...&version=...&channel=...` | Manager import information. |
| GET `/api/v1/bundle/:id` | Legacy import using a numeric bundle ID. |
| GET `/api/v1/bundle/:owner/:repo/:version` | Legacy repository import for an exact tag or `latest`. |
| GET `/api/v2/bundle/:owner/:repo/latest?channel=...` | Legacy repository channel import. |

The API supports GitHub, GitLab, Codeberg, Gitea and configured self-hosted servers. GitLab subgroup paths and encoded API URLs normalize to repository URLs.

Disabled sources remain in source queries with `enabled: false` and an `unavailable_reason`. Their bundles and patches are excluded from browsing, relationships and manager imports; saved history is retained for re-enabling the source.

For v3 imports, use an exact release tag or `version=latest`. Latest requires `channel=any|stable|prerelease`; `latest` and `dev` are accepted aliases. Channel values accept surrounding whitespace and any capitalization. Exact-version requests can omit channel. Latest imports and default website cards use the newest stable release and newest prerelease across retained history, independently of configured channel pointers.

V1 latest defaults to stable; `prerelease=true` selects prereleases. V2 requires a channel. V1/V2 owner and repository paths use recorded repository metadata, including current names after a rename and sources on other supported hosts. V1/V2 return the upstream five-field response: `created_at`, `description`, `version`, `download_url` and `signature_download_url`. V3 adds bundle format, source information and metadata status.

Collection/detail endpoints also accept `/api/v1`, for example `/api/v1/patches`. REST records retain their catalog hash in `id`; `legacy_id` supplies the numeric ID used by legacy imports and GraphQL. Numeric IDs remain stable across refreshes and belong to this catalog. IDs from another catalog installation cannot be reused here.

Lists return `{data,total,limit,offset}`. Defaults: limit 25, offset 0. Limits: 1–100; offset: 0–10000. Use `sort` and `order=asc|desc`. Bundles accept `q`, `source` (ID, alias or URL), `source_url`, `ecosystem`, `channel`, `version`, `package` and `metadata_status`.

Patch search accepts `q`, exact `package`, `app_version`, `bundle_id`, source/ecosystem/channel filters and `include_unverified=true`. REST patch results default to verified metadata. A null version restriction means every app version is compatible. An explicitly empty version collection means no versions are supported and creates no package relationship. Legacy annotation defaults retain their unrestricted meaning.

Patch searches return one window of candidate shards. Follow `next_cursor` as `page_cursor`, keeping filters unchanged. Use offset to read additional rows within that window. Counts and sorting apply to the current window.

## GraphQL

Send JSON `{query,variables,operationName}` to `/graphql`, `/v1/graphql` or `/hasura/v1/graphql`. GET query parameters also work. GraphiQL provides schema documentation, completion and request execution.

The public read-only schema exposes all seven reference tables: `source`, `source_metadata`, `bundle`, `patch`, `package`, `patch_package` and `refresh_jobs`. Each has a `_by_pk` lookup; `patch_package` uses both `package_fk` and `patch_fk`. The six catalog tables expose `_aggregate` roots; refresh jobs follow the reference public role without aggregation.

Relationships work in both directions, including `source_metadatum`, source bundles, bundle patches and patch/package links. IDs and foreign keys use integers. `catalog_id` retains the hash used in REST and website links. The `release` alias and `patch(package_name:...,bundle_id:...,q:...)` shortcuts are also available.

Queries support variables, defaults, aliases, fragments, directives, introspection, logical and relationship filters, `distinct_on`, ordering with explicit null placement, and pagination. Aggregates provide counts (including distinct columns), nodes, min/max, sums, averages, variance and standard deviation. Array relationships support aggregate filters and ordering. Boolean aggregate filters accept `bool_and` and `bool_or` predicates with optional filters and distinct values. Boolean aggregates ignore null inputs and return null for an empty or all-null set.

Comparisons include equality, membership, null tests, ranges, LIKE/ILIKE (including escaped wildcards), their negations, regular expressions and SIMILAR TO. Nested boolean filters preserve PostgreSQL NULL semantics: negating a comparison does not include records with missing values; use `_is_null` to request them explicitly. Regex filters follow PostgreSQL advanced regular-expression syntax, including backreferences, lookahead/lookbehind, POSIX classes, word boundaries, embedded options and basic/extended/literal modes. SIMILAR TO uses SQL wildcards and whole-string matching. Character classes and simple case conversion use PostgreSQL's `en_US.utf8` locale by default, including international letters and word boundaries. ILIKE uses the same locale case conversion. The registry can select a precomputed locale profile; `C`/`POSIX` and `C.UTF-8` are also supported. Patterns remain limited to 512 characters and interpreted matching has a shared work budget per query. Expensive expressions return a budget error instead of blocking the API.

Bundle `created_at` and source metadata `repo_pushed_at` are strings, matching the upstream schema. Provider timestamp strings retain their timezone spelling and fractional seconds. They support string variables, LIKE/regex, text ordering, min/max and streaming cursors. V1/V2/V3 manager-import responses omit a trailing `Z` for upstream compatibility while retaining fractional seconds. Refresh-job `started_at` and `completed_at` remain timestamps and compare instants across timezone offsets.

Text range comparisons, sorting and string min/max use the same deterministic PostgreSQL collation. The default profile is libc `en_US.utf8` from glibc 2.36, including multi-character collation elements; `C`/`POSIX` and `C.UTF-8` use UTF-8 byte ordering. Precomputed patch statistics use the configured catalog locale as well.

Morphe compatibility accepts iterable collections, and absent patch descriptions remain null for GraphQL filtering. Patch names can be null or empty; the website displays “Unnamed patch” and preserves their descriptions and compatibility. A verified bundle can contain zero patches. Permanent bundle rejections set `need_patches_update` to false without marking metadata verified. Artifact or runtime changes make those bundles eligible again; temporary download or worker failures remain eligible for retry.

GraphQL exposes recorded patch metadata, including fallback and stale lists. Inspect `metadata_status` and `patch_metadata_version`, or filter for `metadata_status: {_eq: "verified"}`. This makes freshness explicit without hiding historical records.

```graphql
query Latest($url: String!) {
  bundle(where: {source: {url: {_eq: $url}}, is_latest: {_eq: true}}, limit: 5) {
    id catalog_id version bundle_type file_hash need_patches_update metadata_status
    source { id url source_metadata: source_metadatum { owner_name repo_name repo_stars } }
    patches(where: {metadata_status: {_eq: "verified"}}, limit: 30) {
      id name description
      patch_packages(limit: 50) { package { id name version } }
    }
    patches_aggregate { aggregate { count } nodes { name } }
  }
}
```

```graphql
{
  bundle_by_pk(id: 1) { version source { url } }
  source(where: {bundles_aggregate: {count: {predicate: {_gt: 0}}}}) { url }
  package_aggregate { aggregate { count(columns: [name], distinct: true) } }
}
```

Live subscriptions use WebSockets at the same GraphQL paths. Both `graphql-transport-ws` and the legacy `graphql-ws` protocol are supported. GraphiQL can run subscription operations. Clients receive an initial result and changed results as the registry refreshes, checked every second against the latest published checkpoint. Every evaluation keeps the same query and response limits. Each connection supports four operations; idle connections require initialization within 30 seconds.

Cursor streaming subscriptions are available as `bundle_stream`, `patch_stream`, `source_stream`, `source_metadata_stream`, `package_stream`, `patch_package_stream` and `refresh_jobs_stream`. Supply `batch_size` (1–100) and a `cursor` with `initial_value` and optional `ordering: ASC|DESC`. Each batch contains rows strictly after the previous cursor; the server retains progress across subscription polling and hibernation. Cursor columns need not appear in the selected response. Use a unique sortable cursor such as `id` to receive each record once. Non-unique cursors include boundary ties; a group exceeding 100 rows returns an error so records are not silently skipped. Existing query, shard and response budgets still apply. Empty polls do not emit a batch.

```graphql
subscription NewBundles {
  bundle_stream(batch_size: 25, cursor: [{initial_value: {id: 0}, ordering: ASC}]) {
    id version bundle_type source { url }
  }
}
```

The `is_latest` flag identifies the newest stable release and newest prerelease separately for each source, across bundle formats and retained history. Configured channel pointers remain available independently through `channels` and REST channel filters; manager latest imports use `is_latest`.

Refresh-job queries combine separate `BUNDLES` discovery and `PATCHES` extraction records with recent GitHub Actions refresh runs (`ALL`). Statuses are STARTED (including queued phases), COMPLETED and FAILED; cancellation is reported as FAILED. The status endpoint accepts a phase's UUID `job_id` or a numeric Actions run ID and returns the upstream fields `jobId`, `type`, `status`, `startedAt`, `completedAt` and `error`. Collection and GraphQL records retain snake_case field names. Phase status follows catalog checkpoints. Actions status may be cached for up to two minutes without authentication, or 15 seconds with an optional server-side status token.

Mutations, triggering administrative jobs and database administration remain outside the public read-only API.

## Freshness and request limits

Release history is discovered independently of current channels. Historical patch extraction proceeds in background batches, so newly discovered versions may initially have missing patch lists. Morphe and legacy metadata produced before the compatibility format update is requeued and remains unverified until re-extracted. During a refresh, validated checkpoints publish available results about every 30 seconds and at phase transitions. The site checks for a new generation every 15 seconds while visible; subscriptions check every second. GitHub's content delivery cache can add delay. Readers fall back to the deployed site's catalog if the branch catalog is unavailable.

A verified list was parsed from the matching binary artifact and has matching artifact and patch-list digests. Fallback metadata remains unverified. `need_patches_update` is true while extraction is missing, stale or unverified. Full release notes are available from bundle collections, detail and manager endpoints.

Each request uses one immutable generation and checks fetched file hashes. GitHub snapshot reads use the commit recorded in the manifest, so cached manifests remain usable after newer generations are published. Responses support ETags and conditional GET. API cache lifetime is 60 seconds. Refresh-status responses are not cached, and subscription evaluations read the manifest afresh.

Queries have bounded input, output and work: 100 rows per selection (25 by default), 36 catalog files, 12 MiB catalog input, 2 MiB response and at most 24 patch shards per GraphQL scan. POST bodies are limited to 32 KiB; normal queries to depth 8, 300 fields and complexity 20,000. Standard schema introspection is allowed separately.

Narrow broad queries by source, bundle or package when a budget is exceeded. REST returns 422; GraphQL execution reports an error. The API implements the reference public query surface over catalog snapshots, with these limits; it does not run a Hasura database server.

Phase UUIDs remain queryable across catalog refreshes, including older completed jobs. Job collections and GraphQL fall back to published job records when live Actions status is temporarily unavailable; individual numeric Actions-run lookups still require live status. Collection queries retain their existing pagination and response limits.

Repository availability is reported in each source's `unavailable_reason`: permanent upstream errors include `404: Not Found`, `410: Gone` and `451: Unavailable For Legal Reasons`. The reason clears after release discovery and repository metadata both recover. A temporary upstream outage preserves previously published releases; the configured `disabled` switch remains separate.

Release replacements update the existing source/version/category record and preserve its public ID. Provider asset digests invalidate extracted patch metadata when an artifact changes at the same URL.
