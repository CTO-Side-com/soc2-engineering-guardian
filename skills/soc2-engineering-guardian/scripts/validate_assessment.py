"""Validate evidence structure, scope and period support; never its truth."""
import argparse
from common import STATUSES, TYPES, coverage, iso, library, load, today

def present(x):
    return isinstance(x,str) and x.strip().upper() not in ('','TBD','UNKNOWN','N/A','UNASSIGNED')

def validate(data):
    errors=[]
    def need(test, message):
        if not test: errors.append(message)
    if not isinstance(data,dict): return ['Assessment must be an object']
    lib=library()
    for key in ('product','environment','created_on'):
        need(present(data.get(key)), 'Missing '+key)
    for key in ('in_scope_systems','excluded_systems','service_commitments','system_requirements'):
        value=data.get(key)
        need(isinstance(value,list) and all(isinstance(v,str) for v in value),key+': expected string array')
    need(isinstance(data.get('assessor'),str),'assessor must be a string')
    unknowns=data.get('scope_unknowns',[])
    need(isinstance(unknowns,list) and all(isinstance(v,str) for v in unknowns),'scope_unknowns must be a string array')
    need(data.get('schema_version')=='1.0','Unsupported schema version')
    need(data.get('framework_version')==lib['framework_version'],'Framework version mismatch')
    need(data.get('control_library_version')==lib['version'],'Control library version mismatch')
    need(data.get('categories')==['Security'],'Only the Security pack is supported')
    mode=data.get('mode')
    need(mode in ('type1-readiness','type2-readiness'),'Unsupported assessment mode')
    period=data.get('period',{})
    valid_period=False
    try:
        start,end=iso(period['start']),iso(period['end'])
        need(start<=end,'Reversed period');need(end<=iso(today()),'Future period')
        iso(data.get('created_on'));valid_period=start<=end
    except (ValueError,TypeError,KeyError): errors.append('Invalid assessment dates')
    items=data.get('controls');evs=data.get('evidence')
    if not isinstance(items,list) or not isinstance(evs,list):
        return errors+['controls and evidence must be arrays']
    evmap={}
    for ev in evs:
        if not isinstance(ev,dict): errors.append('Evidence must be an object');continue
        eid=ev.get('id')
        if not present(eid): errors.append('Evidence needs id');continue
        need(eid not in evmap,'Duplicate evidence '+eid);evmap[eid]=ev
        for key in ('ref','method','reviewer','environment'):
            need(present(ev.get(key)),eid+': missing '+key)
        need(isinstance(ev.get('type'),str) and ev.get('type') in TYPES,eid+': invalid evidence type')
        need(ev.get('period') is None or isinstance(ev.get('period'),dict),eid+': period must be an object or null')
        try:
            collected=iso(ev.get('collected_on'))
            need(collected<=iso(today()),eid+': future collection date')
            if ev.get('period'):
                a,b=iso(ev['period']['start']),iso(ev['period']['end'])
                need(a<=b,eid+': reversed evidence period')
                need(b<=collected,eid+': collection predates covered period')
        except (ValueError,TypeError,KeyError): errors.append(eid+': invalid evidence dates')
        if ev.get('sha256'):
            import re
            need(bool(re.fullmatch(r'[a-f0-9]{64}',str(ev['sha256']))),eid+': invalid sha256')
    expected={c['id'] for c in lib['controls']};seen=set()
    for c in items:
        if not isinstance(c,dict): errors.append('Control must be an object');continue
        cid=c.get('id')
        if not isinstance(cid,str): errors.append('Invalid control id');continue
        need(cid in expected,'Unknown control '+cid);need(cid not in seen,'Duplicate control '+cid);seen.add(cid)
        structural=True
        for key in ('rationale','reviewer','approved_by','owner','severity','recommendation','verification_test','due_date'):
            if not isinstance(c.get(key),str):
                errors.append(cid+': '+key+' must be a string');structural=False
        pop=c.get('population')
        if not isinstance(pop,dict):
            errors.append(cid+': population must be an object');structural=False
        else:
            for key in ('source','selection_method','completeness_method','reviewer'):
                if not isinstance(pop.get(key),str):
                    errors.append(cid+': population.'+key+' must be a string');structural=False
            for key in ('total','reviewed','exceptions'):
                n=pop.get(key)
                need(n is None or (type(n) is int and n>=0),cid+': invalid population.'+key)
            if all(type(pop.get(k)) is int for k in ('total','reviewed','exceptions')):
                need(0<=pop['exceptions']<=pop['reviewed']<=pop['total'],cid+': inconsistent population counts')
        if not structural:continue
        if c.get('due_date'):
            try: iso(c['due_date'])
            except (ValueError,TypeError):errors.append(cid+': invalid due_date')
        need(c.get('severity','') in ('','critical','high','medium','low'),cid+': invalid severity')
        watch=c.get('watched_paths',[])
        need(isinstance(watch,list) and all(isinstance(w,str) and bool(w.strip()) for w in watch),cid+': watched_paths must be nonempty string patterns')
        for dimension in ('design','operation'):
            status=c.get(dimension+'_status');refs=c.get(dimension+'_evidence')
            if not isinstance(status,str) or status not in STATUSES:
                errors.append(cid+': invalid '+dimension+' status');continue
            if not isinstance(refs,list) or any(not isinstance(r,str) for r in refs):
                errors.append(cid+': invalid evidence references');continue
            need(len(refs)==len(set(refs)),cid+': duplicate evidence reference')
            for ref in refs:
                need(ref in evmap,cid+': unknown evidence '+ref)
                if ref in evmap:
                    need(evmap[ref].get('environment')==data.get('environment'),cid+': evidence environment mismatch')
            if status!='insufficient_evidence':
                need(present(c.get('rationale')),cid+': rationale required')
                need(present(c.get('reviewer')),cid+': reviewer required')
            if status in ('verified','partially_verified','failed'):
                need(bool(refs),cid+': evidence required for '+dimension)
            if status=='not_applicable':
                need(present(c.get('approved_by')),cid+': applicability approval required')
            if status in ('failed','partially_verified'):
                for key in ('owner','severity','recommendation','verification_test'):
                    need(present(c.get(key)),cid+': gap needs '+key)
            if dimension=='operation' and status=='verified':
                need(c.get('design_status')=='verified',cid+': verified operation requires verified design')
                need(mode=='type2-readiness',cid+': type1 mode cannot assert period operation')
                intervals=[]
                for ref in refs:
                    ev=evmap.get(ref,{})
                    if ev.get('type') in ('operational','test','external_report') and ev.get('period'):
                        try:
                            a,b=ev['period']['start'],ev['period']['end']
                            if iso(a)<=iso(b):intervals.append((a,b))
                        except (KeyError,TypeError,ValueError):pass
                if valid_period:
                    need(not coverage(intervals,period['start'],period['end']),cid+': operating period has uncovered dates')
                pop=c.get('population')
                if not isinstance(pop,dict): errors.append(cid+': population required');continue
                for key in ('source','selection_method','completeness_method','reviewer'):
                    need(present(pop.get(key)),cid+': population needs '+key)
                nums=[pop.get(k) for k in ('total','reviewed','exceptions')]
                good=all(type(n) is int and n>=0 for n in nums)
                need(good,cid+': population counts must be nonnegative integers')
                if good:
                    total,reviewed,exceptions=nums
                    need(total>=reviewed>0,cid+': review at least one item; zero populations require judgment')
                    need(exceptions==0,cid+': exceptions prevent fully verified operation')
                need(present(c.get('verification_test')),cid+': operation needs verification method')
    need(seen==expected,'Missing controls: '+', '.join(sorted(expected-seen)))
    return errors

def require_valid(data):
    errors=validate(data)
    if errors: raise ValueError('\n'.join(errors))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment',required=True);a=p.parse_args()
    try:
        require_valid(load(a.assessment))
        print('Valid structure and minimum support. Evidence truth and audit sufficiency remain subject to review.')
    except (ValueError,OSError) as e:p.exit(1,str(e)+'\n')
