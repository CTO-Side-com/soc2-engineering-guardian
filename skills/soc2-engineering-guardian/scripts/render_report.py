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

def lines(data):
    defs={c['id']:c for c in library()['controls']}
    out=['# SOC 2 Engineering Guardian',NOTICE,'',
         'Product: '+data['product'],'Environment: '+data['environment'],
         'Period: '+data['period']['start']+' to '+data['period']['end'],
         'Mode: '+data['mode'],'Framework mapping: '+data['framework_version'],'',
         '## Assessment boundary',
         'Assessor: '+(data['assessor'] or 'Unassigned'),
         'Systems: '+', '.join(data.get('in_scope_systems',[])),
         'Exclusions: '+', '.join(data.get('excluded_systems',[])),
         'Service commitments: '+(', '.join(data['service_commitments']) or 'Unknown; obtain management input.'),
         'System requirements: '+(', '.join(data['system_requirements']) or 'Unknown; obtain management input.'),
         'Scope unknowns: '+(', '.join(data.get('scope_unknowns',[])) or 'None recorded; this does not prove scope completeness.'),
         'These original checks support Security readiness. They are not the full criteria, an audit program, or a compliance score.',
         'Verified means reviewer-asserted support for the stated scope. Automated validation cannot prove evidence truth.',
         'Recovery checks support risk mitigation; this pack does not assess the Availability category.',
         'PDF text uses built-in Western fonts; use Markdown for full Unicode content.','',
         '## Evidence status counts']
    for dimension in ('design','operation'):
        counts=Counter(c[dimension+'_status'] for c in data['controls'])
        out.append(dimension.title()+': '+', '.join(k+'='+str(v) for k,v in sorted(counts.items())))
    out.extend(['','## Confirmed gaps and next actions'])
    confirmed=[c for c in data['controls'] if any(c[d+'_status'] in ('failed','partially_verified') for d in ('design','operation'))]
    ranks={'critical':0,'high':1,'medium':2,'low':3,'':4}
    for c in sorted(confirmed,key=lambda c:ranks[c['severity']]):
        out.append(c['id']+' | '+c['severity']+' | '+defs[c['id']]['title']+' | Owner: '+c['owner']+' | '+c['recommendation'])
    if not confirmed:out.append('No confirmed gaps recorded. Missing evidence still prevents a supported conclusion.')
    out.extend(['','## Control assessment'])
    for c in data['controls']:
        d=defs[c['id']]
        out.extend(['', '### '+c['id']+' | '+d['title'],
            'Supporting criteria: '+', '.join(d['criteria'])+' (interpretive mapping)',
            'Design: '+c['design_status']+'; Operation: '+c['operation_status'],
            'Rationale: '+(c['rationale'] or 'No reviewer conclusion recorded.'),
            'Evidence: '+(', '.join(c['design_evidence']+c['operation_evidence']) or 'None'),
            'Reviewer: '+(c['reviewer'] or 'Unassigned')+'; Owner: '+(c['owner'] or 'Unassigned'),
            'Period gaps: '+json.dumps(gaps_for(c,data)),
            'Next action: '+(c['recommendation'] or 'Collect and review scoped evidence.'),
            'Verification: '+(c['verification_test'] or d['verification_test'])])
        p=c.get('population',{})
        out.append('Population: total='+str(p.get('total'))+'; reviewed='+str(p.get('reviewed'))+
                   '; exceptions='+str(p.get('exceptions'))+'; method='+str(p.get('selection_method','')))
    out.extend(['','## Evidence index'])
    for e in data['evidence']:
        out.append(e['id']+' | '+e['type']+' | '+e['ref']+' | collected '+e['collected_on']+
                   ' | reviewer '+e['reviewer']+' | method '+e['method'])
    return [clean(line,20000) for line in out]

def pdf_report(data,content,path):
    from pdf_writer import PDF,wrap
    pdf=PDF(title='SOC 2 Engineering Readiness',author='CTOside',subject=NOTICE)
    y=0
    def page():
        nonlocal y
        pdf.add_page();pdf.rect(0,0,612,45,fill='#101827')
        pdf.text(36,29,'CTOside / SOC 2 Engineering Guardian',12,True,color='#FFFFFF')
        pdf.line(36,750,576,750,color='#39B9D0')
        pdf.text(36,767,'Internal readiness only. Not an auditor opinion.',8,color='#526174')
        pdf.text(540,767,str(len(pdf.pages)),8,color='#526174');y=72
    page()
    for text in content:
        heading=text.startswith('#');size=15 if text.startswith('# ') else 11 if heading else 9
        value=text.lstrip('# ').strip() if heading else text
        if not value:y+=6;continue
        for part in wrap(value,size,540,bold=heading):
            if y+size+6>732:page()
            pdf.text(36,y,part,size,heading,color='#AF2867' if heading else '#182437');y+=size+5
        y+=4 if heading else 1
    target(path).write_bytes(pdf.output())

def render(data,out,pdf=False):
    require_valid(data);out=target(str(out)+'/placeholder').parent
    content=lines(data)
    target(out/'SOC2-READINESS.md').write_text('\n'.join(content)+'\n',encoding='utf-8')
    with target(out/'evidence-index.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['ID','Type','Reference','Environment','Collected','Period start','Period end','Reviewer','SHA256'])
        for e in data['evidence']:
            p=e.get('period') or {};w.writerow([csv_safe(x) for x in [e['id'],e['type'],e['ref'],e['environment'],e['collected_on'],p.get('start',''),p.get('end',''),e['reviewer'],e.get('sha256','')]])
    with target(out/'risk-register.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['ID','Title','Design','Operation','Severity','Owner','Due','Action','Verification'])
        defs={c['id']:c for c in library()['controls']}
        for c in data['controls']:
            if any(c[d+'_status'] not in ('verified','not_applicable') for d in ('design','operation')):
                w.writerow([csv_safe(x) for x in [c['id'],defs[c['id']]['title'],c['design_status'],c['operation_status'],c['severity'],c['owner'],c['due_date'],c['recommendation'] or 'Collect evidence',c['verification_test'] or defs[c['id']]['verification_test']]])
    def scrub(obj):
        if isinstance(obj,dict):return {k:scrub(v) for k,v in obj.items()}
        if isinstance(obj,list):return [scrub(v) for v in obj]
        return clean(obj,20000) if isinstance(obj,str) else obj
    write(out/'assessment-redacted.json',scrub(data))
    if pdf:pdf_report(data,content,out/'SOC2-READINESS.pdf')
    names=['SOC2-READINESS.md','evidence-index.csv','risk-register.csv','assessment-redacted.json']+(['SOC2-READINESS.pdf'] if pdf else [])
    write(out/'handoff-manifest.json',{'notice':NOTICE,'raw_evidence_included':False,
        'files':[{'path':n,'sha256':digest(out/n)} for n in names]})
    return names

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment',required=True);p.add_argument('--out',required=True);p.add_argument('--pdf',action='store_true');a=p.parse_args()
    try:print('\n'.join(render(load(a.assessment),a.out,a.pdf)))
    except (ValueError,OSError,TypeError,KeyError) as e:p.exit(1,str(e)+'\n')
