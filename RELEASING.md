# Releasing

Releases are created through the `Release` GitHub Actions workflow.

## Versioning

The project follows Semantic Versioning while it is in alpha. The version in `pyproject.toml` is the source of truth.

Before a release:

1. update `pyproject.toml`;
2. update `CHANGELOG.md`;
3. ensure the `main` branch CI and CodeQL workflows are green;
4. commit the release preparation changes.

## Publishing a release

Open **Actions → Release → Run workflow** and enter the version exactly as it appears in `pyproject.toml`, without the `v` prefix.

For example:

```text
0.1.0
```

The workflow validates the requested version, runs lint and tests, builds both wheel and source distributions, validates package metadata, creates an annotated `vX.Y.Z` tag, and publishes a GitHub Release with generated notes and the distribution artifacts attached.

The workflow refuses to overwrite an existing tag or release.

## PyPI

PyPI publishing is intentionally not automatic. It should be enabled only after the package name, public API, and trusted-publisher configuration are finalized. GitHub Release artifacts remain the canonical downloadable builds until then.
