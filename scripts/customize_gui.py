#!/usr/bin/env python3
"""Create the fork's self-contained GUI from a pinned upstream CAD MCP page."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / 'plugins/text-to-cad-visual/gui'
REPOSITORY = 'https://github.com/Muilrz/image2_text-to-cad'
UPSTREAM_REPOSITORY = 'https://github.com/earthtojake/text-to-cad'
UPSTREAM_VERSION = '0.7.24'
UPSTREAM_HTML_SHA256 = '6ffd0becce919da5e98f779e8f4f70fc0b05eb19d75ac3b1afac5d33c066bafa'


def sources(document):
    start = document.index('const SOURCES=') + len('const SOURCES=')
    chunks, length = json.JSONDecoder().raw_decode(document[start:])
    return start, start + length, chunks


def document_shell(document):
    for marker in ('const SOURCES=', ',IDS='):
        start = document.index(marker) + len(marker)
        _, length = json.JSONDecoder().raw_decode(document[start:])
        document = document[:start] + '{}' + document[start + length:]
    return document


def customize(original):
    if hashlib.sha256(original).hexdigest() != UPSTREAM_HTML_SHA256:
        raise ValueError('Unexpected upstream GUI build; review its changes before updating this patch')
    document = original.decode('utf-8')
    start, end, chunks = sources(document)
    changed, locale_count = [], 0
    for name, encoded in chunks.items():
        script = gzip.decompress(base64.b64decode(encoded)).decode('utf-8')
        if '"menu.madeBy":' not in script:
            continue
        # Modify the translated author text, not the author's X handle or link.
        script, count = re.subn(r'("menu\.madeBy":`[^`]*\{handle\})([^`]*`)',
                                lambda m: m[1] + ', Ming Liu' + m[2], script)
        if count != 5:
            raise ValueError(f'Unexpected language table in {name}: {count} author labels')
        if script.count('github:`' + UPSTREAM_REPOSITORY + '`') != 1:
            raise ValueError('Expected one menu GitHub URL')
        script = script.replace('github:`' + UPSTREAM_REPOSITORY + '`', 'github:`' + REPOSITORY + '`')
        # Feedback belongs to the fork too; avoid routing fork bugs to the upstream project.
        if script.count('issues:`' + UPSTREAM_REPOSITORY + '/issues/new`') != 1:
            raise ValueError('Expected one feedback URL')
        script = script.replace('issues:`' + UPSTREAM_REPOSITORY + '/issues/new`',
                                'issues:`' + REPOSITORY + '/issues/new`')
        # This label still describes cadgen, so its release notes stay with upstream.
        if script.count('release:o||kv(r,c)') != 1:
            raise ValueError('Unexpected release-notes link contract')
        script = script.replace('release:o||kv(r,c)',
                                'release:o||kv(`' + UPSTREAM_REPOSITORY + '`,c)')
        # The patched chunk no longer matches upstream's error-reporting source map.
        script, debug_ids = re.subn(r'(?m)^//# debugId=[^\r\n]+', '', script)
        if debug_ids != 1:
            raise ValueError('Unexpected debug ID contract')
        chunks[name] = base64.b64encode(gzip.compress(script.encode('utf-8'), compresslevel=9, mtime=0)).decode('ascii')
        changed.append(name)
        locale_count += count
    if len(changed) != 1:
        raise ValueError(f'Expected exactly one modified UI chunk, got {changed}')
    result = document[:start] + json.dumps(chunks, separators=(',', ':')) + document[end:]
    # Preserve the loader and IDs for all unmodified chunks; omit only the patched map entry.
    ids_start = result.index(',IDS=') + len(',IDS=')
    ids, length = json.JSONDecoder().raw_decode(result[ids_start:])
    for name in changed:
        ids.pop(name, None)
    result = result[:ids_start] + json.dumps(ids, separators=(',', ':')) + result[ids_start + length:]
    return result.encode('utf-8'), changed, locale_count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream-html', type=Path, help='cadgen 0.7.24 _runtime/mcp/index.html')
    args = parser.parse_args(argv)
    if args.upstream_html:
        upstream = args.upstream_html
    else:
        from cadgen.assets import runtime_root
        upstream = runtime_root() / 'mcp/index.html'
    original = upstream.read_bytes()
    customized, changed, locales = customize(original)
    GUI.mkdir(parents=True, exist_ok=True)
    (GUI / 'index.html').write_bytes(customized)
    _, _, upstream_chunks = sources(original.decode('utf-8'))
    unchanged = {name:hashlib.sha256(gzip.decompress(base64.b64decode(value))).hexdigest()
                 for name,value in upstream_chunks.items() if name not in changed}
    provenance = {'upstream_repository':UPSTREAM_REPOSITORY, 'upstream_version':UPSTREAM_VERSION,
                  'upstream_html_sha256':hashlib.sha256(original).hexdigest(),
                  'custom_html_sha256':hashlib.sha256(customized).hexdigest(),
                  'modified_chunks':changed, 'unchanged_chunk_sha256':unchanged,
                  'original_document_shell_sha256':hashlib.sha256(document_shell(original.decode('utf-8')).encode('utf-8')).hexdigest(),
                  'author':'earthtojake, Ming Liu',
                  'author_name_suffix':', Ming Liu', 'author_locales_modified':locales,
                  'github':REPOSITORY, 'issues':REPOSITORY + '/issues/new',
                  'license':'MIT; upstream and bundled license notices retained'}
    (GUI / 'source.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'gui':str(GUI), 'bytes':len(customized), 'modified_chunks':changed,
                      'author_locales_modified':locales}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
