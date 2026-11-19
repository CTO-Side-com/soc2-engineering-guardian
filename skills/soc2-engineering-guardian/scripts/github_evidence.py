"""Collect minimal GitHub metadata with explicit network opt-in, or normalize local exports.

Raw responses stay in memory. No comments, bodies, titles, secrets or email addresses
are written. Snapshots are leads, not evidence of historical rule enforcement.
"""
import argparse
import hashlib
import json
import re
import subprocess
from common import iso,load,today,write

def actor(user):
    value=str((user or {}).get('id') or (user or {}).get('login') or '')
    return hashlib.sha256(value.encode()).hexdigest()[:16] if value else 'unknown'

def flatten(value):
    if not isinstance(value,list):raise ValueError('Expected GitHub array or paginated arrays')
    return [item for page in value for item in (page if isinstance(page,list) else [page])]

def normalize(raw,repo,start,end):
    if not isinstance(raw,dict):raise ValueError('Expected an export object')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Invalid owner/repository')
    if iso(start)>iso(end) or iso(end)>iso(today()):raise ValueError('Invalid collection period')
    pulls=[]
    reviews=raw.get('reviews',{})
    if not isinstance(reviews,dict):raise ValueError('Expected reviews keyed by PR number')
    for p in flatten(raw.get('pulls',[])):
        if not isinstance(p,dict):raise ValueError('Invalid pull request record')
        merged=p.get('merged_at')
        if merged is not None and not isinstance(merged,str):raise ValueError('Invalid merge timestamp')
        if not merged or not start<=merged[:10]<=end:continue
        number=p['number'];events=[]
        if type(number) is not int or number<1:raise ValueError('Invalid PR number')
        for r in flatten(reviews.get(str(number),[])):
            events.append({'state':r.get('state'),'commit_id':r.get('commit_id'),
                'submitted_at':r.get('submitted_at'),'actor':actor(r.get('user'))})
        pulls.append({'number':number,'merged_at':merged,'merge_commit_sha':p.get('merge_commit_sha'),
            'head_sha':p.get('head',{}).get('sha'),'base_ref':p.get('base',{}).get('ref'),
            'author':actor(p.get('user')),'review_events':events,'review_collection_present':str(number) in reviews})
    deployments=[{'id':d.get('id'),'sha':d.get('sha'),'environment':d.get('environment'),
        'created_at':d.get('created_at'),'actor':actor(d.get('creator'))}
        for d in flatten(raw.get('deployments',[])) if start<=str(d.get('created_at',''))[:10]<=end]
    return {'schema_version':'1.0','repository':repo,'collected_on':today(),
        'requested_period':{'start':start,'end':end},'status':'unreviewed_metadata',
        'completeness':'unverified; reconcile with all production release mechanisms',
        'pulls':pulls,'deployments':deployments,
        'collection_errors':[{'endpoint':str(e.get('endpoint','unknown')).split('?')[0], 'status':'unavailable'} for e in raw.get('collection_errors',[]) if isinstance(e,dict)],
        'limitations':['A deployment record does not prove a successful production release.',
        'Review events need commit and timing analysis; an approval alone does not establish control operation.',
        'Current rules do not prove historical enforcement; bypass and direct deployments need separate evidence.',
        'Missing records do not establish missing controls. API access or external release paths may explain gaps.',
        'No assessment status is updated by this collector.']}

def collect(repo,start,end):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Invalid owner/repository')
    errors=[]
    def api(suffix):
        # Fixed GET-only endpoints. No shell, token arguments, arbitrary URLs or code execution.
        result=subprocess.run(['gh','api','--method','GET','--paginate','--slurp',
            'repos/'+repo+'/'+suffix],capture_output=True,text=True,timeout=60)
        if result.returncode:
            errors.append({'endpoint':suffix.split('?')[0],'status':'unavailable'})
            return []
        return json.loads(result.stdout)
    raw={'pulls':api('pulls?state=all&per_page=100'),'deployments':api('deployments?per_page=100'),'reviews':{}}
    for p in flatten(raw['pulls']):
        if p.get('merged_at') and start<=p['merged_at'][:10]<=end:
            n=p['number']
            if type(n) is not int or n<1:raise ValueError('Invalid pull request number')
            before=len(errors);value=api('pulls/'+str(n)+'/reviews?per_page=100')
            if len(errors)==before:raw['reviews'][str(n)]=value
    raw['collection_errors']=errors
    return normalize(raw,repo,start,end)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('repo','start','end','out'):p.add_argument('--'+k,required=True)
    p.add_argument('--input',help='Local JSON containing pulls, reviews and deployments exports')
    p.add_argument('--allow-network',action='store_true',help='Explicitly authorize read-only GitHub API collection through installed gh')
    a=p.parse_args()
    try:
        if iso(a.start)>iso(a.end) or iso(a.end)>iso(today()):raise ValueError('Invalid collection period')
        if a.input and a.allow_network:raise ValueError('Choose local input or network collection')
        if not a.input and not a.allow_network:raise ValueError('Provide --input for offline mode, or explicitly opt in with --allow-network')
        data=normalize(load(a.input),a.repo,a.start,a.end) if a.input else collect(a.repo,a.start,a.end)
        write(a.out,data,False);print('Collected unreviewed metadata; no control conclusions were made.')
    except (ValueError,OSError,TypeError,KeyError,subprocess.TimeoutExpired) as e:
        p.exit(1,'Collection failed: '+type(e).__name__+'; check inputs, permissions and gh authentication.\n')
