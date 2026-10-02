import {RULE_VERSION,MARKER_EVIDENCE} from './genetics.mjs';
import {MEDICATION_CATALOG} from './medication-context.mjs';
export const INSIGHT_VERSION='pgx-marker-implications-4';
// Directional, marker-level implications. Never translate a limited array into a complete diplotype.
export function deriveInsights(result){
 if(result.ruleVersion!==RULE_VERSION||result.evidence?.manifestSha256!==MARKER_EVIDENCE.manifestSha256)throw Error('Unsupported findings version.');
 const loss=result.findings.filter(f=>f.state==='detected'&&['rs4244285','rs4986893'].includes(f.id));
 const gain=result.findings.filter(f=>f.state==='detected'&&f.id==='rs12248560');
 const unresolved=result.findings.filter(f=>!['detected','not-detected'].includes(f.state));
 const statin=result.findings.find(f=>f.id==='rs4149056');
 const statinDetected=statin?.state==='detected';
 const dpyd=result.findings.filter(f=>f.gene==='DPYD'&&f.state==='detected');
 const basis=[...dpyd,...loss,...gain,...(statinDetected?[statin]:[])].map(f=>({marker:f.id,reportedCall:f.genotype,associatedAllele:f.allele,gene:f.gene}));
 let pattern,title,explanation;
 if(loss.length){pattern=gain.length?'mixed-markers':'loss-marker';title='A reduced-function marker was found in your file.';explanation='This is a genetic signal worth reviewing for medications affected by CYP2C19. It does not establish your overall enzyme function.';}
 else if(gain.length){pattern='increased-marker';title='An increased-function marker was found in your file.';explanation='Your file contains the selected *17-associated variant. Its medication implications depend on the complete genetic result.';}
 else if(unresolved.length){pattern='insufficient-data';title='Your file cannot resolve these medication implications.';explanation='Some selected markers are absent, uncalled or unsupported. No detected signal here does not establish normal metabolism.';}
 else{pattern='no-selected-variants';title='No assessed variant was found in the reported calls.';explanation='Other changes in these genes remain untested. These selected calls cannot establish normal function or rule out medication-related risk.';}
 const cards=[];
 const add=(id,medications,heading,body,sourceId,locator)=>cards.push({id,medications,heading,body,sourceId,locator});
 if(loss.length){
  add('activation',['Clopidogrel'],'Potential for reduced activation','If the reported variant is confirmed as part of a reduced-function result, clopidogrel activation may be lower. That can reduce its antiplatelet effect. Your clinical context and confirmed genotype are needed to assess the implication.','clopidogrel-2022','2022 guideline · page 3 and Tables 2–3');
  add('clearance',['Omeprazole','Lansoprazole','Pantoprazole'],'Potential for greater drug exposure','A confirmed reduced-function result can mean slower clearance and greater exposure to these medicines. This can affect benefit and adverse effects; it does not tell us which dose or medicine is right for you.','ppi-2020','2020 guideline · page 3 and Table 2');
 }else if(gain.length){
  add('clearance',['Omeprazole','Lansoprazole','Pantoprazole'],'Possible faster clearance','If a complete clinical result confirms increased function, these medicines may clear faster and provide less acid suppression. This marker alone does not establish that phenotype.','ppi-2020','2020 guideline · page 3 and Table 2');
  add('activation',['Clopidogrel'],'No standalone response prediction','The *17 marker alone is not enough to label clopidogrel more effective or to predict a higher bleeding risk. Other variants and clinical factors still matter.','clopidogrel-2022','2022 guideline · page 3, genotype–response discussion');
 }
 if(statinDetected){
  add('statin-transport',['Simvastatin'],'Potential for greater muscle-effect risk','Your file reports the SLCO1B1 c.521T>C variant. If confirmed, this can reduce liver uptake of simvastatin acid and increase blood exposure and muscle toxicity risk. It does not mean you will develop symptoms or establish a safe dose.','statins-2022','2022 statin guideline · gene background and Table 2');
  if(!loss.length&&!gain.length){pattern='statin-marker';title='A simvastatin-response marker was found in your file.';explanation='This reported variant affects a drug transporter. It warrants clinical confirmation before it informs treatment.';}
  else{pattern='multiple-genes';title='Medication-related markers were found in two genes.';explanation='The findings below relate to different biological functions. Their effects should not be combined into one metabolism score.';}
 }
 if(dpyd.length){
  add('fluoropyrimidine-clearance',['Fluorouracil','Capecitabine'],'A finding to confirm before treatment','Your file reports a selected DPYD variant associated with reduced DPD function. If confirmed, it may mean slower fluorouracil breakdown and a higher risk of serious toxicity. This does not establish your enzyme activity or a safe dose. Review it with the treating oncology team if these medicines are being considered.','dpyd-2017','2017 guideline · gene background and drug metabolism, pages 1–3');
  if(!loss.length&&!gain.length&&!statinDetected){pattern='dpyd-marker';title='A DPYD medication-response marker was found.';explanation='This is an unconfirmed consumer-data finding. A clinical test is needed before it can inform treatment.';}
  else{pattern='multiple-genes';title='Medication-related markers were found in multiple genes.';explanation='Each implication has its own genetic basis. Do not combine these findings into a single function or risk score.';}
 }
 // Each card carries its own reproducible evidence path, not the report-wide basis.
 for(const card of cards){
  const gene=card.id==='fluoropyrimidine-clearance'?'DPYD':card.id==='statin-transport'?'SLCO1B1':'CYP2C19';
  const triggers=gene==='DPYD'?dpyd:gene==='SLCO1B1'?[statin]:(loss.length?loss:gain);
  const triggerIds=new Set(triggers.map(f=>f.id));
  const source=MEDICATION_CATALOG.sources[card.sourceId];
  card.trace={
   ruleId:`${INSIGHT_VERSION}/${card.id}/${gene==='DPYD'?'direct-variant':gene==='SLCO1B1'?'transport':loss.length?'loss':'gain'}`,
   gene,
   trigger:gene==='DPYD'?'A directly reported selected DPYD variant is present. No linked proxy or activity score was used.':gene==='SLCO1B1'?'The assessed C variant is reported at rs4149056.':loss.length?'At least one selected reduced-function-associated variant is reported.':'The selected increased-function-associated variant is reported, without a detected selected reduced-function marker.',
   basis:triggers.map(f=>({marker:f.id,reportedCall:f.genotype,associatedAllele:f.allele,gene:f.gene,...(gene==='DPYD'?{codingName:f.allele,genomicSubstitution:`${f.reference}>${f.alternate}`,orientation:'Reported bases use genomic positive strand; coding names use the opposite strand.'}:{})})),
   otherSelectedCalls:result.findings.filter(f=>f.gene===gene&&!triggerIds.has(f.id)).map(f=>({marker:f.id,reportedCall:f.genotype,state:f.state})),
   source:{id:card.sourceId,url:source.url,doi:source.doi,sha256:source.sha256,locator:card.locator,...(source.updateNotice?{updateNotice:{...source.updateNotice}}:{})},
   limitation:'These are selected, unconfirmed calls. Other variants and the complete clinical result may change the interpretation.'
  };
 }
 const geneCoverage=[...new Set(result.findings.map(f=>f.gene))].map(gene=>{const rows=result.findings.filter(f=>f.gene===gene);return {gene,assessed:rows.length,called:rows.filter(f=>['detected','not-detected'].includes(f.state)).length,detected:rows.filter(f=>f.state==='detected').map(f=>f.id),unresolved:rows.filter(f=>!['detected','not-detected'].includes(f.state)).map(f=>f.id)};});
 return {version:INSIGHT_VERSION,markerEvidence:MARKER_EVIDENCE.manifestSha256,medicationEvidence:MEDICATION_CATALOG.manifestSha256,pattern,title,explanation,basis,geneCoverage,unresolvedMarkers:unresolved.map(f=>({marker:f.id,state:f.state})),interactionNote:loss.length&&gain.length?'Both reduced- and increased-function markers are present. Do not assume they cancel each other. Phase and the complete allele pattern are unresolved.':null,cards,nextStep:cards.length?'Ask a pharmacist or prescriber whether clinical pharmacogenomic testing could clarify these findings for any relevant medication you take. Do not change treatment from this report.':'If medication response is a concern, discuss whether a clinical pharmacogenomic test would provide information this file cannot.',scope:'Marker-level implications from unconfirmed consumer data. No complete diplotype, metabolizer phenotype, individual risk estimate or dosing recommendation.'};
}
