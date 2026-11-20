"""The synthetic example must validate and make the report show every section."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import load
from render_report import summarize
from validate_assessment import validate

PATH=Path(__file__).resolve().parents[1]/'assets/assessment-example.json'

class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.data=load(PATH);self.controls={c['id']:c for c in self.data['controls']}
        self.summary=summarize(self.data)
        self.gaps=[i for i in self.summary['items'] if i['kind']=='gap']
    def test_example_validates(self):
        self.assertEqual([],validate(self.data))
    def test_example_shows_every_section(self):
        self.assertEqual('type2-readiness',self.data['mode'])
        keys={g['key'] for g in self.gaps}
        self.assertGreaterEqual(len(self.gaps),5)
        self.assertEqual({'design','operation'},{g['dimension'] for g in self.gaps})
        self.assertGreaterEqual(len({g['severity'] for g in self.gaps}),3)
        self.assertLessEqual({'DAT-001-design','CHG-001-operation'},keys)
        self.assertGreaterEqual(sum(c['design_status']=='verified' for c in self.data['controls']),2)
        ev={e['id']:e for e in self.data['evidence']};period=self.data['period']
        verified=[c for c in self.data['controls'] if c['operation_status']=='verified']
        self.assertGreaterEqual(len(verified),1)
        for c in verified:
            self.assertTrue(any(ev[r]['type'] in ('operational','test','external_report')
                and ev[r]['period']==period for r in c['operation_evidence']))
            self.assertGreater(c['population']['reviewed'],0)
        for cid in ('AI-001','AI-002','AI-003'):
            c=self.controls[cid]
            self.assertEqual(('not_applicable','not_applicable'),(c['design_status'],c['operation_status']))
            self.assertTrue(c['approved_by'].strip())
    def test_example_has_period_rows_for_covered_and_uncovered_dates(self):
        rows=self.summary['period'];self.assertGreaterEqual(len(rows),2)
        self.assertTrue(any(not r['uncovered'] and r['covered'] for r in rows))
        self.assertTrue(any(r['uncovered'] for r in rows))
    def test_example_is_synthetic(self):
        for key in ('assessor','product'):self.assertIn('Synthetic',self.data[key])
        for ev in self.data['evidence']:self.assertIn('Synthetic',ev['reviewer'])
        for c in self.data['controls']:
            if c['reviewer']:self.assertIn('Synthetic',c['reviewer'])
        self.assertNotIn('@',PATH.read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
