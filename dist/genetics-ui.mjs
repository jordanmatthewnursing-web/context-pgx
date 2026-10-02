import {importHelp} from './import-help.mjs';
import {deriveInsights} from './insights.mjs';
import {MEDICATION_CATALOG,medicationContext} from './medication-context.mjs';
import {MULTIGENE_SAMPLE as SAMPLE,MAX_BYTES,MARKERS,DPYD_SAMPLE} from './genetics.mjs';
const $=id=>document.getElementById(id),file=$('genetic-file'),status=$('status'),results=$('results');
let generation=0,worker=null;
function clearError(){$('import-error').hidden=true;file.removeAttribute('aria-invalid');file.removeAttribute('aria-describedby');}
function showError(message,code){const help=importHelp(code);$('import-error-title').textContent=help.title;$('import-error-detail').textContent=message;$('import-error-next').textContent=help.next;$('import-error').hidden=false;file.setAttribute('aria-invalid','true');file.setAttribute('aria-describedby','import-error-title import-error-next');status.textContent='File not interpreted. Recovery options are shown.';$('import-error').focus();}
$('retry-file').addEventListener('click',()=>file.click());
$('error-sample').addEventListener('click',()=>run({text:SAMPLE},true));
function stopWorker(){worker?.terminate();worker=null;$('cancel-read').hidden=true;}
function resetRead(){clearError();stopWorker();generation++;intakeVisible(true);file.value='';results.replaceChildren();results.hidden=true;status.textContent=initial;}
$('cancel-read').addEventListener('click',()=>{resetRead();status.textContent='Reading cancelled. No findings were saved.';file.focus();});
function intakeVisible(visible){document.querySelector('.intro').hidden=!visible;document.querySelector('.intake').hidden=!visible;}
const initial='This report assesses selected CYP2C19, SLCO1B1 and DPYD markers for medication implications. Coverage is shown for each gene.';
function element(tag,text,className){const e=document.createElement(tag);if(text)e.textContent=text;if(className)e.className=className;return e;}
function link(text,href){const a=element('a',text);a.href=href;a.rel='noreferrer';return a;}
function clear(){clearError();stopWorker();intakeVisible(true);generation++;file.value='';results.replaceChildren();results.hidden=true;status.textContent=initial;file.focus();}
function render(result,sample){
 const insights=deriveInsights(result);results.replaceChildren();
 let selectedMedication="clopidogrel";
 const top=element('div',null,'report-top'),heading=element('div');
 heading.append(element('p',sample?'Synthetic example · Not a person’s result':'Your file · Selected-marker review','eyebrow'));
 const title=element('h2','Your pharmacogenomics report');title.id='result-title';heading.append(title,element('p','Based on selected CYP2C19, SLCO1B1 and DPYD markers in this file.'));
 const reset=element('button','Clear results','secondary');reset.addEventListener('click',clear);const actions=element('div',null,'report-actions'); const save=element('button','Save findings','secondary'); save.addEventListener('click',()=>{const report={...result,insights,medicationContext:medicationContext(selectedMedication),synthetic:sample,scope:'Selected CYP2C19, SLCO1B1 and DPYD markers only; no phenotype or treatment recommendation.',source:'Marker and medication sources are listed separately in this report.'};const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=sample?'context-synthetic-findings.json':'context-findings.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});actions.append(save,reset);top.append(heading,actions);results.append(top);
 const coverage=element('div',null,'coverage');coverage.append(element('strong',`${result.covered} / ${MARKERS.length}`));
 const coverCopy=element('div');coverCopy.append(element('p','Selected markers with interpretable calls'),element('small',`Build 37 · Positive strand · ${result.records.toLocaleString()} records read${result.duplicates?` · ${result.duplicates} identical duplicate(s) ignored`:''}. This is not whole-gene coverage.`));coverage.append(coverCopy);results.append(coverage);
 const geneCoverage=element('div',null,'gene-coverage');for(const g of insights.geneCoverage){const cell=element('div');cell.append(element('strong',g.gene),element('span',`${g.called} / ${g.assessed} selected markers read`),element('small',g.detected.length?`${g.detected.length} assessed variant(s) detected`:g.unresolved.length?'Incomplete coverage · no reassurance inferred':'No assessed variant detected · other variants untested'));geneCoverage.append(cell);}results.append(geneCoverage);
 const overview=element('section',null,'personal-insights');overview.setAttribute('aria-label','Implications from your file');
 overview.append(element('p','What your file suggests','eyebrow'),element('h3',insights.title),element('p',insights.explanation));
 if(insights.basis.length)overview.append(element('p','Reported basis: '+insights.basis.map(b=>`${b.gene} · ${b.marker} ${b.reportedCall}`).join(' · '),'insight-basis'));
 if(insights.unresolvedMarkers.length)overview.append(element('p',`${insights.unresolvedMarkers.length} of the selected markers remain unresolved. ${insights.cards.length ? "The implications below require confirmation of the detected calls." : "Missing information cannot rule out a medication-related variant."}`,'coverage-note'));
 if(insights.interactionNote)overview.append(element('p',insights.interactionNote,'coverage-note'));
 const cards=element('div',null,'insight-cards');
 for(const card of insights.cards){const article=element('article',null,'insight-card');article.append(element('p',card.medications.join(' · '),'eyebrow'),element('h3',card.heading),element('p',card.body));if(card.sourceId==='dpyd-2017')article.append(element('p',(sample?'Synthetic example · ':'')+'Dated evidence · update notice in the explanation below','evidence-scope'));const detail=element('details');detail.className='evidence-path';detail.append(element('summary','Why this appears'));
 const steps=element('ol',null,'trace-steps');
 const observed=element('li');observed.append(element('strong','Reported in your file'));
 for(const b of card.trace.basis){observed.append(element('p',`${b.gene} · ${b.marker} · ${b.reportedCall}`,'trace-call'));if(b.codingName)observed.append(element('p',`Coding-DNA name: ${b.codingName}. Genomic substitution: ${b.genomicSubstitution}. ${b.orientation}`,'trace-context'));}
 const rule=element('li');rule.append(element('strong','How this was interpreted'),element('p',card.trace.trigger));
 if(card.trace.otherSelectedCalls.length){const names={'detected':'variant detected','not-detected':'assessed variant not detected','missing':'not in this file','no-call':'no call','unsupported':'outside this rule set'};rule.append(element('p','Other selected calls in this gene: '+card.trace.otherSelectedCalls.map(f=>`${f.marker}: ${f.reportedCall??'missing'} (${names[f.state]})`).join('; '),'trace-context'));}
 const source=element('li');source.append(element('strong','Evidence used'),link('CPIC guideline ↗',card.trace.source.url),element('p',card.trace.source.locator));steps.append(observed,rule,source);
 detail.append(steps,element('p',card.trace.limitation,'trace-limit'));if(card.trace.source.updateNotice){const note=element('aside',null,'source-update');note.append(element('strong','Evidence update'),element('p',card.trace.source.updateNotice.summary),link('CPIC update notice · July 2026 ↗',card.trace.source.updateNotice.url));detail.append(note);}
 const technical=element('details',null,'trace-technical');technical.append(element('summary','Reproduction details'),element('p',`Rule: ${card.trace.ruleId}`),element('p',`Source SHA-256: ${card.trace.source.sha256}`),element('p','The saved findings report includes this evidence path. Offline replay checks it against the retained calls and captured rules; it cannot authenticate the original assay.'));detail.append(technical);article.append(detail);cards.append(article);}
 overview.append(cards,element('p',insights.nextStep,'next-step'));results.append(overview);
 const markerHeading=element('h3','The calls behind this report');results.append(markerHeading);
 const markerList=element('div',null,'markers');
 for(const m of result.findings){
  const row=element('article',null,'marker'),identity=element('div');identity.append(element('h3',m.id),element('small',`${m.gene} · ${m.allele}`));
  const explanation=element('div');
  const labels={'detected':'Variant detected','not-detected':'Selected variant not detected','missing':'Not in this file','no-call':'No result reported','unsupported':'Call outside this rule set'};
  explanation.append(element('p',labels[m.state]));
  const descriptions={
   detected:`${m.copies} reported ${m.alternate} ${m.copies===1?'copy':'copies'} at this location. ${m.gene === "DPYD" ? "This directly assessed variant is associated with reduced DPD function. Coding-DNA names use the opposite strand from the raw file; no complete phenotype or activity score is inferred." : m.gene === "SLCO1B1" ? "This c.521T>C variant is associated with decreased transporter function. It is found in multiple haplotypes and does not establish a complete star-allele pair." : `This variant is associated with the CYP2C19 ${m.allele} allele (${m.effect}). A single marker is not a complete star-allele assignment.`}`,
   'not-detected':`The reported ${m.genotype} call does not include the ${m.alternate} variant assessed here. Other changes in this gene may still be present.`,
   missing:'This marker was not found. It may not have been tested; absence of a row is not absence of a variant.',
   'no-call':'The file contains “--” for this marker. The assay did not provide a genotype here.',
   unsupported:'The reported call is outside the supported two-base combinations. It is not interpreted or corrected.'
  };
  explanation.append(element('p',descriptions[m.state]));
  const detail=element('details');detail.append(element('summary','Location & source'),element('p',`Chromosome ${m.chromosome} · ${m.position.toLocaleString()} · GRCh37, positive strand. Assessed substitution: ${m.reference} → ${m.alternate}.`),link('NCBI marker record ↗',`https://www.ncbi.nlm.nih.gov/snp/${m.id}`));explanation.append(detail);
  row.append(identity,element('div',m.genotype??'—','call'),explanation);markerList.append(row);
 }
 const markerDetails=element('details',null,'marker-evidence');markerDetails.append(element('summary','Inspect marker calls and coverage'),markerList);results.append(markerDetails);
 const med=element('section',null,'medication');
 med.append(element('p','Medication context','eyebrow'),element('h3','Medication context.'),element('p','Explore the guideline context for a medication. This selection does not say you take it or that it is suitable for you.'));
 const label=element('label','Medication to explore');label.htmlFor='medication-select';
 const select=element('select');select.id='medication-select';
 for(const group of [...new Set(MEDICATION_CATALOG.medications.map(m=>m.group))]){
  const optgroup=element('optgroup');optgroup.label=group;
  for(const m of MEDICATION_CATALOG.medications.filter(m=>m.group===group)){const option=element('option',m.name);option.value=m.id;optgroup.append(option);}
  select.append(optgroup);
 }
 const panel=element('div',null,'medication-detail');panel.setAttribute('aria-live','polite');
 function showMedication(){
  selectedMedication=select.value;const context=medicationContext(selectedMedication),m=context.medication;panel.replaceChildren();
  panel.append(element('p',m.scope,'evidence-scope'),element('h3',m.name),element('p',m.mechanism),element('p',m.boundary),element('p','Your marker review has not established a metabolizer category or a treatment recommendation.','small'),link('Read the captured guideline source ↗',context.source.url),element('p',m.locator,'small'));
  if(context.source.updateNotice)panel.append(element('p',context.source.updateNotice.summary,'source-update'),link('CPIC update notice ↗',context.source.updateNotice.url));
  if(m.id==='clopidogrel')panel.append(link('Compare clopidogrel guideline categories →','evidence.html'));
 }
 select.addEventListener('change',showMedication);med.append(label,select,panel);showMedication();const library=element('details',null,'supporting-library');library.append(element('summary','Explore supporting medication context'),med);results.append(library);
 const method=element('details');method.append(element('summary','Interpretation boundaries & rule version'),element('p',`Rules: ${result.ruleVersion}. Evidence manifest SHA-256: ${result.evidence.manifestSha256}. No phase, star-allele pair or metabolizer phenotype was inferred. These selected calls cannot exclude rare variants, deletions or other changes. Multiple detected variants may occur on the same chromosome or different chromosomes.`),link('Selected allele nomenclature · NCBI ↗','https://www.ncbi.nlm.nih.gov/books/NBK379740/table/diazepam.Te/'),element('p','Marker coordinates were checked against NCBI RefSNP GRCh37 placements. Functional associations follow the cited CPIC clopidogrel, PPI, statin and dated DPYD guidelines. This prototype has not undergone independent clinical validation.'));results.append(method);
 intakeVisible(false);results.hidden=false;status.textContent=sample?'Synthetic example ready. No personal genetic data was used.':'File reviewed on this device. No genetic data was uploaded.';results.focus();
}
function run(input,sample){
 clearError();stopWorker();const token=++generation;results.hidden=true;results.replaceChildren();intakeVisible(true);
 status.textContent='Reading on this device…';$('cancel-read').hidden=false;
 try{
  worker=new Worker(new URL('./genetics-worker.mjs',import.meta.url),{type:'module'});
  worker.onmessage=({data})=>{if(token!==generation)return;stopWorker();file.value='';if(data.error){showError(data.error,data.code);}else{render(data.result,sample);}};
  worker.onerror=()=>{if(token!==generation)return;stopWorker();file.value='';showError('The local reader could not start.','reader');};
  worker.postMessage(input);
 }catch{stopWorker();file.value='';showError('This browser could not start the local reader.','reader');}
}
file.addEventListener('change',()=>{
 const selected=file.files?.[0];if(!selected){resetRead();return;}
 if(selected.size>MAX_BYTES){resetRead();showError('Choose a plain text file no larger than 25 MB.','size');return;}
 run({file:selected},false);
});
$('dpyd-sample').addEventListener('click',()=>{file.value='';run({text:DPYD_SAMPLE},true);});
$('sample').addEventListener('click',()=>{file.value='';run({text:SAMPLE},true);});
window.addEventListener('pagehide',()=>{clearError();stopWorker();intakeVisible(true);generation++;file.value='';results.replaceChildren();results.hidden=true;status.textContent=initial;});
