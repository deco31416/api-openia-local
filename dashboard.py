"""
Dashboard HTML — Interfaz web mínima para el bridge.
Servida como archivo estático por FastAPI.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Web Bridge — Dashboard</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
        h1{color:#58a6ff;margin-bottom:8px}
        .sub{color:#8b949e;margin-bottom:24px}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
        .card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}
        .card h2{color:#58a6ff;font-size:16px;margin-bottom:12px;border-bottom:1px solid #30363d;padding-bottom:8px}
        .stat{display:flex;justify-content:space-between;padding:4px 0;font-size:14px}
        .stat .val{color:#7ee787;font-weight:600}
        .stat .warn{color:#d29922}
        .stat .err{color:#f85149}
        .conv{border:1px solid #30363d;border-radius:4px;padding:8px;margin-bottom:8px;font-size:13px}
        .conv a{color:#58a6ff;text-decoration:none}
        .conv .meta{color:#8b949e;font-size:11px;margin-top:4px}
        button{background:#238636;color:#fff;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:12px}
        button.danger{background:#da3633}
        pre{background:#0d1117;padding:8px;border-radius:4px;font-size:12px;max-height:200px;overflow-y:auto}
        .loading{color:#8b949e;font-style:italic}
    </style>
</head>
<body>
    <h1>🧠 ChatGPT Web Bridge</h1>
    <p class="sub">deco31416.com — Dashboard local</p>
    <div class="grid">
        <div class="card" id="health-card">
            <h2>🩺 Health</h2>
            <div id="health-content" class="loading">Cargando...</div>
        </div>
        <div class="card">
            <h2>📊 Uso Global</h2>
            <div id="usage-content" class="loading">Cargando...</div>
        </div>
        <div class="card">
            <h2>💬 Conversaciones</h2>
            <div id="convs-content" class="loading">Cargando...</div>
        </div>
        <div class="card">
            <h2>📋 Cola</h2>
            <div id="queue-content" class="loading">Cargando...</div>
        </div>
    </div>
    <script>
        async function load(){try{let h=await fetch('/health').then(r=>r.json());
        let u=await fetch('/v1/usage').then(r=>r.json());
        let c=await fetch('/v1/conversations').then(r=>r.json());
        renderHealth(h);renderUsage(u);renderConvs(c.data||[])}catch(e){console.error(e)}
        }function renderHealth(h){let el=document.getElementById('health-content');
        el.innerHTML=`<div class="stat"><span>Status</span><span class="val">${h.status}</span></div>
        <div class="stat"><span>Auth</span><span class="${h.authenticated?'val':'err'}">${h.authenticated?'✅':'❌'}</span></div>
        <div class="stat"><span>Uptime</span><span class="val">${h.uptime_seconds||0}s</span></div>
        ${(h.components||[]).map(c=>`<div class="stat"><span>${c.name}</span><span class="${c.status=='ok'?'val':c.status=='error'?'err':'warn'}">${c.status}</span></div>`).join('')}`}
        function renderUsage(u){let t=u.totals||{};document.getElementById('usage-content').innerHTML=`
        <div class="stat"><span>Tokens subida</span><span class="val">${t.prompt_tokens||0}</span></div>
        <div class="stat"><span>Tokens bajada</span><span class="val">${t.completion_tokens||0}</span></div>
        <div class="stat"><span>Total tokens</span><span class="val">${t.total_tokens||0}</span></div>
        <div class="stat"><span>Costo USD</span><span class="val">$${(t.cost_total_usd||0).toFixed(4)}</span></div>
        <div class="stat"><span>Llamadas</span><span class="val">${t.calls||0}</span></div>`}
        function renderConvs(data){let el=document.getElementById('convs-content');
        if(!data.length){el.innerHTML='<p class="loading">Sin conversaciones</p>';return}
        el.innerHTML=data.slice(0,10).map(c=>`<div class="conv"><a href="${c.url}" target="_blank">${c.summary||c.conversation_id}</a>
        <div class="meta">${c.model} · ${c.total_tokens||0} tokens · ${new Date((c.last_used_at||0)*1000).toLocaleString()}</div></div>`).join('')}
        load();setInterval(load,10000);
    </script>
</body>
</html>"""
