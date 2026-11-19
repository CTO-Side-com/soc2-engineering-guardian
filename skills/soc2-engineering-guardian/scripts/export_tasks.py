"""Export unresolved controls as tracker import files, without contacting trackers."""
import argparse
import csv
from common import clean,csv_safe,library,load,target
from validate_assessment import require_valid

def export(data,out):
    require_valid(data);defs={c['id']:c for c in library()['controls']};rows=[]
    for c in data['controls']:
        open_dims=[d for d in ('design','operation') if c[d+'_status'] not in ('verified','not_applicable')]
        if not open_dims:continue
        for dimension in open_dims:
            gap=c[dimension+'_status'] in ('failed','partially_verified')
            summary=('Fix: ' if gap else 'Collect evidence: ')+'['+dimension.title()+'] '+defs[c['id']]['title']
            if gap:
                action=c['recommendation'];done=c['verification_test']
            elif dimension=='operation':
                action='Collect relevant operating records across the assessment period and reconcile the complete source population.'
                done='A responsible reviewer evaluates period coverage, population completeness, selection and exceptions; record the supported conclusion.'
            else:
                action='Collect scoped implementation evidence and obtain reviewer judgment.'
                done=defs[c['id']]['verification_test']
            body='Control '+c['id']+'; dimension '+dimension+'. '+action+' Done when: '+done
            rows.append([summary,body,{'critical':'Highest','high':'High','medium':'Medium','low':'Low','':'Medium'}[c['severity']],c['owner'],c['due_date'],c['id']+'-'+dimension])
    for name,headers in [('tasks-jira.csv',['Summary','Description','Priority','Owner','Due Date','Labels']),('tasks-notion.csv',['Name','Description','Priority','Owner','Due','Control']),('tasks-slack-list.csv',['Name','Description','Priority','Owner','Due','Control'])]:
        with target(str(out)+'/'+name).open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(headers);w.writerows([[csv_safe(x) for x in row] for row in rows])
    text='\n'.join('- [ ] '+clean(r[0])+' ('+r[5]+')\n  '+clean(r[1]) for r in rows)
    target(str(out)+'/tasks.md').write_text(text+'\n',encoding='utf-8')
    # Prevent pasted Slack text from forming mentions or user-controlled links.
    target(str(out)+'/tasks-slack.txt').write_text(text.replace('@','＠').replace('<','‹').replace('>','›')+'\n',encoding='utf-8')
    return len(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    try:print('Exported',export(load(a.assessment),a.out),'tasks')
    except (ValueError,OSError) as e:p.exit(1,str(e)+'\n')
