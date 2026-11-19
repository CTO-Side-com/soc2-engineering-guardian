"""Invalidate changed control assertions in a new assessment; preserve the baseline."""
import argparse
import copy
from pathlib import PurePosixPath,Path
from common import load,today,write
from validate_assessment import require_valid

def recheck(data,paths):
    require_valid(data);result=copy.deepcopy(data);changed=[]
    for value in paths:
        p=PurePosixPath(value)
        if p.is_absolute() or '..' in p.parts:raise ValueError('Use repository-relative changed paths')
    for c in result['controls']:
        watch=c.get('watched_paths',[])
        affected=bool(paths) and (not watch or any(PurePosixPath(p).match(w) or p==w for p in paths for w in watch))
        if affected:
            c['design_status']=c['operation_status']='insufficient_evidence'
            c['rationale']='Revalidation required after repository changes; prior evidence is retained only as historical context.'
            c['stale_evidence']=list(dict.fromkeys(c['design_evidence']+c['operation_evidence']))
            c['design_evidence']=[];c['operation_evidence']=[];changed.append(c['id'])
    result['recheck']={'performed_on':today(),'changed_files':paths,'controls_invalidated':changed,
        'notice':'No watched_paths means conservative invalidation for any change. Configuration-only and operational drift need separate reviews.'}
    require_valid(result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment',required=True);p.add_argument('--changed-files',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    try:
        if Path(a.out).resolve()==Path(a.assessment).resolve():raise ValueError('Write recheck to a new path')
        write(a.out,recheck(load(a.assessment),[x.strip() for x in Path(a.changed_files).read_text().splitlines() if x.strip()]),False)
    except (ValueError,OSError) as e:p.exit(1,str(e)+'\n')
