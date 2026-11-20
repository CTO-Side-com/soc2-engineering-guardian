"""Repository-level checks for the public face of the project.

These files (README, images, manifests, CI) are not installed with the skill, so the
skill's own suite cannot cover them. Standard library only.
"""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'soc2-engineering-guardian'
REPO_URL = 'https://github.com/CTO-Side-com/soc2-engineering-guardian'
SVG_NS = '{http://www.w3.org/2000/svg}'


def _skill_version():
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    match = re.search(r'^\s+version:\s*"([^"]+)"', text, re.M)
    assert match, 'SKILL.md metadata.version not found'
    return match.group(1)


class ReadmeTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / 'README.md').read_text(encoding='utf-8')

    def test_readme_links_and_images_resolve(self):
        targets = re.findall(r'(?<!\!)\[[^\]]*\]\(([^)\s]+)\)', self.text)
        targets += re.findall(r'<img[^>]+src="([^"]+)"', self.text)
        targets += re.findall(r'!\[[^\]]*\]\(([^)\s]+)\)', self.text)
        local = [t for t in targets if not re.match(r'^(https?:|mailto:|#)', t)]
        self.assertTrue(local, 'README has no relative links or images')
        images = [t for t in re.findall(r'<img[^>]+src="([^"]+)"', self.text)]
        self.assertGreaterEqual(len(images), 5)
        for target in local:
            path = target.split('#', 1)[0]
            if not path:
                continue
            self.assertTrue((ROOT / path).exists(), 'README target missing: ' + target)
        for target in targets:
            if target.startswith('#'):
                anchor = target[1:]
                headings = {self._slug(h) for h in re.findall(r'^#{1,6}\s+(.+)$', self.text, re.M)}
                self.assertIn(anchor, headings, 'README anchor has no heading: ' + target)

    @staticmethod
    def _slug(heading):
        slug = re.sub(r'[^\w\s-]', '', heading.strip().lower())
        return re.sub(r'\s', '-', slug)

    def test_preview_image_is_small(self):
        size = (ROOT / 'docs' / 'images' / 'report-preview.png').stat().st_size
        self.assertLess(size, 400 * 1024)

    def test_readme_is_current(self):
        for stale in ('bundle', 'publication was not completed', '13 conservative'):
            self.assertNotIn(stale, self.text.lower(), 'stale README text: ' + stale)
        for needed in ('17', '/plugin install soc2-engineering-guardian@ctoside-soc2',
                       '/plugin marketplace add CTO-Side-com/soc2-engineering-guardian'):
            self.assertTrue(needed in self.text, 'README lacks: ' + needed)

    def test_readme_keeps_not_a_report_notice(self):
        self.assertIn('not a SOC 2 report', self.text)
        self.assertIn('## Boundaries', self.text)


class SvgTests(unittest.TestCase):
    NAMES = ('workflow', 'evidence-model', 'control-library', 'outputs')

    def test_svgs_are_accessible(self):
        for name in self.NAMES:
            path = ROOT / 'docs' / 'images' / (name + '.svg')
            self.assertTrue(path.exists(), name + '.svg missing')
            root = ET.parse(path).getroot()
            self.assertEqual(root.tag, SVG_NS + 'svg')
            title = root.find(SVG_NS + 'title')
            desc = root.find(SVG_NS + 'desc')
            self.assertIsNotNone(title, name + ' has no <title>')
            self.assertIsNotNone(desc, name + ' has no <desc>')
            self.assertTrue((title.text or '').strip())
            self.assertGreater(len((desc.text or '').strip()), 40)
            self.assertEqual(root.get('width'), '960')


class ManifestTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / '.claude-plugin' / name).read_text(encoding='utf-8'))

    def test_manifests(self):
        plugin = self.load('plugin.json')
        market = self.load('marketplace.json')
        version = _skill_version()
        self.assertEqual(version, '1.1.0')
        self.assertEqual(plugin['name'], 'soc2-engineering-guardian')
        self.assertEqual(plugin['version'], version)
        self.assertEqual(plugin['homepage'], REPO_URL)
        self.assertEqual(plugin['repository'], REPO_URL)
        self.assertEqual(plugin['category'], 'security')
        self.assertEqual(market['name'], 'ctoside-soc2')
        self.assertEqual(len(market['plugins']), 1)
        entry = market['plugins'][0]
        self.assertEqual(entry['name'], plugin['name'])
        self.assertEqual(entry['version'], version)
        self.assertEqual(entry['homepage'], REPO_URL)
        self.assertEqual(entry['repository'], REPO_URL)
        self.assertEqual(entry['category'], 'security')
        self.assertEqual(entry['source'], './')


class CiTests(unittest.TestCase):
    def test_ci_pins_runner(self):
        text = (ROOT / '.github' / 'workflows' / 'tests.yml').read_text(encoding='utf-8')
        self.assertRegex(text, r'runs-on:\s*ubuntu-24\.04')
        self.assertNotRegex(text, r'runs-on:\s*ubuntu-latest')
        self.assertIn('fail-fast: false', text)
        self.assertIn('3.9', text)
        self.assertIn('python -m unittest discover -s tests -v', text)
        self.assertIn('python -m unittest discover -s skills/soc2-engineering-guardian/tests -v', text)
        self.assertIn('python docs/build_example.py', text)
        self.assertNotIn('paths:', text)


if __name__ == '__main__':
    unittest.main()
