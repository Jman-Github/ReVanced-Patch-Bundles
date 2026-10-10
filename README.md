<div align="center">

# Patch Bundle Registry

Find community patches for your favorite Android apps.

**[Browse the catalog](https://patch-bundles.jmancentral.com/)** · [Try the API](https://patch-bundles.jmancentral.com/api-docs/) · [API reference](docs/catalog-api.md) · [Suggest a source](https://github.com/Jman-Github/Patch-Bundle-Registry/issues)

</div>

---

Patch Bundle Registry brings ReVanced and Morphe patch sources together in one searchable catalog. Explore available patches, check app compatibility, and find the right bundle for your manager.

## Find your patches

- **Search** by source, patch name, or description.
- **Check compatibility** with the package filter. Use an app's package name, such as `com.google.android.youtube`, an app-version fragment such as `19.16`, or an exact combination: `com.google.android.youtube@19.16.39`.
- **Choose a release** using the source, version, bundle format, and release filters.
- **Explore a bundle** to read its changelog and patch list.

Switch between list and grid views to browse the way you prefer.

## Add a bundle to your manager

1. Open the [catalog](https://patch-bundles.jmancentral.com/) and find a source.
2. Choose a bundle format your manager supports.
3. Click **Copy remote bundle URL** and paste it into your manager's patch source settings.

The default remote URL follows new releases in the selected channel. Select a historical bundle version to copy a URL pinned to that version.

You can also download the bundle directly from its card. Available formats and import support depend on the manager you use.

## Releases and patch lists

| Channel | What you'll find |
| --- | --- |
| Latest | The newest release, including prereleases. |
| Stable | The newest regular release. |
| Dev | The newest prerelease. |

Sources can come from GitHub, GitLab, Codeberg, Gitea and supported self-hosted servers. Some sources do not publish every channel. Select a source to browse its release history; older patch lists are filled in as the catalog refreshes. New results appear while an update is running.

Patch lists display their status: **verified**, **unverified**, **stale**, or **missing**. A verified list was extracted from its matching bundle. An unverified or stale list may still help you explore patches, but may not describe the selected release accurately.

## API

Building a manager or another integration? The catalog provides a read-only [REST and GraphQL API](docs/catalog-api.md) for sources, bundles, patches, and app compatibility. Explore requests in [Swagger UI](https://patch-bundles.jmancentral.com/api-docs/) or [GraphiQL](https://patch-bundles.jmancentral.com/graphiql/). Subscribe to catalog changes over WebSockets, or check refresh-job status while an update runs.

## Contribute or get help

[Suggest a patch source or report a problem](https://github.com/Jman-Github/Patch-Bundle-Registry/issues). Include the source's repository URL and a description of what you found. For general questions, visit [Discussions](https://github.com/Jman-Github/Patch-Bundle-Registry/discussions).

Pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits and license

Thanks to **indrastorms** for helping automate updates, and **brosssh** for patch serialization and [ReVanced External Bundles](https://github.com/brosssh/revanced-external-bundles), whose website layout this catalog uses.

The project uses the [Unlicense](LICENSE). The adapted website files use [GPL-3.0-only](web/COPYING); see [source attribution](docs/source-attribution.md).
