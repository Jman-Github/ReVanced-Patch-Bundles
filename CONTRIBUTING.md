# Contributing

Help improve the catalog by suggesting a source, reporting a problem, or submitting a pull request.

## Suggest a patch source

Open an [issue](https://github.com/Jman-Github/Patch-Bundle-Registry/issues) with the repository URL, bundle format, and available release channels.

To submit a source directly, edit [config/sources.json](config/sources.json) and follow an existing entry for the same format and hosting provider.

- Use a GitHub repository API URL or an encoded GitLab project API URL in `patches`.
- Give each entry a unique key ending in `-latest`, `-stable`, or `-dev`.
- Set `latest: true` for latest, `prerelease: false` for stable, or `prerelease: true` for dev.
- Include `integration` when a legacy bundle needs a separate integrations repository.
- Include `disabled: false` for an active source. Setting it to `true` disables every channel and format from that repository; an optional `unavailable_reason` explains why.

Include an example release artifact. Catalog snapshots are generated automatically; source submissions should change the inventory rather than generated data.

## Report a problem

Include the source, selected version, and steps to reproduce the issue. For compatibility problems, include your manager and app version.

## Code contributions

Follow the surrounding code style and include relevant validation with your pull request. Python tests run with `python -m pytest`; API tests run with `npm test`.

Keep the existing site layout and retain upstream attribution and license notices when changing adapted frontend files.

For questions, use [Discussions](https://github.com/Jman-Github/Patch-Bundle-Registry/discussions).
