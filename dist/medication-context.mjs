import {MEDICATION_CATALOG} from './medication-catalog.mjs';
export {MEDICATION_CATALOG};
export function medicationContext(id){
 const medication=MEDICATION_CATALOG.medications.find(m=>m.id===id);
 if(!medication)throw Error('Medication is outside the supported catalog.');
 const source=MEDICATION_CATALOG.sources[medication.sourceId];
 return structuredClone({catalogVersion:MEDICATION_CATALOG.catalogVersion,manifestSha256:MEDICATION_CATALOG.manifestSha256,medication,source,scope:'Educational source context, not a recommendation inferred from the genetic file.'});
}
