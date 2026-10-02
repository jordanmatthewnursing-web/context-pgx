import {test} from 'node:test';import assert from 'node:assert/strict';
import {MEDICATION_CATALOG,medicationContext} from '../dist/medication-context.mjs';
import {replayFindings} from '../scripts/replay-findings.mjs';import {parseGenetics,SAMPLE} from '../dist/genetics.mjs';
test('Ten distinct medication entries each have a captured source',()=>{assert.equal(new Set(MEDICATION_CATALOG.medications.map(m=>m.id)).size,10);for(const m of MEDICATION_CATALOG.medications){const c=medicationContext(m.id);assert.match(c.source.sha256,/^[a-f0-9]{64}$/);assert.ok(m.locator);assert.ok(['CYP2C19','SLCO1B1','DPYD'].includes(m.gene));}});
test('No recommendation and limited evidence are not collapsed into positive guidance',()=>{for(const id of ['esomeprazole','rabeprazole'])assert.match(medicationContext(id).medication.scope,/No recommendation/);assert.match(medicationContext('dexlansoprazole').medication.scope,/limited data/);});
test('Unsupported medication cannot silently default',()=>assert.throws(()=>medicationContext('warfarin'),/outside/));
test('Selected medication context replays exactly without changing findings',()=>{const r=parseGenetics(SAMPLE);for(const m of MEDICATION_CATALOG.medications)assert.equal(replayFindings({...r,medicationContext:medicationContext(m.id)}).verified,true);assert.equal(r.phenotype,null);});
test('Altered medication explanation fails replay',()=>{const c=medicationContext('omeprazole');c.medication.mechanism='Take a higher dose';assert.throws(()=>replayFindings({...parseGenetics(SAMPLE),medicationContext:c}),/differs/);});
