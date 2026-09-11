import http from 'node:http';import fs from 'node:fs';import path from 'node:path';
const root=path.resolve(process.env.SERVE_ROOT||'dist'),port=Number(process.env.PORT||4173);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.png':'image/png','.glb':'model/gltf-binary','.webm':'video/webm','.mp4':'video/mp4'};
http.createServer((req,res)=>{let f;try{f=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]==='/'?'/index.html':req.url.split('?')[0]));}catch{res.writeHead(400).end();return;}if(!f.startsWith(root+path.sep)){res.writeHead(403).end();return;}
 fs.readFile(f,(e,b)=>{if(e){res.writeHead(404).end('Not found');return;}res.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});res.end(b);});
}).listen(port,'0.0.0.0',()=>console.log(`Local preview http://localhost:${port} — ${root}`));
