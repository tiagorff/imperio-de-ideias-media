import json,re
SP=1.0
raw=json.load(open('scribe_words.json'))
ws=raw['words'] if isinstance(raw,dict) else raw
ws=[w for w in ws if w.get('type','word')=='word' and not w['text'].startswith('[') and not w['text'].endswith(']') and not (w['text']=='mais' and 33.3<w['start']<33.42)]
lines=[re.sub(r'\[.*?\]','',l).strip() for l in open('roteiro.txt').read().strip().split('\n')]
words=[[round(w['start']/SP,3),round(w['end']/SP,3),w['text']] for w in ws]
out=[];k=0
for i,l in enumerate(lines,1):
    n=len(l.split()); seg=words[k:k+n]; k+=n
    assert [s[2] for s in seg]==l.split(),(i,[s[2] for s in seg],l)
    out.append({"i":i,"start":seg[0][0],"end":seg[-1][1],"text":l})
assert k==len(words),(k,len(words))
total=round(out[-1]['end']+1.9,2)
json.dump({"lines":out,"total":total},open('timing.json','w'),ensure_ascii=False)
json.dump(words,open('words.json','w'),ensure_ascii=False)
for o in out: print(o['i'],o['start'],o['end'],o['text'][:50])
print('total',total)
