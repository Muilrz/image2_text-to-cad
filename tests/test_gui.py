from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/text-to-cad-visual'
GUI = PLUGIN / 'gui'


def chunks():
    text = (GUI / 'index.html').read_text(encoding='utf-8')
    start = text.index('const SOURCES=') + len('const SOURCES=')
    data, _ = json.JSONDecoder().raw_decode(text[start:])
    return {name:gzip.decompress(base64.b64decode(value)).decode('utf-8') for name,value in data.items()}


class GuiTests(unittest.TestCase):
    def test_author_and_repository_are_visible_in_every_language(self):
        scripts = chunks()
        labels = re.findall(r'"menu\.madeBy":`([^`]+)`', '\n'.join(scripts.values()))
        self.assertEqual(len(labels), 5)
        self.assertTrue(all('{handle}, Ming Liu' in label for label in labels))
        self.assertIn('由 @{handle}, Ming Liu 制作', labels)
        joined = '\n'.join(scripts.values())
        self.assertIn('github:`https://github.com/Muilrz/image2_text-to-cad`', joined)
        self.assertIn('issues:`https://github.com/Muilrz/image2_text-to-cad/issues/new`', joined)
        self.assertIn('x:`https://x.com/earthtojake`', joined)
        self.assertNotIn('github:`https://github.com/earthtojake/text-to-cad`', joined)

    def test_gui_provenance_and_license_preserved(self):
        source = json.loads((GUI / 'source.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((GUI / 'index.html').read_bytes()).hexdigest(), source['custom_html_sha256'])
        self.assertEqual(source['upstream_version'], '0.7.24')
        self.assertEqual((GUI / 'LICENSE').read_bytes(), (ROOT / 'LICENSE').read_bytes())
        scripts = chunks()
        self.assertEqual(len(scripts), 43)
        loader = importlib.util.spec_from_file_location('gui_customizer', ROOT / 'scripts/customize_gui.py')
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        shell = module.document_shell((GUI / 'index.html').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256(shell.encode('utf-8')).hexdigest(), source['original_document_shell_sha256'])
        for name, expected in source['unchanged_chunk_sha256'].items():
            self.assertEqual(hashlib.sha256(scripts[name].encode('utf-8')).hexdigest(), expected)
        for name in source['modified_chunks']:
            self.assertNotIn('//# debugId=', scripts[name])

    def test_codex_gui_is_plugin_relative_and_runtime_pin_unchanged(self):
        for name in ('codex.mcp.json', 'mcp.json'):
            config = json.loads((PLUGIN / name).read_text(encoding='utf-8'))['mcpServers']['cad_visual']
            self.assertEqual(config['cwd'], './', 'Agent Plugins rejects bare . and hides the MCP service')
            resource = (PLUGIN / config['env']['CADGEN_MCP_APP_DIR']).resolve()
            self.assertEqual(resource, GUI.resolve())
            self.assertTrue((resource / 'index.html').is_file())
            self.assertEqual(config['args'], ['--no-config','--managed-python','--python','3.13','--from','cadgen==0.7.24','cadgen','mcp'])

    def test_json_authors_and_codex_display_are_distinct(self):
        found = []
        def visit(value):
            if isinstance(value, dict):
                for key,entry in value.items():
                    if key == 'author' and isinstance(entry, dict):
                        found.append(entry['name'])
                    visit(entry)
            elif isinstance(value, list):
                for entry in value:
                    visit(entry)
        for path in PLUGIN.rglob('*.json'):
            visit(json.loads(path.read_text(encoding='utf-8-sig')))
        self.assertGreaterEqual(len(found), 5)
        self.assertEqual(set(found), {'Ming Liu'})
        manifest = json.loads((PLUGIN / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['interface']['developerName'], 'earthtojake, Ming Liu')
        self.assertEqual(manifest['repository'], 'https://github.com/Muilrz/image2_text-to-cad')

    def test_customizer_rejects_unknown_upstream_build(self):
        spec = importlib.util.spec_from_file_location('customize_gui', ROOT / 'scripts/customize_gui.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaisesRegex(ValueError, 'Unexpected upstream GUI build'):
            module.customize(b'<html>unknown upstream</html>')


if __name__ == '__main__':
    unittest.main()
