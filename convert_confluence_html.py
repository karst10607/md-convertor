#!/usr/bin/env python3
import argparse
import os
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urlparse, urlunparse


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


def resolve_href(base_html_path: Path, href: str) -> tuple[Path, str, str] | None:
    """Resolve href into absolute filesystem path and return (abs_path, fragment, query).

    External protocols return None.
    Hash-only anchors return None.
    """
    if not href:
        return None
    parsed = urlparse(href)
    if parsed.scheme in ('http', 'https', 'mailto', 'tel', 'data'):
        return None
    if not parsed.path and parsed.fragment:
        # hash-only anchor
        return None
    abs_path = (base_html_path.parent / (parsed.path or '')).resolve()
    return abs_path, parsed.fragment, parsed.query


def copy_image_to_output(abs_img: Path, out_md: Path, out_root: Path) -> str:
    """Copy image to a dedicated 'images' folder in the output root and return the new relative path."""
    # Define a dedicated images directory in the output root
    out_images_dir = out_root / 'images'
    out_images_dir.mkdir(parents=True, exist_ok=True)

    # Handle potential filename conflicts
    out_img_path = out_images_dir / abs_img.name
    counter = 1
    while out_img_path.exists():
        out_img_path = out_images_dir / f"{abs_img.stem}-{counter}{abs_img.suffix}"
        counter += 1

    # Copy the image, preserving metadata
    shutil.copy2(abs_img, out_img_path)

    # Return the new relative path from the Markdown file to the copied image
    return relativize(out_md, out_img_path)


def preprocess_links_and_images(content: BeautifulSoup, in_html: Path, out_md: Path, out_root: Path):
    # Images: copy to output directory and update paths
    for img in content.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        resolved = resolve_href(in_html, src)
        if resolved is None:
            # leave external/data URIs unchanged
            continue
        abs_img, frag, query = resolved
        
        # Check if image file exists
        if abs_img.exists() and abs_img.is_file():
            # Copy image and get new relative path
            new_src = copy_image_to_output(abs_img, out_md, out_root)
        else:
            # Image doesn't exist, keep original relative path
            new_src = relativize(out_md, abs_img)
        
        # Re-append query/fragment if present
        if query or frag:
            new_src = urlunparse(('', '', new_src, '', query, f'#{frag}' if frag else ''))
        img['src'] = new_src

    # Links: convert internal .html links to .md and fix relative path
    for a in content.find_all('a'):
        href = a.get('href')
        if not href:
            continue
        # Same-page anchors handled in resolve_href
        resolved = resolve_href(in_html, href)
        if resolved is None:
            # external link, leave as-is
            continue
        abs_target, frag, query = resolved
        # If it points to an HTML file inside the pack, switch to .md
        if abs_target.suffix.lower() in {'.html', '.htm'}:
            abs_target_md = abs_target.with_suffix('.md')
            new_href = relativize(out_md, abs_target_md)
        else:
            # Non-HTML target: still fix relative path so it doesn't break
            new_href = relativize(out_md, abs_target)
        # Re-append query/fragment if present
        if query or frag:
            new_href = urlunparse(('', '', new_href, '', query, f'#{frag}' if frag else ''))
        a['href'] = new_href


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
    preprocess_links_and_images(content, in_path, out_path, out_root)

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
