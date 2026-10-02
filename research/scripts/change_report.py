"""Review two verified snapshots without promoting either one."""
import json
from snapshots import changes,replay,digest,encoded

def report(before,after):
    replay(before);replay(after)
    def sources(bundle):return {s['manifest']['file']:s for s in bundle['sources']}
    a,b=sources(before),sources(after)
    def records(source):return {r['id']:r for r in json.loads(source['recommendations.json']['text'])}
    old,new=records(a),records(b)
    details=[]
    for key in sorted(old.keys()|new.keys()):
        if old.get(key)==new.get(key):continue
        left,right=old.get(key),new.get(key)
        details.append({'sourceId':key,'kind':'added' if left is None else 'removed' if right is None else 'changed','before':left,'after':right})
    return {'schemaVersion':1,'beforeSnapshot':digest(encoded(before)),'afterSnapshot':digest(encoded(after)),
            'summary':changes(before,after),'sourceFiles':[{'file':name,'before':a[name]['manifest'],'after':b[name]['manifest'],'contentChanged':a[name]['manifest']['sha256']!=b[name]['manifest']['sha256']} for name in sorted(a)],
            'recordChanges':details,'scope':'Captured source changes only; no clinical significance is inferred. Neither snapshot is activated by this report.'}
