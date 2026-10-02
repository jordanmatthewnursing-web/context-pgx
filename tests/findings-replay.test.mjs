import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parseGenetics,SAMPLE} from '../dist/genetics.mjs';
import {replayFindings} from '../scripts/replay-findings.mjs';
test('Report interpretation replays from retained calls',()=>assert.equal(replayFindings(parseGenetics(SAMPLE)).verified,true));
test('Changed derived finding rejected',()=>{const r=parseGenetics(SAMPLE);r.findings[0].copies=2;assert.throws(()=>replayFindings(r),/Derived/);});
test('Changed evidence fingerprint rejected',()=>{const r=JSON.parse(JSON.stringify(parseGenetics(SAMPLE)));r.evidence.manifestSha256='0';assert.throws(()=>replayFindings(r),/evidence/);});
test('Added phenotype rejected',()=>{const r=parseGenetics(SAMPLE);r.phenotype='Normal';assert.throws(()=>replayFindings(r),/Derived/);});
test('Missing call replay stays missing',()=>{const r=parseGenetics(SAMPLE.replace('rs4244285\t10\t96541616\tAG\n',''));assert.equal(replayFindings(r).verified,true);});
