import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(ROOT, 'public');
const NOTES_DIR = process.env.NOTES_DIR || path.join(ROOT, 'notes');
const PORT = Number(process.env.PORT) || 3000;
const APP_TOKEN = process.env.APP_TOKEN || '';
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || '';
const ANTHROPIC_MODEL = process.env.ANTHROPIC_MODEL || 'claude-sonnet-5-5';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
};

const slugify = (s) =>
  s
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80) || 'appunto';

const validId = (id) => /^[a-z0-9][a-z0-9-]{0,79}$/.test(id);
const notePath = (id) => path.join(NOTES_DIR, `${id}.md`);

function parseNote(id, raw, mtime) {
  const meta = { title: id, subject: '', updated: mtime.toISOString() };
  let content = raw;
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (m) {
    content = raw.slice(m[0].length);
    for (const line of m[1].split(/\r?\n/)) {
      const i = line.indexOf(':');
      if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim();
    }
  }
  if (!m) {
    const h = content.match(/^#\s+(.+)$/m);
    if (h) meta.title = h[1].trim();
  }
  return { id, title: meta.title, subject: meta.subject, updated: meta.updated, content };
}

async function readNote(id) {
  const file = notePath(id);
  const [raw, stat] = await Promise.all([fs.readFile(file, 'utf8'), fs.stat(file)]);
  return parseNote(id, raw, stat.mtime);
}

async function writeNote(id, { title, subject, content }) {
  const clean = (s) => String(s ?? '').replace(/[\r\n]+/g, ' ').trim();
  const front = `---\ntitle: ${clean(title) || id}\nsubject: ${clean(subject)}\nupdated: ${new Date().toISOString()}\n---\n`;
  await fs.mkdir(NOTES_DIR, { recursive: true });
  await fs.writeFile(notePath(id), front + String(content ?? ''), 'utf8');
  return readNote(id);
}

async function uniqueId(title) {
  const base = slugify(title);
  let id = base;
  for (let n = 2; ; n++) {
    try {
      await fs.access(notePath(id));
      id = `${base}-${n}`;
    } catch {
      return id;
    }
  }
}

async function listNotes() {
  await fs.mkdir(NOTES_DIR, { recursive: true });
  const files = (await fs.readdir(NOTES_DIR)).filter((f) => f.endsWith('.md'));
  const notes = await Promise.all(
    files.map(async (f) => {
      const id = f.slice(0, -3);
      if (!validId(id)) return null;
      const n = await readNote(id);
      return { ...n, preview: n.content.replace(/[#*_`>\-\[\]]/g, '').trim().slice(0, 160) };
    }),
  );
  return notes
    .filter(Boolean)
    .map(({ content, ...rest }) => rest)
    .sort((a, b) => b.updated.localeCompare(a.updated));
}

async function generateNote({ prompt, subject }) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: ANTHROPIC_MODEL,
      max_tokens: 4096,
      system:
        'Sei un assistente che scrive appunti di studio in italiano, chiari e ben strutturati, ' +
        'in Markdown. Inizia con un titolo di primo livello (# Titolo), poi usa sezioni (##), ' +
        'elenchi, formule in testo semplice ed esempi brevi. Rispondi solo con gli appunti.',
      messages: [{ role: 'user', content: `${subject ? `Materia: ${subject}\n` : ''}Richiesta: ${prompt}` }],
    }),
  });
  if (!res.ok) throw new Error(`Errore API Anthropic (${res.status}): ${(await res.text()).slice(0, 300)}`);
  const data = await res.json();
  const text = data.content?.filter((b) => b.type === 'text').map((b) => b.text).join('') || '';
  if (!text.trim()) throw new Error('Risposta vuota dal modello');
  const title = text.match(/^#\s+(.+)$/m)?.[1]?.trim() || prompt.slice(0, 60);
  const id = await uniqueId(title);
  return writeNote(id, { title, subject, content: text.replace(/^#\s+.+\n+/, '') });
}

async function readJson(req) {
  let size = 0;
  const chunks = [];
  for await (const c of req) {
    size += c.length;
    if (size > 1_000_000) throw Object.assign(new Error('Payload troppo grande'), { status: 413 });
    chunks.push(c);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
  } catch {
    throw Object.assign(new Error('JSON non valido'), { status: 400 });
  }
}

const send = (res, status, body) => {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
};

async function handleApi(req, res, url) {
  if (APP_TOKEN && req.headers.authorization !== `Bearer ${APP_TOKEN}`) {
    return send(res, 401, { error: 'Non autorizzato' });
  }
  const parts = url.pathname.split('/').filter(Boolean).slice(1); // dopo "api"

  if (parts[0] === 'status' && req.method === 'GET') {
    return send(res, 200, { ai: Boolean(ANTHROPIC_API_KEY) });
  }

  if (parts[0] === 'generate' && req.method === 'POST') {
    if (!ANTHROPIC_API_KEY) return send(res, 503, { error: 'ANTHROPIC_API_KEY non configurata sul server' });
    const { prompt, subject } = await readJson(req);
    if (!String(prompt ?? '').trim()) return send(res, 400, { error: 'Scrivi cosa vuoi negli appunti' });
    return send(res, 201, await generateNote({ prompt: String(prompt).slice(0, 4000), subject: String(subject ?? '').slice(0, 100) }));
  }

  if (parts[0] !== 'notes') return send(res, 404, { error: 'Non trovato' });
  const id = parts[1];

  if (!id) {
    if (req.method === 'GET') return send(res, 200, await listNotes());
    if (req.method === 'POST') {
      const body = await readJson(req);
      if (!String(body.title ?? '').trim()) return send(res, 400, { error: 'Titolo mancante' });
      return send(res, 201, await writeNote(await uniqueId(body.title), body));
    }
    return send(res, 405, { error: 'Metodo non consentito' });
  }

  if (!validId(id)) return send(res, 400, { error: 'ID non valido' });
  try {
    if (req.method === 'GET') return send(res, 200, await readNote(id));
    if (req.method === 'PUT') {
      await fs.access(notePath(id));
      return send(res, 200, await writeNote(id, await readJson(req)));
    }
    if (req.method === 'DELETE') {
      await fs.unlink(notePath(id));
      return send(res, 200, { ok: true });
    }
  } catch (e) {
    if (e.code === 'ENOENT') return send(res, 404, { error: 'Appunto non trovato' });
    throw e;
  }
  return send(res, 405, { error: 'Metodo non consentito' });
}

async function handleStatic(res, url) {
  const rel = url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname.slice(1));
  const file = path.resolve(PUBLIC_DIR, rel);
  if (!file.startsWith(PUBLIC_DIR + path.sep)) return send(res, 403, { error: 'Vietato' });
  try {
    const data = await fs.readFile(file);
    res.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' });
    res.end(data);
  } catch {
    send(res, 404, { error: 'Non trovato' });
  }
}

http
  .createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    try {
      if (url.pathname.startsWith('/api/')) await handleApi(req, res, url);
      else await handleStatic(res, url);
    } catch (e) {
      console.error(e);
      if (!res.headersSent) send(res, e.status || 500, { error: e.message || 'Errore interno' });
    }
  })
  .listen(PORT, () => {
    console.log(`Appunti → http://localhost:${PORT}  (AI: ${ANTHROPIC_API_KEY ? 'attiva' : 'disattivata'})`);
  });
