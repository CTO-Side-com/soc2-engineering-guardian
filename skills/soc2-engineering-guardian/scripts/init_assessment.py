"""Initialize a scoped assessment with no pre-verified controls."""
import argparse
from common import NOTICE, iso, library, today, write

def create(product, environment, start, end, mode='type2-readiness'):
    if not product.strip() or not environment.strip():
        raise ValueError('Product and environment are required')
    if iso(start) > iso(end) or iso(end) > iso(today()):
        raise ValueError('Use an ordered, non-future assessment period')
    lib = library()
    return {'schema_version':'1.0', 'product':product, 'environment':environment,
        'created_on':today(), 'mode':mode, 'period':{'start':start,'end':end},
        'framework_version':lib['framework_version'], 'control_library_version':lib['version'],
        'categories':['Security'], 'in_scope_systems':[], 'excluded_systems':[],
        'service_commitments':[], 'system_requirements':[], 'scope_unknowns':[], 'assessor':'',
        'notice':NOTICE, 'evidence':[], 'controls':[
        {'id':c['id'], 'design_status':'insufficient_evidence', 'operation_status':'insufficient_evidence',
         'design_evidence':[], 'operation_evidence':[], 'rationale':'', 'reviewer':'',
         'approved_by':'', 'owner':'', 'severity':'', 'recommendation':'',
         'verification_test':'', 'due_date':'', 'watched_paths':[],
         'population':{'source':'','total':None,'reviewed':None,'exceptions':None,
                       'selection_method':'','completeness_method':'','reviewer':''}}
        for c in lib['controls']]}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('product','environment','start','end','out'):
        p.add_argument('--'+key, required=True)
    p.add_argument('--mode', choices=['type1-readiness','type2-readiness'], default='type2-readiness')
    a=p.parse_args()
    try:
        write(a.out,create(a.product,a.environment,a.start,a.end,a.mode),overwrite=False)
    except (ValueError,OSError) as e:
        p.exit(1,str(e)+'\n')
