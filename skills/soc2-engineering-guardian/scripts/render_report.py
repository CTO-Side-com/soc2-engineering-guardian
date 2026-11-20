"""Render validated readiness evidence into Markdown, CSV and optional PDF."""
import argparse
import csv
import json
from collections import Counter
from common import NOTICE, clean, coverage, csv_safe, digest, library, load, target, write
from validate_assessment import require_valid

def gaps_for(c,data):
    ev={e['id']:e for e in data['evidence']};spans=[]
    for ref in c['operation_evidence']:
        e=ev.get(ref,{})
        if e.get('type') in ('operational','test','external_report') and e.get('period'):
            spans.append((e['period']['start'],e['period']['end']))
    return coverage(spans,data['period']['start'],data['period']['end'])

ORDER=['critical','high','medium','low']
# A design evidence request's done-when is the library verification_test, so only the shared texts live here.
DEFAULTS={'design':{'recommendation':'Collect scoped implementation evidence and obtain reviewer judgment.'},
    'operation':{'recommendation':'Collect relevant operating records across the assessment period and reconcile the complete source population.',
        'done_when':'A responsible reviewer evaluates period coverage, population completeness, selection and exceptions; record the supported conclusion.'}}
GAPS=('failed','partially_verified')
RANK={'failed':0,'partially_verified':1,'insufficient_evidence':2}

def summarize(data):
    """One model for the Markdown, PDF and task outputs; every text field is redacted here."""
    lib=library()['controls'];defs={c['id']:c for c in lib};controls={c['id']:c for c in data['controls']}
    ev={e['id']:e for e in data['evidence']};type1=data['mode']=='type1-readiness'
    dims=('design',) if type1 else ('design','operation')
    by_area={}
    for d in lib:by_area.setdefault(d['area'],{'design':Counter(),'operation':Counter()})
    for d in lib:
        for dim in ('design','operation'):by_area[d['area']][dim][controls[d['id']][dim+'_status']]+=1
    items=[]
    for d in lib:
        c=controls[d['id']]
        for dim in dims:
            status=c[dim+'_status']
            if status in ('verified','not_applicable'):continue
            gap=status in GAPS;sev=c['severity'] or d['priority_hint']
            if gap:rec,done=c['recommendation'],c['verification_test']
            else:rec=DEFAULTS[dim]['recommendation'];done=DEFAULTS[dim].get('done_when') or d['verification_test']
            pop=c.get('population') if dim=='operation' else None
            items.append({'key':d['id']+'-'+dim,'control_id':d['id'],'dimension':dim,'area':d['area'],'title':clean(d['title']),
                'criteria':[clean(x) for x in d['criteria']],'status':status,'kind':'gap' if gap else 'evidence_request',
                'summary':('Fix: ' if gap else 'Collect evidence: ')+'['+dim.title()+'] '+clean(d['title']),'severity':sev,
                'observation':clean(c['rationale']) if gap else 'Evidence required','recommendation':clean(rec),'done_when':clean(done),
                'owner':clean(c['owner']),'due_date':clean(c['due_date']) if gap else '',
                'evidence_refs':clean('; '.join(r+' '+ev[r]['ref'] for r in c[dim+'_evidence'] if r in ev)),
                'evidence_to_collect':'' if gap else clean('; '.join(d['evidence_examples'])+' (suggested type: '+d['suggested_evidence_type']+')'),
                'period_gaps':gaps_for(c,data) if dim=='operation' and not type1 else [],
                'population':{k:clean(v) if isinstance(v,str) else v for k,v in pop.items()} if isinstance(pop,dict) else None})
    items.sort(key=lambda i:(RANK[i['status']],ORDER.index(i['severity']),i['control_id'],i['dimension']!='design'))
    period=[]
    if not type1:
        for d in lib:
            c=controls[d['id']]
            if c['operation_status']=='not_applicable' or (not c['operation_evidence'] and c['operation_status']=='insufficient_evidence'):continue
            p=c.get('population') or {}
            period.append({'control_id':d['id'],'title':clean(d['title']),'operation_status':c['operation_status'],
                'covered':[[e['period']['start'],e['period']['end']] for e in (ev.get(r,{}) for r in c['operation_evidence'])
                           if e.get('type') in ('operational','test','external_report') and e.get('period')],
                'uncovered':gaps_for(c,data),'total':p.get('total'),'reviewed':p.get('reviewed'),'exceptions':p.get('exceptions')})
    return {'definitions':defs,'controls':controls,'type1':type1,
        'design_counts':Counter(c['design_status'] for c in data['controls']),'operation_counts':Counter(c['operation_status'] for c in data['controls']),
        'by_area':by_area,'items':items,'period':period}

def lines(data):
    s=summarize(data);defs=s['definitions'];na='Not assessed (Type 1 readiness)'
    out=['# SOC 2 Engineering Guardian',NOTICE,'',
         'Product: '+data['product'],'Environment: '+data['environment'],
         'Period: '+data['period']['start']+' to '+data['period']['end'],
         'Mode: '+data['mode'],'Framework mapping: '+data['framework_version'],'',
         '## Assessment boundary',
         'Assessor: '+(data['assessor'] or 'Unassigned'),
         'Systems: '+', '.join(data.get('in_scope_systems',[])),
         'Exclusions: '+', '.join(data.get('excluded_systems',[])),
         *(['Operation: '+na] if s['type1'] else []),
         'Service commitments: '+(', '.join(data['service_commitments']) or 'Unknown; obtain management input.'),
         'System requirements: '+(', '.join(data['system_requirements']) or 'Unknown; obtain management input.'),
         'Scope unknowns: '+(', '.join(data.get('scope_unknowns',[])) or 'None recorded; this does not prove scope completeness.'),
         'These original checks support Security readiness. They are not the full criteria, an audit program, or a compliance score.',
         'Verified means reviewer-asserted support for the stated scope. Automated validation cannot prove evidence truth.',
         'Recovery checks support risk mitigation; this pack does not assess the Availability category.',
         'PDF text uses built-in Western fonts; use Markdown for full Unicode content.','',
         '## Evidence status counts']
    for dimension in ('design',) if s['type1'] else ('design','operation'):
        counts=Counter(c[dimension+'_status'] for c in data['controls'])
        out.append(dimension.title()+': '+', '.join(k+'='+str(v) for k,v in sorted(counts.items())))
    # Type 1 draws no operating conclusion, whatever operation status the assessment records.
    if s['type1']:out.append('Operation: '+na)
    out.extend(['','## Status by area','Legend: V verified, P partially verified, F failed, NA not applicable, E insufficient evidence.',
        '| Area | Checks | Design V/P/F/NA/E | Operation V/P/F/NA/E |','| --- | --- | --- | --- |'])
    def cells(n):return '/'.join(str(n[k]) for k in ('verified','partially_verified','failed','not_applicable','insufficient_evidence'))
    for area,n in s['by_area'].items():
        out.append('| '+area+' | '+str(sum(n['design'].values()))+' | '+cells(n['design'])+' | '+('not assessed' if s['type1'] else cells(n['operation']))+' |')
    out.extend(['','## Open items by urgency','| Urgency | Confirmed gaps | Evidence requests | Total |','| --- | --- | --- | --- |'])
    for level in ORDER:
        g=sum(1 for i in s['items'] if i['severity']==level and i['kind']=='gap');r=sum(1 for i in s['items'] if i['severity']==level and i['kind']!='gap')
        out.append('| '+level+' | '+str(g)+' | '+str(r)+' | '+str(g+r)+' |')
    if not s['type1']:
        span=lambda v:'; '.join(a+' to '+b for a,b in v) or 'None'
        out.extend(['','## Period coverage','| Check | Operation | Covered | Uncovered | Population total/reviewed/exceptions |','| --- | --- | --- | --- | --- |'])
        for r in s['period']:
            out.append('| '+r['control_id']+' '+r['title']+' | '+r['operation_status']+' | '+span(r['covered'])+' | '+span(r['uncovered'])+' | '+'/'.join('n/a' if r[k] is None else str(r[k]) for k in ('total','reviewed','exceptions'))+' |')
        if not s['period']:out.append('No operation evidence or conclusions are recorded.')
    out.extend(['','## Confirmed gaps and next actions'])
    gaps=[i for i in s['items'] if i['kind']=='gap']
    for i in gaps:out.append(i['key']+' | '+i['severity']+' | '+i['title']+' | Owner: '+(i['owner'] or 'Unassigned')+' | '+i['recommendation'])
    if not gaps:out.append('No confirmed gaps recorded. Missing evidence still prevents a supported conclusion.')
    if not s['items']:out.append('No open items are recorded.')
    out.extend(['','## Control assessment'])
    for c in data['controls']:
        d=defs[c['id']]
        out.extend(['', '### '+c['id']+' | '+d['title'],
            'Supporting criteria: '+', '.join(d['criteria'])+' (interpretive mapping)',
            'Design: '+c['design_status']+'; Operation: '+(na if s['type1'] else c['operation_status']),
            'Rationale: '+(c['rationale'] or 'No reviewer conclusion recorded.'),
            'Evidence: '+(', '.join(c['design_evidence']+c['operation_evidence']) or 'None'),
            'Reviewer: '+(c['reviewer'] or 'Unassigned')+'; Owner: '+(c['owner'] or 'Unassigned'),
            *([] if s['type1'] else ['Period gaps: '+json.dumps(gaps_for(c,data))]),
            'Next action: '+(c['recommendation'] or 'Collect and review scoped evidence.'),
            'Verification: '+(c['verification_test'] or d['verification_test'])])
        p=c.get('population',{})
        if not s['type1']:out.append('Population: total='+str(p.get('total'))+'; reviewed='+str(p.get('reviewed'))+
                   '; exceptions='+str(p.get('exceptions'))+'; method='+str(p.get('selection_method','')))
    out.extend(['','## Evidence index'])
    for e in data['evidence']:
        out.append(e['id']+' | '+e['type']+' | '+e['ref']+' | collected '+e['collected_on']+
                   ' | reviewer '+e['reviewer']+' | method '+e['method'])
    return [clean(line,20000) for line in out]

def render(data,out,pdf=False):
    require_valid(data);out=target(str(out)+'/placeholder').parent
    content=lines(data)
    target(out/'SOC2-READINESS.md').write_text('\n'.join(content)+'\n',encoding='utf-8')
    with target(out/'evidence-index.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['ID','Type','Reference','Environment','Collected','Period start','Period end','Reviewer','SHA256'])
        for e in data['evidence']:
            p=e.get('period') or {};w.writerow([csv_safe(x) for x in [e['id'],e['type'],e['ref'],e['environment'],e['collected_on'],p.get('start',''),p.get('end',''),e['reviewer'],e.get('sha256','')]])
    with target(out/'risk-register.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['Item','Control','Dimension','Title','Criteria','Finding','Kind','Urgency','Owner','Due','Action','Done when','Evidence'])
        for i in summarize(data)['items']:
            w.writerow([csv_safe(x) for x in [i['key'],i['control_id'],i['dimension'],i['title'],', '.join(i['criteria']),i['status'],
                'Confirmed gap' if i['kind']=='gap' else 'Evidence request',i['severity'],i['owner'],i['due_date'],i['recommendation'],i['done_when'],i['evidence_refs']]])
    def scrub(obj):
        if isinstance(obj,dict):return {clean(k,200) if isinstance(k,str) else k:scrub(v) for k,v in obj.items()}
        if isinstance(obj,list):return [scrub(v) for v in obj]
        return clean(obj,20000) if isinstance(obj,str) else obj
    write(out/'assessment-redacted.json',scrub(data))
    if pdf:
        from pdf_report import render_pdf  # lazy: pdf_report imports this module
        target(out/'SOC2-READINESS.pdf').write_bytes(render_pdf(data))
    names=['SOC2-READINESS.md','evidence-index.csv','risk-register.csv','assessment-redacted.json']+(['SOC2-READINESS.pdf'] if pdf else [])
    write(out/'handoff-manifest.json',{'notice':NOTICE,'raw_evidence_included':False,
        'files':[{'path':n,'sha256':digest(out/n)} for n in names]})
    return names

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment',required=True);p.add_argument('--out',required=True);p.add_argument('--pdf',action='store_true');a=p.parse_args()
    try:print('\n'.join(render(load(a.assessment),a.out,a.pdf)))
    except (ValueError,OSError,TypeError,KeyError) as e:p.exit(1,str(e)+'\n')
