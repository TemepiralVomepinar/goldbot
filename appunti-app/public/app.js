const $ = (s) => document.querySelector(s);
const layout = document.querySelector('.layout');
let notes = [];
let currentId = null;
let token = (() => { try { return localStorage.getItem('appunti-token') || ''; } catch { return ''; } })();

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { 'content-type': 'application/json', ...(token ? { authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) {
    token = prompt('Inserisci la password dell\'app') || '';
    try { localStorage.setItem('appunti-token', token); } catch {}
    if (token) return api(method, url, body);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Errore ${res.status}`);
  return data;
}

const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
}

// Renderer Markdown minimale: titoli, elenchi, citazioni, codice, tabelle, righe.
function render(md) {
  const lines = md.replace(/\r\n?/g, '\n').split('\n');
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^```/.test(line)) {
      const code = [];
      for (i++; i < lines.length && !/^```/.test(lines[i]); i++) code.push(lines[i]);
      i++;
      out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`);
    } else if (/^#{1,6}\s/.test(line)) {
      const n = line.match(/^#+/)[0].length;
      out.push(`<h${n}>${inline(line.replace(/^#+\s+/, ''))}</h${n}>`);
      i++;
    } else if (/^\s*([-*]|\d+\.)\s/.test(line)) {
      const ordered = /^\s*\d+\./.test(line);
      const items = [];
      for (; i < lines.length && /^\s*([-*]|\d+\.)\s/.test(lines[i]); i++) {
        items.push(`<li>${inline(lines[i].replace(/^\s*([-*]|\d+\.)\s+/, ''))}</li>`);
      }
      out.push(`<${ordered ? 'ol' : 'ul'}>${items.join('')}</${ordered ? 'ol' : 'ul'}>`);
    } else if (/^>\s?/.test(line)) {
      const q = [];
      for (; i < lines.length && /^>\s?/.test(lines[i]); i++) q.push(lines[i].replace(/^>\s?/, ''));
      out.push(`<blockquote>${inline(q.join(' '))}</blockquote>`);
    } else if (/^\|.+\|\s*$/.test(line) && /^\|[\s:|-]+\|\s*$/.test(lines[i + 1] || '')) {
      const cells = (l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const head = cells(line);
      i += 2;
      const rows = [];
      for (; i < lines.length && /^\|.+\|\s*$/.test(lines[i]); i++) rows.push(cells(lines[i]));
      out.push(
        `<table><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join('')}</tr></thead><tbody>${rows
          .map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`)
          .join('')}</tbody></table>`,
      );
    } else if (/^(-{3,}|\*{3,})\s*$/.test(line)) {
      out.push('<hr>');
      i++;
    } else if (!line.trim()) {
      i++;
    } else {
      const p = [];
      for (; i < lines.length && lines[i].trim() && !/^(#{1,6}\s|```|>|\s*([-*]|\d+\.)\s)/.test(lines[i]); i++) p.push(lines[i]);
      out.push(`<p>${inline(p.join(' '))}</p>`);
    }
  }
  return out.join('\n');
}

function renderList() {
  const q = $('#search').value.trim().toLowerCase();
  const subj = $('#subject-filter').value;
  const shown = notes.filter(
    (n) => (!subj || n.subject === subj) && (!q || `${n.title} ${n.subject} ${n.preview}`.toLowerCase().includes(q)),
  );
  $('#list').innerHTML = shown.length
    ? shown
        .map(
          (n) => `<li data-id="${esc(n.id)}" class="${n.id === currentId ? 'active' : ''}">
            <div class="t">${esc(n.title)}</div>
            <div class="m">${esc(n.subject || 'Senza materia')} · ${new Date(n.updated).toLocaleDateString('it-IT')}</div>
            <div class="p">${esc(n.preview)}</div></li>`,
        )
        .join('')
    : '<li class="m">Nessun appunto trovato.</li>';
}

function renderSubjects() {
  const sel = $('#subject-filter');
  const keep = sel.value;
  const subjects = [...new Set(notes.map((n) => n.subject).filter(Boolean))].sort();
  sel.innerHTML = '<option value="">Tutte le materie</option>' + subjects.map((s) => `<option>${esc(s)}</option>`).join('');
  sel.value = subjects.includes(keep) ? keep : '';
}

async function refresh() {
  notes = await api('GET', '/api/notes');
  renderSubjects();
  renderList();
}

async function openNote(id) {
  const n = await api('GET', `/api/notes/${id}`);
  currentId = id;
  layout.classList.add('reading');
  $('#view').className = '';
  $('#view').innerHTML = `
    <div class="note-head">
      <div><h2>${esc(n.title)}</h2>${n.subject ? `<span class="badge">${esc(n.subject)}</span>` : ''}</div>
      <div class="actions"><button id="btn-edit">Modifica</button><button id="btn-del" class="danger">Elimina</button></div>
    </div>
    <article class="md">${render(n.content)}</article>`;
  $('#btn-edit').onclick = () => editNote(n);
  $('#btn-del').onclick = async () => {
    if (!confirm(`Eliminare "${n.title}"?`)) return;
    await api('DELETE', `/api/notes/${id}`);
    currentId = null;
    layout.classList.remove('reading');
    $('#view').className = 'empty';
    $('#view').textContent = 'Appunto eliminato.';
    await refresh();
  };
  renderList();
}

function editNote(n) {
  layout.classList.add('reading');
  $('#view').className = '';
  $('#view').innerHTML = `
    <form class="edit">
      <input id="e-title" placeholder="Titolo" required value="${esc(n?.title || '')}">
      <input id="e-subject" placeholder="Materia" list="subjects" value="${esc(n?.subject || '')}">
      <datalist id="subjects">${[...new Set(notes.map((x) => x.subject).filter(Boolean))].map((s) => `<option value="${esc(s)}">`).join('')}</datalist>
      <textarea id="e-content" placeholder="Scrivi in Markdown…">${esc(n?.content || '')}</textarea>
      <div class="actions"><button class="primary" type="submit">Salva</button><button type="button" id="e-cancel">Annulla</button></div>
    </form>`;
  $('#e-cancel').onclick = () => (n ? openNote(n.id) : showEmpty());
  $('.edit').onsubmit = async (e) => {
    e.preventDefault();
    const body = { title: $('#e-title').value, subject: $('#e-subject').value, content: $('#e-content').value };
    try {
      const saved = n ? await api('PUT', `/api/notes/${n.id}`, body) : await api('POST', '/api/notes', body);
      await refresh();
      await openNote(saved.id);
      toast('Appunto salvato');
    } catch (err) { toast(err.message); }
  };
}

function showEmpty() {
  layout.classList.remove('reading');
  $('#view').className = 'empty';
  $('#view').textContent = 'Seleziona un appunto oppure creane uno nuovo.';
}

$('#list').onclick = (e) => {
  const li = e.target.closest('li[data-id]');
  if (li) openNote(li.dataset.id).catch((err) => toast(err.message));
};
$('#btn-new').onclick = () => editNote(null);
$('#btn-back').onclick = showEmpty;
$('#search').oninput = renderList;
$('#subject-filter').onchange = renderList;

$('#gen-form').onsubmit = async (e) => {
  e.preventDefault();
  const btn = $('#gen-btn');
  btn.disabled = true;
  btn.textContent = 'Generazione in corso…';
  try {
    const n = await api('POST', '/api/generate', { prompt: $('#gen-prompt').value, subject: $('#subject-filter').value });
    $('#gen-prompt').value = '';
    await refresh();
    await openNote(n.id);
    toast('Appunto generato');
  } catch (err) { toast(err.message); }
  btn.disabled = false;
  btn.textContent = 'Genera appunto';
};

(async () => {
  try {
    const st = await api('GET', '/api/status');
    $('#gen-form').hidden = !st.ai;
    await refresh();
  } catch (err) { toast(err.message); }
})();
