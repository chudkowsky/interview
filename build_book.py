#!/usr/bin/env python3
"""Build the interview prep viewer:
  - site/index.html  : HTML shell + embedded JS
  - site/chapters/   : theory.md and questions.md per chapter (fetched on demand)

Run:  python3 build_book.py
"""

import os
import json
import shutil
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.join(BASE, "book")
OUT_DIR  = os.path.join(BASE, "site")

# ── Fetch or cache marked.min.js ──────────────────────────────────────────────
MARKED_CACHE = os.path.join(BASE, ".marked.min.js")
if not os.path.exists(MARKED_CACHE):
    print("Fetching marked.min.js...")
    urllib.request.urlretrieve(
        "https://cdn.jsdelivr.net/npm/marked/marked.min.js", MARKED_CACHE
    )
with open(MARKED_CACHE, "r", encoding="utf-8") as f:
    MARKED_JS = f.read()

# ── Discover chapters in order ────────────────────────────────────────────────
CHAPTER_TITLES = {
    "01_foundation":      "Layer 1: Foundation — DeFi, AMMs, Liquidity Pools",
    "02_lp_mechanics":    "Layer 2: LP Mechanics — Impermanent Loss, Fees, Yield",
    "03_defi_primitives": "Layer 3: DeFi Primitives — Lending, Flash Loans, Oracles",
    "04_defi_ecosystem":  "Layer 4: DeFi Ecosystem — Governance, Composability, Security",
    "05_mempool_mev_basics": "Layer 5: Mempool & MEV Basics",
    "06_mev_strategies":  "Layer 6: MEV Strategies — Sandwich, Arbitrage, Liquidation",
    "07_flashbots_pbs":   "Layer 7: Flashbots & PBS — Bundles, Relays, MEV-Boost",
    "08_uniswap_v3":      "Layer 8: Uniswap V3 — Concentrated Liquidity, Ticks",
    "09_synthesis":       "Layer 9: Synthesis — MEV in V3, Sandwich Protection",
}

chapters = []
for entry in sorted(os.listdir(BOOK_DIR)):
    path = os.path.join(BOOK_DIR, entry)
    if not os.path.isdir(path):
        continue
    theory_src    = os.path.join(path, "theory.md")
    questions_src = os.path.join(path, "questions.md")
    if not os.path.exists(theory_src):
        continue
    title = CHAPTER_TITLES.get(entry, entry)
    chapters.append({
        "slug":     entry,
        "title":    title,
        "theory":   theory_src,
        "questions": questions_src if os.path.exists(questions_src) else None,
    })

# ── Output directories ────────────────────────────────────────────────────────
chapters_out = os.path.join(OUT_DIR, "chapters")
os.makedirs(chapters_out, exist_ok=True)

# ── Copy markdown files ───────────────────────────────────────────────────────
for ch in chapters:
    shutil.copy2(ch["theory"],    os.path.join(chapters_out, ch["slug"] + "_theory.md"))
    if ch["questions"]:
        shutil.copy2(ch["questions"], os.path.join(chapters_out, ch["slug"] + "_questions.md"))

# ── TOC JSON (no content) ─────────────────────────────────────────────────────
toc_json = json.dumps(
    [{"slug": ch["slug"], "title": ch["title"], "hasQuestions": ch["questions"] is not None}
     for ch in chapters],
    ensure_ascii=False,
)

# ── HTML shell ────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DeFi & MEV Interview Prep</title>
<script>{MARKED_JS}</script>
<style>
  :root {{
    --bg: #f9f6f1;
    --sidebar-bg: #1a1a2e;
    --sidebar-text: #c8c8d4;
    --text: #2c2c2c;
    --heading: #1a1a2e;
    --accent: #e94560;
    --link: #0a3d8f;
    --border: #ddd6cb;
    --code-bg: #f0ede8;
    --shadow: rgba(0,0,0,0.08);
    --sidebar-width: 300px;
    --tab-active-bg: #e94560;
    --tab-active-text: #fff;
  }}
  [data-theme="dark"] {{
    --bg: #12121e;
    --sidebar-bg: #0d0d1a;
    --sidebar-text: #a0a0b8;
    --text: #d4d4e0;
    --heading: #e8e8f0;
    --link: #6aa3e8;
    --border: #2a2a3e;
    --code-bg: #1e1e30;
    --shadow: rgba(0,0,0,0.3);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Georgia', serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    min-height: 100vh;
    transition: background 0.2s, color 0.2s;
  }}

  /* ── Sidebar ── */
  #sidebar {{
    width: var(--sidebar-width);
    background: var(--sidebar-bg);
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    overflow-y: auto;
    z-index: 100;
    transition: transform 0.3s;
  }}
  #sidebar-header {{
    padding: 28px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
  }}
  #sidebar-header .book-title {{
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    line-height: 1.4;
    margin-bottom: 4px;
  }}
  #sidebar-header .book-subtitle {{
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  #toc {{ padding: 12px 0; flex: 1; }}
  .toc-item {{
    display: block;
    padding: 9px 20px;
    color: var(--sidebar-text);
    cursor: pointer;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 12px;
    line-height: 1.4;
    border-left: 3px solid transparent;
    transition: all 0.15s;
  }}
  .toc-item:hover {{ color: #fff; background: rgba(255,255,255,0.05); }}
  .toc-item.active {{ color: #fff; border-left-color: var(--accent); background: rgba(233,69,96,0.1); }}
  #sidebar-footer {{
    padding: 16px 20px;
    border-top: 1px solid rgba(255,255,255,0.07);
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    line-height: 1.6;
  }}

  /* ── Main ── */
  #main {{
    margin-left: var(--sidebar-width);
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }}
  #topbar {{
    position: sticky;
    top: 0;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    padding: 10px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 50;
    box-shadow: 0 1px 4px var(--shadow);
  }}
  #chapter-title-bar {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px;
    color: var(--accent);
    font-weight: 600;
    letter-spacing: 0.03em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 500px;
  }}
  #controls {{
    display: flex;
    gap: 8px;
    align-items: center;
    flex-shrink: 0;
  }}
  .btn {{
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    cursor: pointer;
    color: var(--text);
    font-family: -apple-system, sans-serif;
    transition: all 0.15s;
  }}
  .btn:hover {{ background: var(--border); }}
  #font-size-display {{
    font-size: 12px;
    color: var(--text);
    font-family: -apple-system, sans-serif;
    min-width: 30px;
    text-align: center;
  }}

  /* ── Tabs ── */
  #tabs {{
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--border);
    background: var(--bg);
    padding: 0 48px;
  }}
  .tab-btn {{
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    font-family: -apple-system, sans-serif;
    cursor: pointer;
    color: var(--sidebar-text);
    letter-spacing: 0.04em;
    transition: all 0.15s;
  }}
  .tab-btn:hover {{ color: var(--text); }}
  .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

  /* ── Loading ── */
  #loading {{
    display: none;
    text-align: center;
    padding: 80px 48px;
    color: var(--accent);
    font-family: -apple-system, sans-serif;
    font-size: 14px;
    letter-spacing: 0.05em;
  }}
  #loading.visible {{ display: block; }}

  /* ── Content ── */
  #content {{
    max-width: 760px;
    margin: 0 auto;
    padding: 48px 48px 80px;
    width: 100%;
    overflow-wrap: break-word;
    word-break: break-word;
  }}
  #content h1 {{ font-size: 1.9em; color: var(--heading); margin-bottom: 0.3em; line-height: 1.2; font-weight: 700; }}
  #content h2 {{ font-size: 1.3em; color: var(--heading); margin-top: 2em; margin-bottom: 0.6em; padding-bottom: 0.3em; border-bottom: 1px solid var(--border); font-weight: 700; }}
  #content h3 {{ font-size: 1.05em; color: var(--heading); margin-top: 1.5em; margin-bottom: 0.4em; font-weight: 700; }}
  #content h4 {{ font-size: 0.85em; color: var(--heading); margin-top: 1.2em; margin-bottom: 0.3em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
  #content p {{ line-height: 1.8; margin-bottom: 1.1em; }}
  #content ul, #content ol {{ margin: 0.8em 0 1em 1.4em; line-height: 1.8; }}
  #content li {{ margin-bottom: 0.3em; }}
  #content li p {{ margin-bottom: 0.2em; }}
  #content a {{ color: var(--link); text-decoration: none; }}
  #content a:hover {{ text-decoration: underline; }}
  #content strong {{ color: var(--heading); font-weight: 700; }}
  #content code {{
    background: var(--code-bg);
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.85em;
  }}
  #content pre {{
    background: var(--code-bg);
    padding: 1.2em;
    border-radius: 8px;
    overflow-x: auto;
    white-space: pre;
    margin: 1.2em 0;
    border: 1px solid var(--border);
  }}
  #content pre code {{ background: none; padding: 0; font-size: 0.88em; }}
  #content blockquote {{
    border-left: 4px solid var(--accent);
    padding: 0.6em 1.2em;
    margin: 1.2em 0;
    background: var(--code-bg);
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #666;
  }}
  [data-theme="dark"] #content blockquote {{ color: #999; }}
  #content table {{
    display: block;
    width: 100%;
    border-collapse: collapse;
    overflow-x: auto;
    white-space: nowrap;
    margin: 1.2em 0;
    font-size: 0.92em;
    font-family: -apple-system, sans-serif;
  }}
  #content th {{
    background: var(--heading);
    color: var(--bg);
    padding: 8px 12px;
    text-align: left;
    font-size: 0.82em;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: normal;
    min-width: 80px;
  }}
  #content td {{
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    white-space: normal;
    min-width: 80px;
  }}
  #content tr:hover td {{ background: var(--code-bg); }}
  #content hr {{ border: none; border-top: 1px solid var(--border); margin: 2em 0; }}

  /* ── Questions mode: hide answers by default ── */
  #content.questions-mode .answer {{ display: none; }}
  #content.questions-mode .question-block {{
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: border-color 0.15s;
  }}
  #content.questions-mode .question-block:hover {{ border-color: var(--accent); }}
  #content.questions-mode .question-block.revealed .answer {{ display: block; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); }}
  #content.questions-mode .question-block .reveal-hint {{
    font-size: 11px;
    color: var(--accent);
    font-family: -apple-system, sans-serif;
    margin-top: 6px;
    letter-spacing: 0.05em;
  }}
  #content.questions-mode .question-block.revealed .reveal-hint {{ display: none; }}

  /* ── Nav footer ── */
  #nav-footer {{
    display: flex;
    justify-content: space-between;
    padding: 24px 48px 40px;
    max-width: 760px;
    margin: 0 auto;
    width: 100%;
    gap: 16px;
  }}
  .nav-btn {{
    background: none;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 20px;
    font-size: 13px;
    cursor: pointer;
    color: var(--text);
    font-family: -apple-system, sans-serif;
    transition: all 0.15s;
    text-align: left;
    max-width: 45%;
    line-height: 1.4;
  }}
  .nav-btn:hover {{ background: var(--code-bg); border-color: var(--accent); }}
  .nav-btn .direction {{ font-size: 11px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 4px; }}
  .nav-btn.next {{ text-align: right; margin-left: auto; }}
  .nav-btn:disabled {{ opacity: 0.3; cursor: default; }}
  .nav-btn:disabled:hover {{ background: none; border-color: var(--border); }}

  /* ── Mobile ── */
  #hamburger {{
    display: none;
    background: none;
    border: none;
    font-size: 26px;
    cursor: pointer;
    color: var(--text);
    padding: 8px;
    min-width: 44px;
    min-height: 44px;
    line-height: 1;
  }}
  #overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 90;
  }}

  @media (max-width: 768px) {{
    #sidebar {{ transform: translateX(-100%); }}
    #sidebar.open {{ transform: translateX(0); }}
    #overlay.open {{ display: block; }}
    #main {{ margin-left: 0; }}
    #topbar {{ padding: 6px 12px; }}
    #chapter-title-bar {{ font-size: 12px; max-width: 140px; }}
    #controls {{ gap: 4px; }}
    .btn {{ padding: 6px 8px; font-size: 13px; min-width: 36px; min-height: 36px; }}
    #tabs {{ padding: 0 16px; }}
    #content {{ padding: 24px 16px 60px; }}
    #content h1 {{ font-size: 1.4em; }}
    #nav-footer {{ padding: 12px 16px 32px; }}
    .nav-btn {{ max-width: 48%; padding: 10px 12px; font-size: 12px; }}
    #hamburger {{ display: flex; align-items: center; justify-content: center; }}
  }}
</style>
</head>
<body>

<div id="overlay" onclick="closeSidebar()"></div>

<nav id="sidebar">
  <div id="sidebar-header">
    <div class="book-title">DeFi & MEV Interview Prep</div>
    <div class="book-subtitle">Work through layers in order</div>
  </div>
  <div id="toc"></div>
  <div id="sidebar-footer">9 layers · Theory + Questions per layer</div>
</nav>

<div id="main">
  <div id="topbar">
    <button id="hamburger" onclick="toggleSidebar()">&#9776;</button>
    <div id="chapter-title-bar"></div>
    <div id="controls">
      <button class="btn" onclick="changeFont(-1)">A&#8722;</button>
      <span id="font-size-display">18</span>
      <button class="btn" onclick="changeFont(1)">A+</button>
      <button class="btn" id="theme-btn" onclick="toggleTheme()">Dark</button>
    </div>
  </div>

  <div id="tabs">
    <button class="tab-btn active" id="tab-theory" onclick="switchTab('theory')">Theory</button>
    <button class="tab-btn" id="tab-questions" onclick="switchTab('questions')">Questions</button>
  </div>

  <div id="loading">Loading&hellip;</div>
  <div id="content"></div>

  <div id="nav-footer">
    <button class="nav-btn prev" id="btn-prev" onclick="navigate(-1)">
      <span class="direction">&#8592; Previous</span>
      <span id="prev-title"></span>
    </button>
    <button class="nav-btn next" id="btn-next" onclick="navigate(1)">
      <span class="direction">Next &#8594;</span>
      <span id="next-title"></span>
    </button>
  </div>
</div>

<script>
const chapters = {toc_json};

let currentIndex = 0;
let currentTab = 'theory';   // 'theory' | 'questions'
let fontSize = 18;
const cache = {{}};

// Build TOC
const toc = document.getElementById('toc');
chapters.forEach((ch, i) => {{
  const el = document.createElement('div');
  el.className = 'toc-item';
  el.textContent = ch.title;
  el.id = 'toc-' + i;
  el.onclick = () => {{ loadChapter(i); closeSidebar(); }};
  toc.appendChild(el);
}});

function slugFor(index, tab) {{
  return chapters[index].slug + '_' + tab + '.md';
}}

async function fetchMd(slug) {{
  if (cache[slug]) return cache[slug];
  const res = await fetch('chapters/' + slug);
  if (!res.ok) throw new Error('HTTP ' + res.status);
  cache[slug] = await res.text();
  return cache[slug];
}}

async function loadChapter(index, tab) {{
  currentIndex = index;
  if (tab) currentTab = tab;

  const ch = chapters[index];

  // Update tabs visibility
  const hasQ = ch.hasQuestions;
  document.getElementById('tab-questions').style.display = hasQ ? '' : 'none';
  if (currentTab === 'questions' && !hasQ) currentTab = 'theory';

  document.getElementById('tab-theory').classList.toggle('active', currentTab === 'theory');
  document.getElementById('tab-questions').classList.toggle('active', currentTab === 'questions');

  document.getElementById('loading').classList.add('visible');
  document.getElementById('content').innerHTML = '';

  try {{
    const md = await fetchMd(slugFor(index, currentTab));
    document.getElementById('loading').classList.remove('visible');

    if (currentTab === 'questions') {{
      document.getElementById('content').innerHTML = renderQuestions(md);
      document.getElementById('content').classList.add('questions-mode');
    }} else {{
      document.getElementById('content').innerHTML = marked.parse(md);
      document.getElementById('content').classList.remove('questions-mode');
    }}
  }} catch(e) {{
    document.getElementById('loading').classList.remove('visible');
    document.getElementById('content').innerHTML =
      '<p style="color:var(--accent);padding:2em 0">Failed to load. Please refresh.</p>';
    return;
  }}

  document.getElementById('chapter-title-bar').textContent = ch.title;
  document.getElementById('content').style.fontSize = fontSize + 'px';
  window.scrollTo({{ top: 0 }});

  document.querySelectorAll('.toc-item').forEach((el, i) => {{
    el.classList.toggle('active', i === index);
  }});

  const prev = document.getElementById('btn-prev');
  const next = document.getElementById('btn-next');
  prev.disabled = index === 0;
  document.getElementById('prev-title').textContent = index > 0 ? chapters[index - 1].title : '';
  next.disabled = index === chapters.length - 1;
  document.getElementById('next-title').textContent = index < chapters.length - 1 ? chapters[index + 1].title : '';

  history.replaceState(null, '', '#' + ch.slug + (currentTab === 'questions' ? ':q' : ''));
  document.title = ch.title + ' — Interview Prep';
}}

// Render questions.md with click-to-reveal behaviour.
// Each question block starts with a bold **Q[N]** line; everything after is the answer.
function renderQuestions(md) {{
  // Split on lines starting with ** (question markers) or blank separator lines
  const rawHtml = marked.parse(md);
  const tmp = document.createElement('div');
  tmp.innerHTML = rawHtml;

  // Find all <p> children that start with a bold question marker
  const paras = Array.from(tmp.querySelectorAll('p'));
  const blocks = [];
  let current = null;

  for (const p of paras) {{
    const text = p.textContent.trim();
    const isQuestion = /^\\*?\\*?Q\\d+[\\.\\)]/.test(text) || /^Q\\d+[\\.\\)]/.test(text);
    if (isQuestion) {{
      if (current) blocks.push(current);
      current = {{ question: p, answers: [] }};
    }} else if (current) {{
      current.answers.push(p);
    }} else {{
      // Header content before first question
      blocks.push({{ header: p }});
    }}
  }}
  if (current) blocks.push(current);

  // Also grab headings from the parsed HTML
  const allElems = Array.from(tmp.children);
  const headerElems = allElems.filter(el => /^H[1-4]$/.test(el.tagName));

  let html = '';
  // Re-parse with structure preserved using the raw markdown approach instead
  // Simpler: wrap each question+answer group in a div
  html = '<div id="q-header">' + headerElems.map(e => e.outerHTML).join('') + '</div>';

  for (const block of blocks) {{
    if (block.header) {{
      html += block.header.outerHTML;
    }} else {{
      const answerHtml = block.answers.map(a => '<div class="answer">' + a.outerHTML + '</div>').join('');
      html += `<div class="question-block" onclick="this.classList.toggle('revealed')">
        ${{block.question.outerHTML}}
        ${{answerHtml ? answerHtml : ''}}
        ${{answerHtml ? '<div class="reveal-hint">Click to reveal</div>' : ''}}
      </div>`;
    }}
  }}
  return html;
}}

function switchTab(tab) {{
  loadChapter(currentIndex, tab);
}}

function navigate(dir) {{
  const next = currentIndex + dir;
  if (next >= 0 && next < chapters.length) loadChapter(next);
}}

function changeFont(delta) {{
  fontSize = Math.max(14, Math.min(26, fontSize + delta));
  document.getElementById('content').style.fontSize = fontSize + 'px';
  document.getElementById('font-size-display').textContent = fontSize;
}}

function toggleTheme() {{
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.documentElement.setAttribute('data-theme', isDark ? '' : 'dark');
  document.getElementById('theme-btn').textContent = isDark ? 'Dark' : 'Light';
  localStorage.setItem('theme', isDark ? '' : 'dark');
}}

function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}}
function closeSidebar() {{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}}

// Restore theme
const savedTheme = localStorage.getItem('theme') || '';
if (savedTheme) {{
  document.documentElement.setAttribute('data-theme', savedTheme);
  document.getElementById('theme-btn').textContent = 'Light';
}}

// Load from hash or default
const hash = location.hash.slice(1);
let startIndex = 0;
let startTab = 'theory';
if (hash) {{
  const [slugPart, tabPart] = hash.split(':');
  const idx = chapters.findIndex(c => c.slug === slugPart);
  if (idx >= 0) startIndex = idx;
  if (tabPart === 'q') startTab = 'questions';
}}
loadChapter(startIndex, startTab);
</script>
</body>
</html>
"""

out_html = os.path.join(OUT_DIR, "index.html")
with open(out_html, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"Built: {out_html}")
print(f"       {chapters_out}/  ({len(chapters) * 2} .md files)")
