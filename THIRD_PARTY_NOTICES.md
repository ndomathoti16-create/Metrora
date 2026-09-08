# Third-party notices

Metrora depends on third-party Python packages and GitHub Actions listed in `pyproject.toml` and the
workflow files under `.github/workflows`. Those components remain subject to their respective
licenses and notices. Installing optional `cloud`, `desktop`, or `dev` extras adds the corresponding
provider SDK, desktop runtime, packaging, and verification dependencies.

The interface uses operating-system font fallbacks and does not download web fonts at runtime.
Product screenshots and the Metrora SVG mark in this repository are project assets rather than
stock imagery.

The Windows release workflow generates `THIRD_PARTY_LICENSES.txt` from the exact build environment
and includes it alongside this notice in the portable application. The generated inventory should
be reviewed whenever dependencies change and before redistributing a build.
