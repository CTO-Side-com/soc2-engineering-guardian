"""Documentation invariants for SKILL.md, references and templates."""
from pathlib import Path
import json
import re
import unittest

SKILL=Path(__file__).resolve().parents[1]
SKILL_MD=SKILL/'SKILL.md'
TEMPLATES=[SKILL/'assets'/'SYSTEM-DESCRIPTION.md',SKILL/'assets'/'SUBSERVICE-VENDOR-REGISTER.md']

def frontmatter(text):
    lines=text.splitlines()
    assert lines and lines[0]=='---','missing frontmatter'
    end=lines.index('---',1)
    top,meta,section={},{},None
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line.startswith((' ','\t')):
            key,_,value=line.strip().partition(':')
            if section=='metadata':
                meta[key.strip()]=value.strip().strip('"')
            continue
        key,_,value=line.partition(':')
        section=key.strip()
        top[section]=value.strip()
    return top,meta,'\n'.join(lines[end+1:])

class SkillDocTests(unittest.TestCase):
    def test_frontmatter(self):
        top,meta,_=frontmatter(SKILL_MD.read_text(encoding='utf-8'))
        self.assertEqual(top['name'],'soc2-engineering-guardian')
        self.assertEqual(top['license'],'MIT')
        self.assertEqual(meta.get('version'),'1.1.0')
        self.assertTrue(meta.get('author'))
        self.assertLessEqual(len(top['description']),1024)
        self.assertIn('SOC 2',top['description'])

    def test_relative_links_resolve(self):
        files=[SKILL_MD]+sorted((SKILL/'references').glob('*.md'))+sorted((SKILL/'assets').glob('*.md'))
        checked=0
        for f in files:
            for target in re.findall(r'\]\(([^)\s]+)\)',f.read_text(encoding='utf-8')):
                if re.match(r'^([a-z]+:|#|mailto:)',target):
                    continue
                path=(f.parent/target.split('#')[0]).resolve()
                self.assertTrue(path.exists(),f'{f.name}: broken link {target}')
                self.assertTrue(path.is_relative_to(SKILL.resolve()),f'{f.name}: link leaves skill {target}')
                checked+=1
        self.assertGreater(checked,0)

    def test_templates_are_marked_unverified(self):
        for t in TEMPLATES:
            self.assertTrue(t.exists(),f'missing {t.name}')
            self.assertIn('INTERNAL / UNVERIFIED TEMPLATE',t.read_text(encoding='utf-8'))

    def test_skill_body_under_500_lines(self):
        _,_,body=frontmatter(SKILL_MD.read_text(encoding='utf-8'))
        self.assertLess(len(body.splitlines()),500)

    def test_skill_states_rule_count(self):
        text=SKILL_MD.read_text(encoding='utf-8')
        self.assertRegex(text,r'\b17 (regex )?(scanner )?rules')
        self.assertNotIn('13 regex',text)

    def test_ai_threats_cite_existing_checks(self):
        known={c['id'] for c in json.loads((SKILL/'references'/'controls.json').read_text(encoding='utf-8'))['controls']}
        cited=set(re.findall(r'\b[A-Z]{2,3}-\d{3}\b',(SKILL/'references'/'ai-saas-threats.md').read_text(encoding='utf-8')))
        self.assertTrue(cited,'no check ids cited')
        self.assertFalse(cited-known,f'unknown check ids: {sorted(cited-known)}')

    def test_install_guide_has_public_commands(self):
        text=(SKILL/'references'/'installation.md').read_text(encoding='utf-8')
        self.assertIn('/plugin install soc2-engineering-guardian@ctoside-soc2',text)
        self.assertIn('gh skill install CTO-Side-com/soc2-engineering-guardian soc2-engineering-guardian',text)

    def test_vendor_register_wording(self):
        text=(SKILL/'assets'/'SUBSERVICE-VENDOR-REGISTER.md').read_text(encoding='utf-8')
        self.assertIn('unmodified',text)
        self.assertNotIn('unqualified',text)
        bridge=[l for l in text.splitlines() if l.startswith('- **Bridge letter')]
        self.assertEqual(len(bridge),1)
        self.assertIn('not an auditor opinion',bridge[0])

    def test_outputs_section_precedes_no_safety_text(self):
        heading=None
        for para in re.split(r'\n\s*\n',SKILL_MD.read_text(encoding='utf-8')):
            for line in para.splitlines():
                if line.startswith('## '):
                    heading=line
            if 'independent CPA engagement' in para:
                self.assertIsNotNone(heading)
                self.assertNotEqual(heading,'## Outputs')
                return
        self.fail('closing safety paragraph not found')

if __name__=='__main__':
    unittest.main()
