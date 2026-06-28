"use strict";

// Maxout dashboard — reads data.json (from `python -m ventures.maxout.export`)
// and renders the weekly report as a dark, dependency-free SPA. All charts are
// inline SVG so it runs offline and deploys as static files.

let DATA = null;
let week = null;
const app = document.getElementById("app");

const LOGO = `<svg class="mark" width="24" height="24" viewBox="0 0 32 32" aria-hidden="true">
  <circle cx="16" cy="16" r="12" fill="none" stroke="#222b38" stroke-width="4"/>
  <circle cx="16" cy="16" r="12" fill="none" stroke="#5ad27e" stroke-width="4" stroke-linecap="round"
          stroke-dasharray="75.4" stroke-dashoffset="20" transform="rotate(-90 16 16)"/>
</svg>`;

fetch("data.json")
  .then((r) => r.json())
  .then((d) => { DATA = d; week = d.weeks[d.weeks.length - 1]; render(); })
  .catch((e) => { app.innerHTML = `<p class="err">failed to load data.json: ${e}</p>`; });

const fmt = (n) => Math.round(n).toLocaleString();
const pc = (x) => Math.round(x * 100);

function donut(p) {
  const r = 52, c = 2 * Math.PI * r, off = c * (1 - Math.max(0, Math.min(1, p)));
  return `<svg class="donut" viewBox="0 0 128 128">
    <circle class="track" cx="64" cy="64" r="${r}"/>
    <circle class="val" cx="64" cy="64" r="${r}" stroke-dasharray="${c.toFixed(1)}"
            stroke-dashoffset="${off.toFixed(1)}" transform="rotate(-90 64 64)"/>
    <text class="dnum" x="64" y="62" text-anchor="middle">${pc(p)}%</text>
    <text class="dlbl" x="64" y="82" text-anchor="middle">quota used</text>
  </svg>`;
}

function spark(values) {
  const w = 260, h = 46, pad = 5;
  const lo = Math.min(...values), hi = Math.max(...values), rng = (hi - lo) || 1;
  const pts = values.map((v, i) => {
    const x = pad + i * (w - 2 * pad) / (values.length - 1);
    const y = h - pad - ((v - lo) / rng) * (h - 2 * pad);
    return [x.toFixed(1), y.toFixed(1)];
  });
  const line = pts.map((p) => p.join(",")).join(" ");
  const last = pts[pts.length - 1];
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    <polygon class="sarea" points="${pad},${h - pad} ${line} ${w - pad},${h - pad}"/>
    <polyline class="sline" points="${line}"/>
    <circle class="sdot" cx="${last[0]}" cy="${last[1]}" r="3.2"/>
  </svg>`;
}

function streak() {
  let s = 0;
  for (let i = DATA.weeks.length - 1; i >= 0; i--) {
    if (DATA.byWeek[DATA.weeks[i]].utilization.pct >= 0.8) s++; else break;
  }
  return s;
}

function meter(label, fillPct, right, cls) {
  return `<div class="row">
    <span class="rlbl">${label}</span>
    <span class="track2"><span class="fill ${cls || ""}" style="width:${fillPct}%"></span></span>
    <span class="rval">${right}</span></div>`;
}

function render() {
  const W = DATA.byWeek[week];
  const u = W.utilization, v = W.value, bk = W.byKind, tr = DATA.trend, L = DATA.kindLabels;

  const chips = DATA.weeks.map((w) =>
    `<button class="chip${w === week ? " on" : ""}" data-w="${w}">${w}</button>`).join("");

  const maxc = Math.max(...Object.values(bk).map((d) => d.credits), 1);
  const capacity = Object.entries(bk).sort((a, b) => b[1].credits - a[1].credits)
    .map(([k, d]) => meter(L[k], d.credits / maxc * 100,
      `${fmt(d.credits)}cr · ${d.merged}/${d.attempted}`)).join("");

  const reliability = Object.entries(DATA.agentPerformance)
    .sort((a, b) => b[1].acceptance_rate - a[1].acceptance_rate)
    .map(([k, d]) => {
      const a = pc(d.acceptance_rate);
      const cls = a >= 80 ? "good" : a >= 50 ? "mid" : "bad";
      return meter(L[k], a, `${a}% · ${d.roi_min_per_credit} min/cr`, cls);
    }).join("");

  const repos = Object.entries(DATA.perRepo).map(([r, d]) =>
    `<div class="repo"><h4>${r}</h4>
      <p class="big">${d.merged} <span>merged</span></p>
      <p class="muted">${fmt(d.credits)}cr · +${d.coverage_delta}pt cov · ${d.bugs_fixed} bugs · ${d.hours_saved}h</p>
    </div>`).join("");

  const totalHours = tr.reduce((s, t) => s + t.hours_saved, 0);

  app.innerHTML = `
    <header class="top">
      <div class="brand">${LOGO}<span class="word">Maxout</span>
        <span class="tag">make your Claude Code Max quota ship</span></div>
      <div class="chips">${chips}</div>
    </header>

    <section class="hero">
      <div class="ring">${donut(u.pct)}
        <div class="ringnote">${fmt(u.idle)} credits left on the table</div></div>
      <div class="cards">
        <div class="card"><b>$${fmt(u.usd_equiv)}</b><span>capacity put to work</span></div>
        <div class="card"><b>${v.prs_merged}<small>/${v.prs_opened}</small></b><span>PRs merged · ${pc(v.acceptance_rate)}% accepted</span></div>
        <div class="card"><b>${v.hours_saved}h</b><span>saved this week</span></div>
        <div class="card"><b>${streak()}<small>wk</small></b><span>streak ≥ 80% used</span></div>
        <div class="card warn"><b>${fmt(u.wasted_credits)}</b><span>credits on PRs that didn't land</span></div>
        <div class="card"><b>${v.bugs_fixed}·${v.cves_patched}</b><span>bugs · CVEs fixed</span></div>
      </div>
    </section>

    <section class="grid2">
      <div class="panel"><h3>Where the capacity went</h3><div class="rows">${capacity}</div></div>
      <div class="panel"><h3>Momentum</h3>
        <div class="trend"><div class="tlbl">Utilization <b>${pc(tr[0].pct)}% → ${pc(tr[tr.length - 1].pct)}%</b></div>${spark(tr.map((t) => t.pct))}</div>
        <div class="trend"><div class="tlbl">Hours saved <b>${fmt(totalHours)}h total</b></div>${spark(tr.map((t) => t.hours_saved))}</div>
      </div>
    </section>

    <section class="grid2">
      <div class="panel"><h3>Autopilot reliability <small>acceptance by task type — what to prioritize</small></h3><div class="rows">${reliability}</div></div>
      <div class="panel"><h3>By repo</h3><div class="repos">${repos}</div></div>
    </section>

    <footer>${DATA.weeks.length} weeks · value lives outside the model · data from
      <code>python -m ventures.maxout.export</code></footer>`;

  app.querySelectorAll(".chip").forEach((c) =>
    c.addEventListener("click", () => { week = c.dataset.w; render(); }));
}
