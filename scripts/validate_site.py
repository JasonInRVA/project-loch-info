import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
HTML_FILES = [ROOT / "index.html", ROOT / "library.html"]
MANIFEST_PATH = ROOT / "docs" / "manifest.json"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if "id" in attributes and attributes["id"]:
            self.ids.add(attributes["id"])
        if tag == "a" and attributes.get("href"):
            self.links.append((attributes["href"], self.getpos()[0]))


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def validate_manifest(records: list[dict]) -> list[str]:
    errors = []
    paths = set()
    for record in records:
        archived_path = record["archived_path"]
        if archived_path in paths:
            errors.append(f"Duplicate archived_path in manifest: {archived_path}")
        paths.add(archived_path)

        file_path = ROOT / archived_path
        if not file_path.exists():
            errors.append(f"Missing archived file: {archived_path}")

    return errors


def validate_html_file(path: Path) -> list[str]:
    errors = []
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))

    for href, line_number in parser.links:
        if href.startswith(("http://", "https://", "mailto:", "javascript:")):
            continue
        if href.startswith("#"):
            anchor = href[1:]
            if anchor and anchor not in parser.ids:
                errors.append(f"{path.name}:{line_number} missing in-page anchor #{anchor}")
            continue

        parsed = urlparse(href)
        target_path = (path.parent / parsed.path).resolve()
        if not target_path.exists():
            errors.append(f"{path.name}:{line_number} missing linked file {href}")
            continue

        if parsed.fragment:
            target_parser = LinkParser()
            target_parser.feed(target_path.read_text(encoding="utf-8"))
            if parsed.fragment not in target_parser.ids:
                errors.append(
                    f"{path.name}:{line_number} missing fragment {parsed.fragment} in {parsed.path}"
                )

    return errors


def main() -> None:
    records = load_manifest()
    errors = validate_manifest(records)
    for html_file in HTML_FILES:
        errors.extend(validate_html_file(html_file))

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print(f"Validated manifest entries: {len(records)}")
    for html_file in HTML_FILES:
        print(f"Validated links in {html_file.name}")


if __name__ == "__main__":
    main()
