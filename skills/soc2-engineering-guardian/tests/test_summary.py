"""Tests for the shared summary model, urgency hints, Markdown sections and risk register."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import library
from init_assessment import create
from validate_assessment import validate
from render_report import DEFAULTS,ORDER,render,summarize

HEADER=['Item','Control','Dimension','Title','Criteria','Finding','Kind','Urgency','Owner','Due','Action','Done when','Evidence']

class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31')
    def evidence(self,kind='operational',start='2026-08-01',end='2026-10-31',eid='E1'):
        return {'id':eid,'type':kind,'ref':'controlled-records/review.json','method':'Reviewed synthetic records',
            'reviewer':'Synthetic Reviewer','environment':'production','collected_on':'2026-11-01',
            'period':{'start':start,'end':end}}
    def check(self,cid):
        return next(c for c in self.a['controls'] if c['id']==cid)
    def gap(self,cid,dimension,status='failed',severity='low',evidence=('E1',)):
        c=self.check(cid)
        c.update({dimension+'_status':status,dimension+'_evidence':list(evidence),'rationale':'Synthetic finding for '+cid,
            'reviewer':'Synthetic Reviewer','owner':'Owner','severity':severity,'recommendation':'Repair '+cid,
            'verification_test':'Retest '+cid,'due_date':'2026-12-01'})
        return c
    def type1_all_verified(self):
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31','type1-readiness')
        self.a['evidence']=[self.evidence('code')]
        for c in self.a['controls']:
            c.update(design_status='verified',design_evidence=['E1'],rationale='Synthetic design reviewed',reviewer='Synthetic Reviewer')
        self.assertEqual([],validate(self.a))
    def register(self,root):
        with Path(root,'risk-register.csv').open(newline='',encoding='utf-8') as f:return list(csv.reader(f))
    def render_md(self):
        with tempfile.TemporaryDirectory() as root:
            render(self.a,root);return Path(root,'SOC2-READINESS.md').read_text()

    def test_every_check_has_a_priority_hint(self):
        cs=library()['controls']
        for c in cs:self.assertIn(c.get('priority_hint'),ORDER,c['id'])
        hints={c['id']:c['priority_hint'] for c in cs}
        for cid in ('IAM-002','IAM-003','IAM-004','DAT-003','AI-001'):self.assertEqual('critical',hints[cid])
    def test_blank_type2_has_106_evidence_requests(self):
        s=summarize(self.a);self.assertEqual(106,len(s['items']));self.assertTrue(all(i['kind']=='evidence_request' for i in s['items']))
        self.assertFalse(s['type1']);self.assertEqual(53,sum(s['design_counts'].values()))
    def test_blank_type1_has_53_design_items_only(self):
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31','type1-readiness');s=summarize(self.a)
        self.assertEqual(53,len(s['items']));self.assertEqual({'design'},{i['dimension'] for i in s['items']});self.assertTrue(s['type1'])
    def test_items_ordered_gaps_then_urgency_then_id(self):
        self.a['evidence']=[self.evidence('code')]
        self.gap('GOV-001','design','failed','low');self.gap('IAM-001','design','partially_verified','critical');self.gap('CHG-001','design','failed','high')
        keys=[i['key'] for i in summarize(self.a)['items']]
        self.assertEqual(['CHG-001-design','GOV-001-design','IAM-001-design'],keys[:3])
        kinds=[i['kind'] for i in summarize(self.a)['items']];self.assertEqual(['gap']*3,kinds[:3]);self.assertEqual({'evidence_request'},set(kinds[3:]))
    def test_evidence_request_never_inherits_fix_text(self):
        self.a['evidence']=[self.evidence('code')]
        c=self.gap('CHG-001','design','failed','high');c['verification_test']='Fix test';c['recommendation']='Repair'
        items={i['key']:i for i in summarize(self.a)['items']}
        d,o=items['CHG-001-design'],items['CHG-001-operation']
        self.assertEqual(('gap','Fix test','2026-12-01','Repair'),(d['kind'],d['done_when'],d['due_date'],d['recommendation']))
        self.assertEqual(DEFAULTS['operation']['done_when'],o['done_when']);self.assertEqual(DEFAULTS['operation']['recommendation'],o['recommendation'])
        self.assertEqual(('','Owner','high','evidence_request'),(o['due_date'],o['owner'],o['severity'],o['kind']))
        self.assertNotIn('Fix test',o['done_when']+o['recommendation']);self.assertEqual('Evidence required',o['observation'])
    def test_unreviewed_item_takes_priority_hint(self):
        hints={c['id']:c['priority_hint'] for c in library()['controls']}
        for i in summarize(self.a)['items']:self.assertEqual(hints[i['control_id']],i['severity'])
    def test_period_rows_show_uncovered_dates(self):
        self.a['evidence']=[self.evidence('operational','2026-09-01','2026-10-31')]
        self.gap('CHG-001','operation','partially_verified','high')
        s=summarize(self.a);row=next(r for r in s['period'] if r['control_id']=='CHG-001')
        self.assertEqual([['2026-08-01','2026-08-31']],row['uncovered']);self.assertEqual([['2026-09-01','2026-10-31']],row['covered'])
        self.assertEqual('partially_verified',row['operation_status'])
        item=next(i for i in s['items'] if i['key']=='CHG-001-operation');self.assertEqual([['2026-08-01','2026-08-31']],item['period_gaps'])
        self.assertEqual(['CHG-001'],[r['control_id'] for r in s['period']])
        self.assertEqual([],summarize(create('Synthetic SaaS','production','2026-08-01','2026-10-31','type1-readiness'))['period'])
    def test_item_text_is_redacted(self):
        self.a['evidence']=[self.evidence('code')];self.gap('CHG-001','design')['rationale']='Contact person@example.com'
        i=next(i for i in summarize(self.a)['items'] if i['key']=='CHG-001-design')
        self.assertIn('[REDACTED_EMAIL]',i['observation']);self.assertNotIn('person@example.com',i['observation'])
        self.assertEqual('E1 controlled-records/review.json',i['evidence_refs'])
    def test_no_open_items(self):
        self.type1_all_verified();self.assertEqual([],summarize(self.a)['items'])
        with tempfile.TemporaryDirectory() as root:
            render(self.a,root);rows=self.register(root)
            self.assertEqual([HEADER],rows);self.assertIn('No open items are recorded.',Path(root,'SOC2-READINESS.md').read_text())
    def test_markdown_has_no_score(self):
        self.a['evidence']=[self.evidence('code')];self.gap('CHG-001','design','failed','high');self.gap('IAM-001','design','partially_verified','critical')
        md=self.render_md().lower();self.assertNotIn('%',md)
        for word in ('compliant','certified','score:'):self.assertNotIn(word,md)
    def test_risk_register_one_row_per_item(self):
        self.a['evidence']=[self.evidence('code')];self.gap('CHG-001','design','failed','high')
        with tempfile.TemporaryDirectory() as root:
            render(self.a,root);rows=self.register(root)
        items=summarize(self.a)['items'];self.assertEqual(HEADER,rows[0]);self.assertEqual(len(items),len(rows)-1)
        self.assertEqual([i['key'] for i in items],[r[0] for r in rows[1:]])
        self.assertEqual(['CHG-001-design','CHG-001','design'],rows[1][:3]);self.assertEqual('Confirmed gap',rows[1][6]);self.assertEqual('Evidence request',rows[-1][6])
    def test_not_applicable_operation_has_no_period_row(self):
        c=self.check('AI-001')
        c.update(design_status='not_applicable',operation_status='not_applicable',rationale='Synthetic product has no AI features',
            reviewer='Synthetic Reviewer',approved_by='Synthetic Approver')
        self.assertEqual([],validate(self.a))
        self.assertNotIn('AI-001',[r['control_id'] for r in summarize(self.a)['period']])
    def test_markdown_sections(self):
        md=self.render_md()
        for h in ('## Status by area','## Open items by urgency','## Period coverage'):self.assertIn(h,md)
        self.assertNotIn('Not assessed (Type 1 readiness)',md)
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31','type1-readiness');md=self.render_md()
        for h in ('## Status by area','## Open items by urgency'):self.assertIn(h,md)
        self.assertNotIn('## Period coverage',md);self.assertIn('Not assessed (Type 1 readiness)',md)
    def test_type1_markdown_has_no_operation_conclusions(self):
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31','type1-readiness')
        self.a['evidence']=[self.evidence('operational')];self.gap('CHG-001','operation','failed','high')
        self.assertEqual([],validate(self.a));md=self.render_md()
        for leak in ('Period gaps: [[','Operation: failed','Operation: insufficient_evidence','Population: total='):self.assertNotIn(leak,md)
        self.assertIn('Not assessed (Type 1 readiness)',md)
        self.assertIn('Design: insufficient_evidence; Operation: Not assessed (Type 1 readiness)',md)

if __name__=='__main__':unittest.main()
