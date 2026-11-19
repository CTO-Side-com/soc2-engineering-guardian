"""Offline behavioral tests; all examples are synthetic."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import coverage,csv_safe,library,target,write
from init_assessment import create
from validate_assessment import validate,require_valid
from repo_scan import scan
from render_report import render
from export_tasks import export
from recheck import recheck
from github_evidence import normalize

class GuardianTests(unittest.TestCase):
    def setUp(self):
        self.a=create('Synthetic SaaS','production','2026-08-01','2026-10-31')
    def evidence(self,kind='operational',start='2026-08-01',end='2026-10-31'):
        return {'id':'E1','type':kind,'ref':'controlled-records/review.json','method':'Reviewed synthetic records',
            'reviewer':'Synthetic Reviewer','environment':'production','collected_on':'2026-11-01',
            'period':{'start':start,'end':end}}
    def operating(self):
        self.a['evidence']=[self.evidence()];c=self.a['controls'][0]
        c.update(design_status='verified',operation_status='verified',design_evidence=['E1'],operation_evidence=['E1'],
            rationale='Synthetic supporting records reviewed for stated scope',reviewer='Synthetic Reviewer',verification_test='Reconcile and test every synthetic entry')
        c['population']={'source':'synthetic population','total':12,'reviewed':12,'exceptions':0,
            'selection_method':'all entries','completeness_method':'reconciled source count','reviewer':'Synthetic Reviewer'}
        return c
    def assertBad(self):self.assertTrue(validate(self.a))
    def test_initial_assessment_has_no_verified_controls(self):
        self.assertEqual([],validate(self.a));self.assertTrue(all(c['design_status']=='insufficient_evidence' for c in self.a['controls']))
    def test_control_library_size_and_unique_ids(self):
        cs=library()['controls'];self.assertEqual(53,len(cs));self.assertEqual(len(cs),len({c['id'] for c in cs}))
    def test_original_checks_cover_all_common_criteria_families(self):
        families={x.split('.')[0] for c in library()['controls'] for x in c['criteria']}
        self.assertEqual({'CC'+str(n) for n in range(1,10)},families)
    def test_init_rejects_future_period(self):
        with self.assertRaises(ValueError):create('x','production','2099-01-01','2099-02-01')
    def test_init_rejects_reverse_period(self):
        with self.assertRaises(ValueError):create('x','production','2026-10-31','2026-08-01')
    def test_full_period_with_population(self):self.operating();self.assertEqual([],validate(self.a))
    def test_operation_requires_verified_design(self):self.operating()['design_status']='insufficient_evidence';self.assertBad()
    def test_malformed_status_returns_validation_error(self):self.a['controls'][0]['design_status']=[];self.assertBad()
    def test_malformed_evidence_type_returns_validation_error(self):self.a['evidence']=[self.evidence([])];self.assertBad()
    def test_watched_paths_must_be_string_array(self):self.a['controls'][0]['watched_paths']='backend/*';self.assertBad()
    def test_null_population_is_rejected_before_render(self):self.a['controls'][0]['population']=None;self.assertBad()
    def test_missing_severity_is_rejected_before_export(self):self.a['controls'][0].pop('severity');self.assertBad()
    def test_null_watched_path_is_rejected(self):self.a['controls'][0]['watched_paths']=[None];self.assertBad()
    def test_nonstring_rationale_is_rejected(self):self.a['controls'][0]['rationale']=[];self.assertBad()
    def test_invalid_system_list_is_rejected(self):self.a['in_scope_systems']='production';self.assertBad()
    def test_inconsistent_partial_population_is_rejected(self):
        c=self.operating();c['operation_status']='insufficient_evidence';c['population']['exceptions']=99;self.assertBad()
    def test_snapshot_does_not_prove_operation(self):self.operating();self.a['evidence'][0]['type']='configuration';self.assertBad()
    def test_code_does_not_prove_operation(self):self.operating();self.a['evidence'][0]['type']='code';self.assertBad()
    def test_period_gap_blocks_verified(self):self.operating();self.a['evidence'][0]['period']['start']='2026-08-02';self.assertBad()
    def test_missing_reviewer(self):self.operating();self.a['controls'][0]['reviewer']='';self.assertBad()
    def test_missing_evidence_reviewer(self):self.operating();self.a['evidence'][0]['reviewer']='';self.assertBad()
    def test_mismatched_environment(self):self.operating();self.a['evidence'][0]['environment']='staging';self.assertBad()
    def test_exception_blocks_verified(self):self.operating()['population']['exceptions']=1;self.assertBad()
    def test_zero_population_needs_judgment(self):
        c=self.operating();c['population']['total']=c['population']['reviewed']=0;self.assertBad()
    def test_missing_population_reconciliation(self):self.operating()['population']['completeness_method']='';self.assertBad()
    def test_reviewed_exceeds_population(self):self.operating()['population']['reviewed']=13;self.assertBad()
    def test_boolean_is_not_population_count(self):self.operating()['population']['total']=True;self.assertBad()
    def test_type1_cannot_assert_period_operation(self):self.operating();self.a['mode']='type1-readiness';self.assertBad()
    def test_unknown_reference(self):self.operating()['operation_evidence']=['unknown'];self.assertBad()
    def test_duplicate_reference(self):self.operating()['operation_evidence']=['E1','E1'];self.assertBad()
    def test_duplicate_evidence(self):self.operating();self.a['evidence'].append(self.a['evidence'][0]);self.assertBad()
    def test_duplicate_control(self):self.a['controls'].append(copy.deepcopy(self.a['controls'][0]));self.assertBad()
    def test_missing_control(self):self.a['controls'].pop();self.assertBad()
    def test_unsupported_category(self):self.a['categories'].append('Availability');self.assertBad()
    def test_draft_framework_rejected(self):self.a['framework_version']='2027-draft';self.assertBad()
    def test_unapproved_inapplicability(self):
        c=self.a['controls'][0];c.update(design_status='not_applicable',reviewer='Reviewer',rationale='Provider responsibility');self.assertBad()
    def test_partial_gap_needs_owner_and_fix(self):
        c=self.operating();c.update(operation_status='partially_verified',owner='',recommendation='');self.assertBad()
    def test_collection_before_period_end(self):self.operating();self.a['evidence'][0]['collected_on']='2026-09-01';self.assertBad()
    def test_invalid_hash(self):self.operating();self.a['evidence'][0]['sha256']='not-a-hash';self.assertBad()
    def test_bad_due_date(self):self.a['controls'][0]['due_date']='tomorrow';self.assertBad()
    def test_bad_evidence_type(self):self.a['evidence']=[self.evidence('screenshot')];self.assertBad()
    def test_coverage_merges_adjacent_and_overlap(self):
        self.assertEqual([],coverage([('2026-08-01','2026-09-01'),('2026-08-10','2026-10-31')],'2026-08-01','2026-10-31'))
    def test_coverage_finds_one_day_gap(self):
        self.assertEqual([['2026-09-01','2026-09-01']],coverage([('2026-08-01','2026-08-31'),('2026-09-02','2026-10-31')],'2026-08-01','2026-10-31'))
    def test_coverage_clips_outside_period(self):
        self.assertEqual([],coverage([('2026-01-01','2026-12-31')],'2026-08-01','2026-10-31'))
    def test_recheck_preserves_baseline(self):
        self.operating();new=recheck(self.a,['app/api.py']);self.assertEqual('verified',self.a['controls'][0]['operation_status']);self.assertEqual('insufficient_evidence',new['controls'][0]['operation_status']);self.assertEqual(['E1'],new['controls'][0]['stale_evidence'])
    def test_recheck_respects_reviewed_watch_paths(self):
        c=self.operating();c['watched_paths']=['backend/*'];self.assertEqual('verified',recheck(self.a,['frontend/a.ts'])['controls'][0]['operation_status'])
    def test_empty_recheck_has_no_invalidations(self):self.assertEqual([],recheck(self.a,[])['recheck']['controls_invalidated'])
    def test_recheck_rejects_traversal(self):
        with self.assertRaises(ValueError):recheck(self.a,['../secret'])
    def test_scanner_emits_metadata_only(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root,'app.py').write_text('client.get(url, verify=False)\n')
            data=scan(root);self.assertEqual(1,len(data['findings']));self.assertNotIn('verify=False',json.dumps(data));self.assertEqual('unconfirmed_lead',data['findings'][0]['status'])
    def test_scanner_skips_sensitive_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root,'.env').write_text('verify=False');Path(root,'records').mkdir();Path(root,'records','x.py').write_text('verify=False')
            Path(root,'link.py').symlink_to(Path(root,'.env'));self.assertEqual([],scan(root)['findings'])
    def test_scanner_does_not_flag_secure_tls(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root,'app.py').write_text('client.get(url, verify=True)');self.assertEqual([],scan(root)['findings'])
    def test_scanner_truncation_visible(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root,'app.py').write_text('verify=False\nverify=False');self.assertTrue(scan(root,max_findings=1)['truncated_findings'])
    def test_export_guards_formula_injection(self):
        self.assertTrue(csv_safe('  =HYPERLINK("x")').startswith("'"))
    def test_end_to_end_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            names=render(self.a,root,True);self.assertEqual(106,export(self.a,root));self.assertTrue(Path(root,'SOC2-READINESS.pdf').read_bytes().startswith(b'%PDF'))
            m=json.loads(Path(root,'handoff-manifest.json').read_text());self.assertEqual(len(names),len(m['files']));self.assertFalse(m['raw_evidence_included'])
    def test_invalid_assessment_refuses_reports_and_tasks(self):
        self.a['controls'].pop()
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):render(self.a,root)
            with self.assertRaises(ValueError):export(self.a,root)
            self.assertEqual([],list(Path(root).iterdir()))
    def test_export_redacts_and_neutralizes_slack_mentions(self):
        self.a['product']='person@example.com';self.a['controls'][0]['recommendation']='Contact person@example.com @channel <https://bad.test>'
        with tempfile.TemporaryDirectory() as root:
            render(self.a,root);export(self.a,root)
            self.assertNotIn('person@example.com',Path(root,'SOC2-READINESS.md').read_text());self.assertNotIn('@channel',Path(root,'tasks-slack.txt').read_text());self.assertNotIn('<https',Path(root,'tasks-slack.txt').read_text())
    def test_output_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root,'file');p.write_text('keep');Path(root,'link').symlink_to(p)
            with self.assertRaises(ValueError):write(Path(root,'link'),{})
            self.assertEqual('keep',p.read_text())
    def test_report_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root,'keep.txt');p.write_text('keep');Path(root,'SOC2-READINESS.md').symlink_to(p)
            with self.assertRaises(ValueError):render(self.a,root)
            self.assertEqual('keep',p.read_text())
    def test_null_optional_period_is_supported_for_design(self):
        self.a['evidence']=[self.evidence('code')];self.a['evidence'][0]['period']=None
        self.assertEqual([],validate(self.a))
        with tempfile.TemporaryDirectory() as root:render(self.a,root)
    def test_malformed_optional_period_is_rejected(self):
        self.a['evidence']=[self.evidence('code')];self.a['evidence'][0]['period']=[];self.assertBad()
    def test_report_preserves_scope_context(self):
        self.a['service_commitments']=['Synthetic commitment'];self.a['system_requirements']=['Synthetic requirement'];self.a['scope_unknowns']=['Synthetic unknown'];self.a['assessor']='Synthetic assessor'
        with tempfile.TemporaryDirectory() as root:
            render(self.a,root);s=Path(root,'SOC2-READINESS.md').read_text()
            for term in ('Synthetic commitment','Synthetic requirement','Synthetic unknown','Synthetic assessor'):self.assertIn(term,s)
    def test_tasks_separate_fix_and_period_evidence(self):
        c=self.operating();c.update(design_status='failed',operation_status='insufficient_evidence',severity='high',owner='Owner',recommendation='Repair design',verification_test='Retest design')
        with tempfile.TemporaryDirectory() as root:
            export(self.a,root);s=Path(root,'tasks.md').read_text();self.assertIn('Fix: [Design]',s);self.assertIn('Collect evidence: [Operation]',s);self.assertIn('complete source population',s)
    def test_github_normalization_excludes_bodies_and_titles(self):
        raw={'pulls':[[{'number':1,'title':'private title','body':'private body','merged_at':'2026-09-01T12:00:00Z','head':{'sha':'a'},'base':{'ref':'main'},'user':{'login':'someone','email':'private@example.com'}}]],'reviews':{'1':[]},'deployments':[]}
        d=normalize(raw,'example/repository','2026-08-01','2026-10-31');s=json.dumps(d)
        for token in ('private title','private body','private@example.com','someone'):self.assertNotIn(token,s)
        self.assertEqual('unreviewed_metadata',d['status']);self.assertTrue(d['pulls'][0]['review_collection_present'])
    def test_github_missing_reviews_differ_from_empty(self):
        raw={'pulls':[{'number':1,'merged_at':'2026-09-01T00:00:00Z'}]};d=normalize(raw,'example/repo','2026-08-01','2026-10-31');self.assertFalse(d['pulls'][0]['review_collection_present'])
    def test_github_rejects_arbitrary_endpoint(self):
        with self.assertRaises(ValueError):normalize({},'https://bad.test','2026-08-01','2026-10-31')
    def test_github_rejects_nonobject_export(self):
        with self.assertRaises(ValueError):normalize([],'example/repo','2026-08-01','2026-10-31')

if __name__=='__main__':unittest.main()
