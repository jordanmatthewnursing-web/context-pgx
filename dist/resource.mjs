/** Fetch a bounded, hash-verified artifact. Hashes establish consistency, not authorship. */
export const hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
export async function verifiedFile(url,expected,{timeoutMs=10000,maxBytes=2000000,fetcher=fetch}={}){
 const controller=new AbortController();
 const timer=setTimeout(()=>controller.abort(),timeoutMs);
 let reader;
 try{
  const res=await fetcher(url,{signal:controller.signal});
  if(!res.ok)throw Error('Evidence could not be loaded');
  if(Number(res.headers.get('content-length'))>maxBytes)throw Error('The evidence file exceeds the supported size');
  reader=res.body.getReader();const chunks=[];let size=0;
  while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>maxBytes){await reader.cancel();throw Error('The evidence file exceeds the supported size');}chunks.push(value);}
  const bytes=new Uint8Array(size);let offset=0;for(const part of chunks){bytes.set(part,offset);offset+=part.byteLength;}
  if(await hash(bytes)!==expected)throw Error('The saved evidence did not pass its integrity check');
  return {bytes:bytes.buffer,data:JSON.parse(new TextDecoder().decode(bytes))};
 }catch(error){if(controller.signal.aborted)throw Error('The evidence request timed out');throw error;}
 finally{clearTimeout(timer);reader?.releaseLock();}
}
