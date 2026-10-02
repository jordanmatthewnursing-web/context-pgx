import {SNAPSHOT, REVIEW_HASH, CHANGES_HASH} from './config.js';
const $=id=>document.getElementById(id);
const shortContexts=['ACS / PCI','Other cardiovascular','Neurovascular'];
const phenotypes=['Ultrarapid Metabolizer','Rapid Metabolizer','Normal Metabolizer','Likely Intermediate Metabolizer','Intermediate Metabolizer','Likely Poor Metabolizer','Poor Metabolizer','Indeterminate'];
let bundle, review, rows, mappings, current, phenotype, evidenceBytes;
import {hash,verifiedFile} from './resource.mjs';
function text(id,value){$(id).textContent=value;}
const date=value=>new Date(value).toLocaleDateString('en-US',{year:'numeric',month:'short',day:'numeric',timeZone:'UTC'});
function activeRow(){return rows.find(r=>r.population.trim()===current&&r.phenotypes.CYP2C19===phenotype);}
function setSelection(context,category,updateUrl=true){
 if(!mappings.some(m=>m.code===context)||!phenotypes.includes(category))throw Error('Unknown document category');
 current=context;phenotype=category;render();
 if(updateUrl)history.replaceState(null,'','#'+new URLSearchParams({context:current,phenotype}));
}
function render(){
 const row=activeRow(),mapping=mappings.find(m=>m.code===current),fda=bundle.analysis.fdaAssociation;
 if(!row)throw Error('No record covers this selection');
 $('phenotype').value=phenotype;
 document.querySelectorAll('[data-context]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.context===current)));
 text('record-title',phenotype);text('context-description',mapping.label+'. '+mapping.note);
 text('classification',row.classification??'Not reported');
 const note=row.classification==='No Recommendation'?'“No Recommendation” is the source classification. It is not an assurance of safety.':row.classification==null?'The source does not report a classification. No category is inferred.':'';text('classification-note',note);$('classification-note').hidden=!note;
 text('recommendation',row.drugrecommendation||'No recommendation text is provided in this source record.');
 text('implications',row.implications.CYP2C19||'Not reported');text('comments',row.comments||'No comments supplied.');
 text('record-locator',`CPIC record ${row.id} · version ${row.version} · context ${row.population.trim()}`);
 text('fda-text',fda.description);
 const listed=fda.directPhenotypeLabels.includes(phenotype);
 text('membership',listed?'This phenotype is explicitly named in the FDA subgroup.':'This exact phenotype label is not explicitly named in the FDA subgroup. No equivalent category is assumed.');
 const across=$('context-comparison');const focused=document.activeElement?.closest('#context-comparison button')?.dataset.context;across.replaceChildren();
 mappings.forEach((m,i)=>{const r=rows.find(r=>r.population.trim()===m.code&&r.phenotypes.CYP2C19===phenotype);const b=document.createElement('button');b.dataset.context=m.code;b.setAttribute('aria-pressed',String(m.code===current));const label=document.createElement('span');label.textContent=shortContexts[i];const result=document.createElement('strong');result.textContent=r?.classification??'Not reported';b.append(label,result);b.addEventListener('click',()=>setSelection(m.code,phenotype));across.append(b);});
 if(focused)Array.from(across.children).find(b=>b.dataset.context===focused)?.focus({preventScroll:true});
 text('status',`${mapping.label} · ${phenotype}`);
}
function restore(){if(['#sources','#workspace'].includes(location.hash)&&current)return;const p=new URLSearchParams(location.hash.slice(1));const context=p.get('context'),category=p.get('phenotype');if((context&&!mappings.some(m=>m.code===context))||(category&&!phenotypes.includes(category))){throw Error('The link contains an unknown evidence category. Open the main page to reset it');}setSelection(context||mappings[0].code,category||'Intermediate Metabolizer',false);}
function fail(error){$('content').hidden=true;text('status',error.message+'. Reload to try again.');$('status').setAttribute('role','alert');}
async function start(){
 const captured=await verifiedFile('evidence.json',SNAPSHOT);bundle=captured.data;evidenceBytes=captured.bytes;
 if(bundle.format!=='pgx-evidence-bundle-v1')throw Error('Unsupported evidence format');
 for(const s of bundle.sources){const raw=new TextEncoder().encode(s.text);if(raw.byteLength!==s.manifest.bytes||await hash(raw)!==s.manifest.sha256)throw Error('Source bytes do not match their manifest');}
 rows=JSON.parse(bundle.sources.find(s=>s.manifest.file==='recommendations.json').text);mappings=bundle.contextMap.mappings;
 if(rows.length!==24||new Set(rows.map(r=>r.population.trim()+'|'+r.phenotypes.CYP2C19)).size!==24)throw Error('Source coverage changed');
 for(const p of phenotypes)for(const m of mappings)if(!rows.some(r=>r.population.trim()===m.code&&r.phenotypes.CYP2C19===p))throw Error('Source context is missing');
 for(const p of phenotypes){const o=document.createElement('option');o.value=p;o.textContent=p;$('phenotype').append(o);}
 mappings.forEach((m,i)=>{const b=document.createElement('button');b.dataset.context=m.code;b.textContent=shortContexts[i];b.addEventListener('click',()=>setSelection(m.code,phenotype));$('contexts').append(b);});
 $('phenotype').addEventListener('change',event=>setSelection(current,event.target.value));
 text('snapshot-id',SNAPSHOT);const times=bundle.sources.map(s=>s.manifest.retrievedAt);text('snapshot-date',[...new Set(times.map(date))].join(' – ')+' (UTC)');
 for(const s of bundle.sources){const div=document.createElement('div');div.className='source-item';const a=document.createElement('a');a.href=s.manifest.url;a.target='_blank';a.rel='noopener';a.textContent=s.manifest.file;const time=document.createElement('span');time.textContent='Retrieved '+s.manifest.retrievedAt+' · '+s.manifest.bytes+' bytes';const sha=document.createElement('code');sha.textContent='SHA-256 '+s.manifest.sha256;div.append(a,time,sha);$('provenance').append(div);}
 $('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([evidenceBytes],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='pgx-evidence-'+SNAPSHOT.slice(0,12)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 restore();$('content').hidden=false;
 void loadReview();void loadChanges();
 // In-page navigation must not overwrite the shareable evidence selection.
 for(const a of document.querySelectorAll('a[href="#sources"],a[href="#workspace"]'))a.addEventListener('click',event=>{event.preventDefault();const target=document.querySelector(a.getAttribute('href'));target.focus({preventScroll:true});target.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
 window.addEventListener('hashchange',()=>{try{restore();$('content').hidden=false;$('status').setAttribute('role','status');}catch(e){fail(e);}});
 if(document.modelContext?.registerTool){try{await document.modelContext.registerTool({name:'read_evidence_selection',title:'Read the selected evidence',description:'Read the currently visible CPIC context, phenotype and source scope. No prescribing interpretation.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,untrustedContentHint:true},execute(input){if(!input||typeof input!=='object'||Array.isArray(input)||Object.keys(input).length)throw Error('Expected an empty object');if($('content').hidden)throw Error('Evidence unavailable');const row=activeRow();return {snapshot:SNAPSHOT,context:current,phenotype,recordId:row.id,classification:row.classification,sourceText:row.drugrecommendation,fdaContext:null,clinicalAgreement:'not-assessed',correspondenceReview:review?'verified-for-current-source-bytes':'unavailable'};}});}catch{/* Optional browser capability; ordinary controls remain available. */}}
}
start().catch(fail);

async function loadChanges(){
 try{
  const report=(await verifiedFile('changes.json',CHANGES_HASH)).data;
  if(report.schemaVersion!==1||report.beforeSnapshot!==SNAPSHOT||report.sourceFiles.length!==5)throw Error('Wrong change report');
  const sourceHashes=new Map(bundle.sources.map(s=>[s.manifest.file,s.manifest.sha256]));
  if(new Set(report.sourceFiles.map(s=>s.file)).size!==5||report.sourceFiles.some(s=>sourceHashes.get(s.file)!==s.before.sha256||s.contentChanged!==(s.before.sha256!==s.after.sha256)))throw Error('Mismatched comparison sources');
  const changed=report.sourceFiles.filter(s=>s.contentChanged).length;
  text('changes-status',changed?`${changed} of 5 source files changed. Inspect the original records below.`:report.summary.contextMapChanged?'The reviewed context map changed. Source file contents are unchanged.':'No source content changed across the five files. Retrieval dates differ.');
  text('changes-scope',`${report.recordChanges.length} CPIC records added, removed or changed. Context map ${report.summary.contextMapChanged?'changed':'unchanged'}. FDA row content ${report.summary.fdaContentChanged?'changed':'unchanged'}.`);
  for(const source of report.sourceFiles){const item=document.createElement('div');item.className='source-item';const name=document.createElement('strong');const names={'drug.json':'Drug identity','guideline.json':'Guideline identity','publications.json':'Guideline publications','recommendations.json':'CPIC recommendations','fda-associations.html':'FDA association table'};name.textContent=names[source.file]+' · '+(source.contentChanged?'Content changed':'Same content');const times=document.createElement('p');const stamp=value=>new Date(value).toLocaleString('en-US',{month:'short',day:'numeric',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false,timeZone:'UTC'})+' UTC';times.textContent='First: '+stamp(source.before.retrievedAt)+' / Later: '+stamp(source.after.retrievedAt);item.append(name,times);$('changes-files').append(item);}
  for(const change of report.recordChanges){const detail=document.createElement('details');const title=document.createElement('summary');title.textContent=`Record ${change.sourceId} · ${change.kind}`;detail.append(title);for(const side of ['before','after']){const label=document.createElement('h4');label.textContent=side==='before'?'Before':'After';const value=document.createElement('pre');value.textContent=change[side]===null?'No record':JSON.stringify(change[side],null,2);detail.append(label,value);}$('changes-records').append(detail);}
  text('changes-ids','First snapshot: '+report.beforeSnapshot+' / Later snapshot: '+report.afterSnapshot);
  $('changes-detail').hidden=false;
 }catch{ text('changes-status','The snapshot comparison is unavailable. The active source records remain available.');$('changes-detail').hidden=true;}
}

async function loadReview(){
 text('review-status','Correspondence review is loading.');
 try{review=(await verifiedFile('review.json',REVIEW_HASH)).data;const hashes=new Map(bundle.sources.map(s=>[s.manifest.file,s.manifest.sha256]));if(review.status!=='text-correspondence-verified'||review.apiManifest.length!==4||review.apiManifest.some(m=>hashes.get(m.file)!==m.sha256)||review.checks.length!==24||review.checks.some(c=>c.differentFields.length))throw Error('Review does not cover these source files');text('review-status','24 of 24 CPIC records match the page-linked recommendation workbook across four text fields.');text('review-detail',`The guideline page and its visible history were reviewed on ${date(review.pageReview.reviewedAt)}. The page links the 2022 publication; its latest listed correction addresses a gene-name typo in the summary. Recommendation text, classification, implications and comments match the captured workbook. This review applies only to the saved source bytes shown here.`);}catch{review=null;text('review-status','Correspondence review is unavailable for this copy. Source evidence remains available.');text('review-detail','The separate review could not be verified. No workbook correspondence claim is made.');}
}
