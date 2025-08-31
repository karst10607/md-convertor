#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def find_main_content(soup: BeautifulSoup, selector: str | None = None):
    # Prefer an explicit selector if provided
    if selector:
        node = soup.select_one(selector)
        if node:
            return node
    # Confluence common containers
    for sel in [
        '#main-content',
        'div#content',
        'div#page',
        'article',
        'div#main',
        'div#content-body',
        'div.content',
    ]:
        node = soup.select_one(sel)
        if node:
            return node
    # Fallback to body
    return soup.body or soup


def relativize(from_path: Path, to_path: Path) -> str:
    """Return a POSIX-style relative path from from_path's parent to to_path."""
    rel = os.path.relpath(to_path, start=from_path.parent)
    return Path(rel).as_posix()


def resolve_href(base_html_path: Path, href: str) -> Path | None:
    # Ignore empty and hash-only anchors
    if not href or href.startswith('#'):
        return None
    # Protocols we leave unchanged (mailto:, http:, https:, data:)
    lowered = href.lower()
    if any(lowered.startswith(pfx) for pfx in ('http://', 'https://', 'mailto:', 'tel:', 'data:')):
        return None
    # Make it absolute based on the input html file location
    return (base_html_path.parent / href).resolve()


def preprocess_links_and_images(content: BeautifulSoup, in_html: Path, out_md: Path):
    # Images: keep source images in place; make markdown point to correct relative path from out_md
    for img in content.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        abs_img = resolve_href(in_html, src)
        if abs_img is None:
            # leave external/data URIs unchanged
            continue
        # Compute rel path from output markdown location to the absolute image path
        new_src = relativize(out_md, abs_img)
        img['src'] = new_src

    # Links: convert internal .html links to .md and fix relative path
    for a in content.find_all('a'):
        href = a.get('href')
        if not href:
            continue
        # Allow same-page anchors
        if href.startswith('#'):
            continue
        abs_target = resolve_href(in_html, href)
        if abs_target is None:
            # external link, leave as-is
            continue
        # If it points to an HTML file inside the pack, switch to .md
        if abs_target.suffix.lower() in {'.html', '.htm'}:
            abs_target_md = abs_target.with_suffix('.md')
            new_href = relativize(out_md, abs_target_md)
            a['href'] = new_href
        else:
            # Non-HTML target: still fix relative path so it doesn't break
            a['href'] = relativize(out_md, abs_target)


def html_to_markdown(html_str: str) -> str:
    # Configure markdownify for better output
    return md(
        html_str,
        heading_style="ATX",
        strip=['style', 'script'],
        bullets='*',
        code_language=False,
        escape_asterisks=False,
        escape_underscores=False,
    ).strip() + "\n"


def convert_file(in_path: Path, out_root: Path, in_root: Path, main_selector: str | None):
    rel = in_path.relative_to(in_root)
    out_path = out_root / rel.with_suffix('.md')
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open('r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'lxml')

    content = find_main_content(soup, main_selector)

    # Preprocess links and images so markdown gets correct targets
    preprocess_links_and_images(content, in_path, out_path)

    md_text = html_to_markdown(str(content))

    with out_path.open('w', encoding='utf-8') as f:
        f.write(md_text)

    return out_path


def convert_directory(input_dir: Path, output_dir: Path, main_selector: str | None = None):
    html_exts = {'.html', '.htm'}
    converted = []
    for path in input_dir.rglob('*'):
        if path.is_file() and path.suffix.lower() in html_exts:
            out_path = convert_file(path, output_dir, input_dir, main_selector)
            converted.append((path, out_path))
    return converted


def parse_args():
    p = argparse.ArgumentParser(
        description='Convert a Confluence HTML export pack into Markdown without copying images (paths preserved).'
    )
    p.add_argument('-i', '--input', required=True, type=Path, help='Path to Confluence HTML export root directory')
    p.add_argument('-o', '--output', required=True, type=Path, help='Output directory for Markdown files')
    p.add_argument('--main-selector', default=None, help='CSS selector to pick main content (default tries common Confluence containers)')
    return p.parse_args()


def main():
    args = parse_args()
    input_dir: Path = args.input.resolve()
    output_dir: Path = args.output.resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist or is not a directory: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    results = convert_directory(input_dir, output_dir, args.main_selector)

    print(f"Converted {len(results)} HTML files to Markdown.")
    if len(results) == 0:
        print("No .html files found. Check your input path.")


if __name__ == '__main__':
    main()
