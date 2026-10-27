import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const files = ['index.html', 'app.mjs', 'verify.mjs', 'style.css', 'riyal.svg', 'trusted-keys.json', 'robots.txt'];
const source = Object.fromEntries(files.map(name => [name, fs.readFileSync(path.join(root, name), 'utf8')]));
const registry = JSON.parse(source['trusted-keys.json']);
if (!Array.isArray(registry.keys)) throw new Error('Invalid trusted public-key registry.');
for (const key of registry.keys) {
  if (!key || typeof key.publicKey !== 'string' || Buffer.from(key.publicKey, 'base64').length !== 64 ||
      typeof key.company !== 'string' || typeof key.vat !== 'string' ||
      typeof key.cr !== 'string' || typeof key.enabled !== 'boolean') {
    throw new Error('Invalid trusted public-key entry.');
  }
}
const paths = {'/':'index.html','/index.html':'index.html','/app.mjs':'app.mjs','/verify.mjs':'verify.mjs',
  '/style.css':'style.css','/riyal.svg':'riyal.svg','/trusted-keys.json':'trusted-keys.json','/robots.txt':'robots.txt'};
const types = {'index.html':'text/html; charset=utf-8','app.mjs':'text/javascript; charset=utf-8',
  'verify.mjs':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8','riyal.svg':'image/svg+xml',
  'trusted-keys.json':'application/json; charset=utf-8','robots.txt':'text/plain; charset=utf-8'};

const worker = `const source=${JSON.stringify(source)};
const paths=${JSON.stringify(paths)};
const types=${JSON.stringify(types)};
const headers={"cache-control":"no-store, max-age=0, must-revalidate","x-content-type-options":"nosniff","referrer-policy":"no-referrer","content-security-policy":"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'","x-frame-options":"DENY","x-robots-tag":"noindex, nofollow"};
addEventListener("fetch", event => event.respondWith(handle(event.request)));
function handle(req){
 const url=new URL(req.url);
 if(req.method!=="GET" && req.method!=="HEAD")return new Response("Method not allowed",{status:405,headers:{...headers,"allow":"GET, HEAD"}});
 const file=paths[url.pathname];
 if(!file)return new Response("Not found",{status:404,headers:{...headers,"content-type":"text/plain; charset=utf-8"}});
 return new Response(req.method==="HEAD"?null:source[file],{status:200,headers:{...headers,"content-type":types[file]}});
}
`;
const directory=path.join(root,'dist');
fs.mkdirSync(directory,{recursive:true});
fs.writeFileSync(path.join(directory,'worker.js'),worker);
console.log('Built dist/worker.js from the audited document verifier and public-key registry.');
