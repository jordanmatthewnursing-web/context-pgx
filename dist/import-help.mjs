// Recovery copy never includes raw lines, file names or genetic calls.
const guidance={
 archive:['Unzip the download first.','Open the ZIP on your device, then choose the original text file inside. Renaming the archive will not convert it.'],
 document:['Choose the raw data file.','PDF reports cannot be read here. Use the original 23andMe raw-data text export.'],
 vcf:['This version cannot read VCF.','VCF interpretation needs its own checks. Use a supported 23andMe export if you have one, or explore the synthetic example. Do not rename or manually convert this file.'],
 empty:['This file is empty.','Choose the original downloaded text file, or download a fresh copy from your provider.'],
 size:['This file is too large.','The limit is 25 MB. Do not remove records to make it fit; try the example while support for larger files remains open.'],
 header:['The original export header is needed.','Choose the unedited 23andMe text export. Its header must identify the provider, reference build and strand. Do not add these labels yourself.'],
 build:['The genome build is not supported.','This reader requires an unambiguous build 37 header. Do not change build labels or coordinates by hand; a different build needs a validated conversion.'],
 strand:['The strand could not be confirmed.','Choose the original positive-strand export. Missing or conflicting strand information cannot be guessed.'],
 location:['A marker location does not match.','Use a fresh, unedited export. The reader will not move a marker or reinterpret it under a different genome build.'],
 conflict:['Some records disagree.','Choose a fresh original export. Do not select one conflicting call or delete rows to force a result.'],
 reader:['The local reader could not start.','Reload the page and try again in a current browser.'],
 format:['Choose an original text export.','Compressed or binary files are not supported. Unzip the download and choose its original text file.'],
 records:['This file could not be interpreted.','Choose a fresh, unedited 23andMe export. This reader needs four tab-separated columns; it does not repair or guess genetic records.']
};
export function importHelp(code){const [title,next]=guidance[code]||guidance.records;return {title,next};}
