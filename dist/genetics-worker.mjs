import {parseGenetics,MAX_BYTES} from './genetics.mjs';
self.onmessage=async({data})=>{
 try{
  if(data.file && data.file.size>MAX_BYTES)throw Object.assign(Error('Choose a plain text file no larger than 25 MB.'),{code:'size'});
  const text=data.file?await data.file.text():data.text;
  self.postMessage({result:parseGenetics(text)});
 }catch(error){self.postMessage({code:error?.code||'records',error:error instanceof Error?error.message:'The genetic file could not be read.'});}
};
