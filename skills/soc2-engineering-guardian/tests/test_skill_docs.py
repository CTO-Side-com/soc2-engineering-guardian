"""Documentation invariants for SKILL.md, references and templates."""
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

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
        files=[SKILL_MD]+sorted((SKILL/'references').glob('*.md'))
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

if __name__=='__main__':
    unittest.main()
