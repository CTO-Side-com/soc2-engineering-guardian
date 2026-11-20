"""Tests for the import-ready Jira, Notion, Slack and Markdown task exports."""
import csv
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from init_assessment import create
from validate_assessment import validate
from render_report import ORDER,summarize
from export_tasks import FORMATS,export

JIRA=['Summary','Issue Type','Priority','Labels','Labels','Labels','Labels','Due Date','Description']
NOTION=['Task','Status','Priority','Finding','Dimension','Control','Area','Criteria','Owner','Due','Recommendation','Done when','Evidence to collect','Item ID']
SLACK_LIST=['Task','Priority','Status','Owner','Due date','Control','Notes']
FILES={'jira':['tasks-jira.csv'],'notion':['tasks-notion.csv'],'slack':['tasks-slack-list.csv','tasks-slack.txt'],'markdown':['tasks.md']}
CSVS=('tasks-jira.csv','tasks-notion.csv','tasks-slack-list.csv')
NOTICE='Internal readiness item, not an audit finding or opinion.'

class ExportTests(unittest.TestCase):
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
    def run_export(self,**kw):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.out=Path(self.tmp.name)
        self.count=export(self.a,self.out,**kw);return self.out
    def rows(self,name):
        with Path(self.out,name).open(newline='',encoding='utf-8') as f:return list(csv.reader(f))
    def text(self,name):
        return Path(self.out,name).read_text(encoding='utf-8')
    def mixed(self):
        self.a['evidence']=[self.evidence('code'),self.evidence('operational','2026-09-01','2026-10-31','E2')]
        self.gap('IAM-001','design','failed','critical');self.gap('CHG-001','design','partially_verified','high')
        self.gap('GOV-001','design','failed','medium');self.gap('AI-001','design','failed','low')
        self.gap('CHG-002','operation','partially_verified','high',('E2',))

    def test_one_task_per_item_in_summary_order(self):
        self.mixed();self.run_export();items=summarize(self.a)['items']
        self.assertEqual(106,len(items));self.assertEqual(len(items),self.count)
        rows=self.rows('tasks-jira.csv');self.assertEqual([i['key'] for i in items],[r[0].split(' ',1)[0] for r in rows[1:]])
        self.assertEqual([i['summary'] for i in items],[r[0].split(' ',1)[1] for r in rows[1:]])
        self.assertEqual([i['key'] for i in items],[r[-1] for r in self.rows('tasks-notion.csv')[1:]])
    def test_gaps_only_drops_evidence_requests(self):
        self.mixed();self.run_export(gaps_only=True);gaps=[i['key'] for i in summarize(self.a)['items'] if i['kind']=='gap']
        self.assertEqual(5,len(gaps));self.assertEqual(5,self.count)
        self.assertEqual(gaps,[r[0].split(' ',1)[0] for r in self.rows('tasks-jira.csv')[1:]])
        self.assertEqual(5,len(re.findall(r'^- \[ \] ',self.text('tasks.md'),re.M)))
        self.assertNotIn('Collect evidence',self.text('tasks-slack.txt'))
    def test_jira_columns_and_priorities(self):
        self.mixed();self.run_export();rows=self.rows('tasks-jira.csv');self.assertEqual(JIRA,rows[0])
        self.assertEqual({'Task'},{r[1] for r in rows[1:]});self.assertLessEqual({r[2] for r in rows[1:]},{'Highest','High','Medium','Low'})
        by={r[0].split(' ',1)[0]:r for r in rows[1:]}
        for key,pri in (('IAM-001-design','Highest'),('CHG-001-design','High'),('GOV-001-design','Medium'),('AI-001-design','Low')):self.assertEqual(pri,by[key][2],key)
        self.assertEqual(['soc2','soc2-ai-engineering','confirmed-gap','ai-001'],by['AI-001-design'][3:7])
        self.assertEqual(['soc2','soc2-access','confirmed-gap','iam-001'],by['IAM-001-design'][3:7])
        self.assertEqual('2026-12-01',by['AI-001-design'][7])
        req=by['GOV-002-design'];self.assertEqual(['soc2','soc2-governance','evidence-request','gov-002'],req[3:7]);self.assertEqual('',req[7])
    def test_jira_description_lines_in_order(self):
        self.mixed();self.run_export();by={r[0].split(' ',1)[0]:r[8].split('\n') for r in self.rows('tasks-jira.csv')[1:]}
        g=by['IAM-001-design']
        self.assertEqual('SOC 2 Guardian IAM-001-design: Failed, critical urgency',g[0]);self.assertTrue(g[1].startswith('Control: IAM-001 (Design), criteria '))
        self.assertTrue(g[1].endswith(' (interpretive mapping)'));self.assertEqual(['Observation: Synthetic finding for IAM-001','Recommendation: Repair IAM-001','Done when: Retest IAM-001','Owner: Owner',NOTICE],g[2:])
        op=by['CHG-002-operation'];self.assertTrue(op[0].startswith('SOC 2 Guardian CHG-002-operation: Partially verified, high urgency'))
        heads=[l.split(':')[0] for l in op];self.assertEqual(['SOC 2 Guardian CHG-002-operation','Control','Observation','Recommendation','Period gaps','Done when','Owner'],heads[:-1]);self.assertEqual(NOTICE,op[-1])
        self.assertIn('2026-08-01',op[heads.index('Period gaps')])
        r=by['GOV-002-design'];self.assertIn(': Evidence missing, ',r[0]);rh=[l.split(':')[0] for l in r]
        self.assertEqual(['Control','Observation','Recommendation','Evidence to collect','Done when'],rh[1:6]);self.assertNotIn('Owner',rh);self.assertEqual(NOTICE,r[-1])
    def test_notion_and_slack_list_headers(self):
        self.mixed();self.run_export();self.assertEqual(NOTION,self.rows('tasks-notion.csv')[0]);self.assertEqual(SLACK_LIST,self.rows('tasks-slack-list.csv')[0])
        n=self.rows('tasks-notion.csv')[1];self.assertEqual(['Not started'],[n[1]]);self.assertEqual(len(NOTION),len(n))
        s=self.rows('tasks-slack-list.csv')[1];self.assertEqual('Not started',s[2]);self.assertEqual(len(SLACK_LIST),len(s))
        self.assertEqual(['Fix: [Design] ','Critical','Failed','Design','IAM-001','Access'],[n[0][:14]]+[n[2],n[3],n[4],n[5],n[6]])
    def test_no_csv_cell_can_be_a_formula(self):
        self.mixed();c=self.gap('IAM-001','design','failed','critical');c['recommendation']='=HYPERLINK("http://x.test","go")';c['owner']='@ops';c['verification_test']='\t=cmd'
        self.gap('CHG-001','design')['recommendation']='  +SUM(A1)';self.gap('GOV-001','design')['owner']='-2+3'
        self.assertEqual([],validate(self.a));self.run_export()
        for name in CSVS:
            for row in self.rows(name):
                for cell in row:self.assertFalse(cell.startswith(('=','+','-','@','\t','\r')),(name,cell[:40]))
        self.assertIn("'=HYPERLINK",self.text('tasks-notion.csv'))
    def test_exports_redact_contact_details(self):
        self.a['product']='person@example.com';self.mixed();self.gap('IAM-001','design','failed','critical')['recommendation']='Email person@example.com token=abc123'
        self.run_export()
        for name in sum(FILES.values(),[]):
            t=self.text(name);self.assertNotIn('person@example.com',t,name);self.assertNotIn('abc123',t,name)
        self.assertIn('[REDACTED_EMAIL]',self.text('tasks.md'))
    def test_slack_message_cannot_ping_or_link(self):
        self.mixed();self.gap('IAM-001','design','failed','critical')['recommendation']='<!channel> @here <https://x.test>';self.a['controls'][3]['owner']='@boss'
        self.run_export();t=self.text('tasks-slack.txt')
        for ch in '@<>':self.assertNotIn(ch,t)
        self.assertIn('‹!channel› ＠here ‹https://x.test›',t);self.assertIn('＠boss',t)
    def test_slack_message_shape(self):
        self.mixed();self.run_export();t=self.text('tasks-slack.txt').split('\n')
        self.assertEqual('*SOC 2 Guardian tasks: Synthetic SaaS*',t[0]);self.assertEqual('_106 open items: 5 confirmed gaps, 101 evidence requests. '+NOTICE+'_',t[1])
        self.assertIn('*Critical (',self.text('tasks-slack.txt'));self.assertIn('• *IAM-001-design* Fix: [Design] ',self.text('tasks-slack.txt'))
        self.assertIn('      _Next:_ Repair IAM-001',self.text('tasks-slack.txt'))
    def test_markdown_checklist_grouped_by_urgency(self):
        self.mixed();self.run_export();t=self.text('tasks.md')
        self.assertEqual(106,len(re.findall(r'^- \[ \] ',t,re.M)));heads=re.findall(r'^## (\w+) \((\d+)\)$',t,re.M)
        self.assertEqual(sorted({h[0] for h in heads},key=lambda h:ORDER.index(h.lower())),[h[0] for h in heads]);self.assertEqual(106,sum(int(h[1]) for h in heads))
        self.assertEqual('Critical',heads[0][0]);self.assertIn('- [ ] **IAM-001-design** Fix: [Design] ',t)
        for part in ('  - Recommendation: Repair IAM-001','  - Done when: Retest IAM-001','  - Owner: Owner · Due: 2026-12-01','  - Evidence to collect: '):self.assertIn(part,t)
    def test_type1_blank_exports_53(self):
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31','type1-readiness');self.run_export();self.assertEqual(53,self.count)
        self.assertEqual(53,len(self.rows('tasks-jira.csv'))-1)
        self.assertEqual({'Design'},{r[4] for r in self.rows('tasks-notion.csv')[1:]})
    def test_no_open_items_writes_header_only_csvs(self):
        self.type1_all_verified();self.run_export();self.assertEqual(0,self.count)
        self.assertEqual([JIRA],self.rows('tasks-jira.csv'));self.assertEqual([NOTION],self.rows('tasks-notion.csv'));self.assertEqual([SLACK_LIST],self.rows('tasks-slack-list.csv'))
        self.assertEqual(0,len(re.findall(r'^- \[ \] ',self.text('tasks.md'),re.M)));self.assertIn('0 open items',self.text('tasks-slack.txt'))
    def test_unicode_text_writes_utf8(self):
        self.mixed();self.gap('IAM-001','design','failed','critical')['recommendation']='Rotiere Schlüssel – 日本語 ✓';self.run_export()
        for name in ('tasks-jira.csv','tasks-notion.csv','tasks-slack-list.csv','tasks-slack.txt','tasks.md'):self.assertIn('Rotiere Schlüssel – 日本語 ✓',self.text(name),name)
    def test_invalid_assessment_writes_nothing(self):
        self.a['controls'].pop();self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        with self.assertRaises(ValueError):export(self.a,self.tmp.name)
        self.assertEqual([],list(Path(self.tmp.name).iterdir()))
    def test_unknown_format_writes_nothing_via_api(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        with self.assertRaises(ValueError):export(self.a,self.tmp.name,('jira','trello'))
        self.assertEqual([],list(Path(self.tmp.name).iterdir()))
    def test_defaults_write_every_format(self):
        self.assertEqual(('jira','notion','slack','markdown'),FORMATS);self.run_export()
        self.assertEqual(sorted(sum(FILES.values(),[])),sorted(p.name for p in self.out.iterdir()))
    def cli(self,*args):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name);(root/'in').mkdir();(root/'out').mkdir()
        (root/'in'/'a.json').write_text(json.dumps(self.a))
        r=subprocess.run([sys.executable,str(SCRIPTS/'export_tasks.py'),'--assessment',str(root/'in'/'a.json'),'--out',str(root/'out'),*args],capture_output=True,text=True)
        return r,sorted(p.name for p in (root/'out').iterdir())
    def test_cli_unknown_format_writes_nothing(self):
        r,files=self.cli('--format','jira,trello');self.assertEqual(2,r.returncode);self.assertIn('trello',r.stderr);self.assertEqual([],files)
    def test_format_subset_writes_only_those_files(self):
        r,files=self.cli('--format','jira,markdown');self.assertEqual(0,r.returncode,r.stderr);self.assertEqual(['tasks-jira.csv','tasks.md'],files)
        r,files=self.cli('--format','slack');self.assertEqual(['tasks-slack-list.csv','tasks-slack.txt'],files)
    def test_cli_defaults_to_all_and_gaps_only(self):
        r,files=self.cli();self.assertEqual(0,r.returncode,r.stderr);self.assertEqual(sorted(sum(FILES.values(),[])),files);self.assertIn('106',r.stdout)
        r,files=self.cli('--format','all','--gaps-only');self.assertEqual(0,r.returncode);self.assertIn('Exported 0 tasks',r.stdout)

if __name__=='__main__':unittest.main()
