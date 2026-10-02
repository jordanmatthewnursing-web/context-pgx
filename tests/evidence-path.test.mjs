import test from 'node:test';import assert from 'node:assert/strict';import {parseGenetics,SAMPLE,MULTIGENE_SAMPLE} from '../dist/genetics.mjs';import {deriveInsights} from '../dist/insights.mjs';import {MEDICATION_CATALOG} from '../dist/medication-context.mjs';import {replayFindings} from '../scripts/replay-findings.mjs';
test('Each drug card names only its actual triggering gene and calls',()=>{const r=deriveInsights(parseGenetics(MULTIGENE_SAMPLE));assert.deepEqual(r.cards.find(c=>c.id==='statin-transport').trace.basis.map(b=>b.marker),['rs4149056']);assert.deepEqual(r.cards.find(c=>c.id==='activation').trace.basis.map(b=>b.marker),['rs4244285']);assert.equal(r.cards[0].trace.otherSelectedCalls.find(f=>f.marker==='rs12248560').state,'no-call');});
test('625 selected-call combinations keep evidence paths gene-specific and detected-only',()=>{
 let checked=0;
 for(const a of ['GG','AG','AA','--','CG'])for(const b of ['GG','AG','AA','--','CG'])for(const c of ['CC','CT','TT','--','AC'])for(const d of ['TT','CT','CC','--','AT']){
  const r=parseGenetics(SAMPLE.replace('96541616\tAG',`96541616\t${a}`).replace('96540410\tGG',`96540410\t${b}`).replace('96521657\t--',`96521657\t${c}`).replace('21331549\tTT',`21331549\t${d}`));
  const out=deriveInsights(r);
  for(const card of out.cards){const t=card.trace;assert.ok(t.basis.length);for(const basis of t.basis){const f=r.findings.find(f=>f.id===basis.marker);assert.equal(f.state,'detected');assert.equal(f.gene,t.gene);assert.equal(f.genotype,basis.reportedCall);}
   assert.equal(t.basis.length+t.otherSelectedCalls.length,r.findings.filter(f=>f.gene===t.gene).length);
   assert.equal(t.source.sha256,MEDICATION_CATALOG.sources[card.sourceId].sha256);
   if(t.gene==='CYP2C19'&&r.findings.some(f=>['rs4244285','rs4986893'].includes(f.id)&&f.state==='detected'))assert.ok(t.basis.every(f=>f.marker!=='rs12248560'));
  }
  checked++;
 }
 assert.equal(checked,625);
});
test('Missing calls remain context, never triggering evidence',()=>{const r=parseGenetics(MULTIGENE_SAMPLE.replace('rs4986893\t10\t96540410\tGG\n',''));const trace=deriveInsights(r).cards[0].trace;assert.equal(trace.otherSelectedCalls.find(f=>f.marker==='rs4986893').state,'missing');});
test('Export replay rejects a swapped marker, altered source hash or missing trace',()=>{const r=parseGenetics(MULTIGENE_SAMPLE);r.insights=deriveInsights(r);assert.equal(replayFindings(r).verified,true);for(const mutate of [x=>x.insights.cards[0].trace.basis[0].marker='rs4149056',x=>x.insights.cards[0].trace.source.sha256='fake',x=>delete x.insights.cards[0].trace]){const copy=structuredClone(r);mutate(copy);assert.throws(()=>replayFindings(copy),/implications differ/);}});
