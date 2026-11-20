"""Export unresolved controls as import-ready task files for Jira, Notion, Slack and Markdown, without contacting trackers."""
import argparse
import csv
import io
import re
from collections import Counter
from common import clean,csv_safe,load,target
from render_report import ORDER,summarize
from validate_assessment import require_valid

FORMATS=('jira','notion','slack','markdown')
FILES={'jira':('tasks-jira.csv',),'notion':('tasks-notion.csv',),'slack':('tasks-slack-list.csv','tasks-slack.txt'),'markdown':('tasks.md',)}
# Jira's default priority scheme; an importer only maps values that exist in the target site.
JIRA_PRIORITY={'critical':'Highest','high':'High','medium':'Medium','low':'Low'}
FINDING={'failed':'Failed','partially_verified':'Partially verified','insufficient_evidence':'Evidence missing'}
NOTICE='Internal readiness item, not an audit finding or opinion.'
JIRA=['Summary','Issue Type','Priority','Labels','Labels','Labels','Labels','Due Date','Description']
NOTION=['Task','Status','Priority','Finding','Dimension','Control','Area','Criteria','Owner','Due','Recommendation','Done when','Evidence to collect','Item ID']
SLACK_LIST=['Task','Priority','Status','Owner','Due date','Control','Notes']

def slug(text):return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')
def criteria(i):return clean(', '.join(i['criteria']))
def slack(text):
    # Look-alikes survive both pasting (a typed @channel pings) and webhook posting (<...> links).
    return clean(text).replace('@','＠').replace('<','‹').replace('>','›')

class Safe(str):
    """A multi-line cell whose lines were each made safe; csv_safe would flatten the line breaks."""

def description(i):
    lines=['SOC 2 Guardian '+i['key']+': '+FINDING[i['status']]+', '+i['severity']+' urgency',
        'Control: '+i['control_id']+' ('+i['dimension'].title()+'), criteria '+criteria(i)+' (interpretive mapping)',
        'Observation: '+i['observation'],'Recommendation: '+i['recommendation']]
    if i['evidence_to_collect']:lines.append('Evidence to collect: '+i['evidence_to_collect'])
    if i['period_gaps']:lines.append('Period gaps: '+', '.join(a+' to '+b for a,b in i['period_gaps']))
    lines.append('Done when: '+i['done_when'])
    if i['owner']:lines.append('Owner: '+i['owner'])
    return Safe('\n'.join(csv_safe(x) for x in lines+[NOTICE]))

def table(header,rows):
    buf=io.StringIO();w=csv.writer(buf);w.writerow(header);w.writerows([x if isinstance(x,Safe) else csv_safe(x) for x in row] for row in rows);return buf.getvalue()

def jira(items):
    return table(JIRA,[[i['key']+' '+i['summary'],'Task',JIRA_PRIORITY[i['severity']],'soc2','soc2-'+slug(i['area']),
        'confirmed-gap' if i['kind']=='gap' else 'evidence-request',i['control_id'].lower(),i['due_date'],description(i)] for i in items])

def notion(items):
    return table(NOTION,[[i['summary'],'Not started',i['severity'].capitalize(),FINDING[i['status']],i['dimension'].title(),i['control_id'],i['area'],
        criteria(i),i['owner'],i['due_date'],i['recommendation'],i['done_when'],i['evidence_to_collect'],i['key']] for i in items])

def slack_list(items):
    return table(SLACK_LIST,[[i['summary'],i['severity'].capitalize(),'Not started',i['owner'],i['due_date'],i['control_id'],
        i['key']+'. '+i['recommendation']+' Done when: '+i['done_when']] for i in items])

def groups(items):
    for sev in ORDER:
        g=[i for i in items if i['severity']==sev]
        if g:yield sev.capitalize(),g

def slack_message(items,product):
    kinds=Counter(i['kind'] for i in items)
    out=['*SOC 2 Guardian tasks: '+slack(product)+'*','_'+str(len(items))+' open items: '+str(kinds['gap'])+' confirmed gaps, '+str(kinds['evidence_request'])+' evidence requests. '+NOTICE+'_']
    for name,g in groups(items):
        out+=['','*'+name+' ('+str(len(g))+')*']
        for i in g:
            meta=', '.join(x for x in (slack(i['owner']),'due '+slack(i['due_date']) if i['due_date'] else '') if x)
            out.append('• *'+i['key']+'* '+slack(i['summary'])+(' ('+meta+')' if meta else ''))
            if i['kind']=='gap':out.append('      _Next:_ '+slack(i['recommendation']))
    return '\n'.join(out)+'\n'

def markdown(items,product):
    out=['# SOC 2 Guardian task list: '+clean(product),'','> '+NOTICE+' Check for secrets and personal data before sharing.']
    for name,g in groups(items):
        out+=['','## '+name+' ('+str(len(g))+')','']
        for i in g:
            out.append('- [ ] **'+i['key']+'** '+clean(i['summary'])+' ('+i['control_id']+', '+criteria(i)+')')
            out.append('  - Recommendation: '+clean(i['recommendation']))
            if i['evidence_to_collect']:out.append('  - Evidence to collect: '+clean(i['evidence_to_collect']))
            out.append('  - Done when: '+clean(i['done_when']))
            out.append('  - Owner: '+(clean(i['owner']) or 'Unassigned')+' · Due: '+(clean(i['due_date']) or 'not set'))
    return '\n'.join(out)+'\n'

def export(data,out,formats=FORMATS,gaps_only=False):
    unknown=[f for f in formats if f not in FORMATS]
    if unknown:raise ValueError('Unknown format(s): '+', '.join(map(str,unknown))+'. Choose from '+', '.join(FORMATS)+' or all.')
    require_valid(data);items=[i for i in summarize(data)['items'] if not gaps_only or i['kind']=='gap'];product=data['product']
    content={'tasks-jira.csv':lambda:jira(items),'tasks-notion.csv':lambda:notion(items),'tasks-slack-list.csv':lambda:slack_list(items),
        'tasks-slack.txt':lambda:slack_message(items,product),'tasks.md':lambda:markdown(items,product)}
    # Build every text and resolve every path first, so a failure leaves no partial export.
    files=[(target(str(out)+'/'+name),content[name]()) for f in dict.fromkeys(formats) for name in FILES[f]]
    for path,text in files:
        with path.open('w',newline='',encoding='utf-8') as f:f.write(text)
    return len(items)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment',required=True);p.add_argument('--out',required=True)
    p.add_argument('--format',default='all',help='Comma list of '+', '.join(FORMATS)+', or all (default)');p.add_argument('--gaps-only',action='store_true',help='Drop evidence requests')
    a=p.parse_args();formats=FORMATS if a.format.strip().lower()=='all' else tuple(dict.fromkeys(x.strip().lower() for x in a.format.split(',') if x.strip()))
    if not formats or [x for x in formats if x not in FORMATS]:p.error('Unknown format in '+repr(a.format)+'. Choose from '+', '.join(FORMATS)+' or all.')
    try:print('Exported',export(load(a.assessment),a.out,formats,a.gaps_only),'tasks')
    except (ValueError,OSError,TypeError,KeyError) as e:p.exit(1,str(e)+'\n')
