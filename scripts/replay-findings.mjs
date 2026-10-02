import {deriveInsights} from '../dist/insights.mjs';
// Offline validation of exported selected-marker findings, not authentication of the input assay.
import {medicationContext} from '../dist/medication-context.mjs';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {isDeepStrictEqual} from 'node:util';
import {parseGenetics,MARKERS,MARKER_EVIDENCE,RULE_VERSION} from '../dist/genetics.mjs';
export function replayFindings(report){
 if(report?.ruleVersion!==RULE_VERSION||!isDeepStrictEqual(report.evidence,MARKER_EVIDENCE))throw Error('Report uses different evidence or rule versions.');
 if(report.build!=='GRCh37'||report.strand!=='positive'||!Array.isArray(report.findings)||report.findings.length!==MARKERS.length)throw Error('Unsupported report structure.');
 let text='# 23andMe selected-call replay (not original assay data)\n# build 37\n# positive strand\n# rsid\tchromosome\tposition\tgenotype\n';
 report.findings.forEach((f,i)=>{
  if(f.id!==MARKERS[i].id)throw Error('Report marker order or identity changed.');
  if(f.genotype!==null){if(typeof f.genotype!=='string'||!/^(?:[ACGTDI]{1,2}|--)$/.test(f.genotype))throw Error('Unsupported reported call.');text+=`${f.id}\t${MARKERS[i].chromosome}\t${MARKERS[i].position}\t${f.genotype}\n`;}
 });
 // A synthetic unrelated row keeps an all-missing report parseable; it contributes no findings.
 text+='rs1\t1\t1\tAA\n';const replay=parseGenetics(text);
 for(const field of ['findings','covered','phenotype','diplotype'])if(!isDeepStrictEqual(replay[field],report[field]))throw Error(`Derived report field changed: ${field}`);
 if(report.insights!==undefined && !isDeepStrictEqual(report.insights,deriveInsights(replay)))throw Error('Personalized implications differ from retained calls and rules.');
 if(report.medicationContext!==undefined && !isDeepStrictEqual(report.medicationContext,medicationContext(report.medicationContext?.medication?.id)))throw Error('Medication context differs from captured catalog.');
 return {verified:true,ruleVersion:RULE_VERSION,scope:'Selected calls and derived findings only. Original file, total row count, duplicate count and synthetic flag cannot be authenticated from this export.'};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 try{if(!process.argv[2])throw Error('Usage: node scripts/replay-findings.mjs REPORT.json');const data=await readFile(process.argv[2]);if(data.length>1024*1024)throw Error('Report exceeds 1 MiB.');console.log(JSON.stringify(replayFindings(JSON.parse(data)),null,2));}catch(error){console.error(error.message);process.exitCode=1;}
}
