"""Generate a reviewable license bundle from the active build environment."""

from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path, PurePosixPath

MAX_LICENSE_BYTES = 2 * 1024 * 1024


def _declared_license(distribution: metadata.Distribution) -> str:
    expression = distribution.metadata.get("License-Expression", "").strip()
    if expression:
        return expression
    declared = distribution.metadata.get("License", "").strip()
    if declared:
        return " ".join(declared.split())
    classifiers = distribution.metadata.get_all("Classifier", [])
    licenses = [
        value.removeprefix("License :: OSI Approved :: ")
        for value in classifiers
        if value.startswith("License :: OSI Approved :: ")
    ]
    return ", ".join(licenses) or "Not declared in package metadata"


def _license_texts(distribution: metadata.Distribution) -> list[tuple[str, str]]:
    available = {str(item).replace("\\", "/"): item for item in distribution.files or ()}
    collected: list[tuple[str, str]] = []
    for declared_path in distribution.metadata.get_all("License-File", []):
        normalized = declared_path.replace("\\", "/")
        relative = PurePosixPath(normalized)
        if relative.is_absolute() or ".." in relative.parts:
            continue
        package_path = available.get(normalized)
        if package_path is None:
            continue
        located = Path(distribution.locate_file(package_path))
        try:
            if not located.is_file() or located.stat().st_size > MAX_LICENSE_BYTES:
                continue
            raw_text = located.read_text(encoding="utf-8", errors="replace")
            text = "\n".join(line.rstrip() for line in raw_text.splitlines()).strip()
        except OSError:
            continue
        if text:
            collected.append((normalized, text))
    return collected


def build_license_bundle() -> str:
    sections = [
        "Metrora third-party license inventory",
        "Generated from the exact Python environment used to build this application.",
        "Package metadata remains the authoritative source for each dependency.",
    ]
    seen: set[tuple[str, str]] = set()
    packages = []
    for distribution in metadata.distributions():
        name = distribution.metadata.get("Name", "Unknown package").strip()
        version = distribution.version
        identity = (name.casefold(), version)
        if identity in seen or name.casefold() == "metrora":
            continue
        seen.add(identity)
        packages.append((name.casefold(), name, version, distribution))

    for _, name, version, distribution in sorted(packages):
        sections.extend(
            [
                "",
                "=" * 78,
                f"{name} {version}",
                f"Declared license: {_declared_license(distribution)}",
            ]
        )
        license_texts = _license_texts(distribution)
        if not license_texts:
            sections.append("No license file was declared in the installed package metadata.")
            continue
        for relative_path, contents in license_texts:
            sections.extend(["", f"--- {relative_path} ---", contents])
    return "\n".join(sections).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.output.write_text(build_license_bundle(), encoding="utf-8")


if __name__ == "__main__":
    main()
