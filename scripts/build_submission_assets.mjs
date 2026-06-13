#!/usr/bin/env node

import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..");
const ASSET_DIR = path.join(REPO_ROOT, "docs", "submission-assets");
const THREAD_ID = process.env.CODEX_THREAD_ID || `manual-${new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14)}`;
const WORKSPACE = path.join(REPO_ROOT, "outputs", THREAD_ID, "presentations", "t23-submission-asset-pack");
const SLIDES_DIR = path.join(WORKSPACE, "slides");
const PREVIEW_DIR = path.join(WORKSPACE, "preview");
const LAYOUT_DIR = path.join(WORKSPACE, "layout");
const OUTPUT_DIR = ASSET_DIR;
const SKILL_DIR = "/Users/junhaocheng/.codex/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations";
const NODE_BIN = "/Users/junhaocheng/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node";
const RUNTIME_NODE_MODULES = "/Users/junhaocheng/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const PYTHON_BIN = "/Users/junhaocheng/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const files = {
  coverHtml: path.join(WORKSPACE, "rfp-trustroom-cover.html"),
  coverPng: path.join(ASSET_DIR, "rfp-trustroom-cover.png"),
  deckHtml: path.join(WORKSPACE, "rfp-trustroom-submission-deck.html"),
  deckPdf: path.join(ASSET_DIR, "rfp-trustroom-submission-deck.pdf"),
  deckPptx: path.join(ASSET_DIR, "rfp-trustroom-submission-deck.pptx"),
  videoScript: path.join(ASSET_DIR, "video-script-shot-list.md"),
  submissionCopy: path.join(ASSET_DIR, "submission-copy.md"),
  dashboardShot: path.join(ASSET_DIR, "dashboard-replay-first-screen.png"),
  routeShot: path.join(ASSET_DIR, "run-trace-route.png"),
  traceShot: path.join(ASSET_DIR, "representative-traces.png"),
};

const deck = [
  {
    kicker: "TITLE",
    title: "RFP TrustRoom makes RFP response work visible, bounded, and reviewable.",
    support: "A hackathon working prototype where specialized agents coordinate through Band-style handoffs to build an evidence-backed answer pack.",
    proof: "Hybrid cover: real replay dashboard plus Intake -> Evidence -> Draft -> Review -> Approval -> Final Pack path.",
  },
  {
    kicker: "PAIN",
    title: "RFP and security questionnaires fail at the handoff, not only at generation.",
    support: "Sales, security, product, legal and SME reviewers need fresh evidence, bounded wording, and visible accountability.",
    proof: "Before-state workflow: scattered requests, stale evidence and risky commitments.",
  },
  {
    kicker: "BAND LAYER",
    title: "Band is the coordination layer, not a final notification channel.",
    support: "The demo path shows sender -> receiver transitions, shared object refs, task states and a human approval gate.",
    proof: "Agent chain: orchestrator -> decomposer -> retriever -> drafter -> reviewer -> human approver.",
  },
  {
    kicker: "RUN TRACE",
    title: "Judges can verify the workflow from the first screen.",
    support: "The route starts with Executive Decision, proof strip, Business Milestones and Agent Handoff Chain before raw logs.",
    proof: "Screenshot crop: Run Trace, milestones, handoff chain and replay boundary.",
  },
  {
    kicker: "ITEM TRACES",
    title: "The system treats happy path, review loop, and blocker path differently.",
    support: "Q-002 is approved with scoped SME context; Q-004 is rewritten after review and legal approval; Q-006 is excluded.",
    proof: "Representative Item Traces for Q-002, Q-004 and Q-006.",
  },
  {
    kicker: "RISK CONTROL",
    title: "High-risk commitments stay out of the pack without valid scoped approval.",
    support: "Q-006 has stale/conflicting evidence, no valid approval, final-pack exclusion and a policy-owner follow-up.",
    proof: "Blocked Impact Path plus approval validity language.",
  },
  {
    kicker: "FINAL PACK",
    title: "The output is a traceable answer pack, not just generated prose.",
    support: "Included answers carry evidence, review and approval context; excluded answers keep next actions visible.",
    proof: "Final Pack, evidence index, event refs and replay/live boundary.",
  },
  {
    kicker: "ARCHITECTURE",
    title: "A lightweight prototype keeps the demo stable without broadening live claims.",
    support: "FastAPI dashboard, public-safe mock/replay, Band REST boundary verified separately, autonomous replies remain a separate gate.",
    proof: "Architecture map and no-overclaim footer.",
  },
];

function ensureWithinRepo(filePath) {
  const resolved = path.resolve(filePath);
  if (!resolved.startsWith(REPO_ROOT)) {
    throw new Error(`Refusing to write outside repo: ${resolved}`);
  }
}

async function writeFile(filePath, content) {
  ensureWithinRepo(filePath);
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, "utf8");
}

function run(cmd, args, options = {}) {
  const env = {
    HOME: process.env.HOME || "",
    PATH: process.env.PATH || "",
    TMPDIR: process.env.TMPDIR || "/tmp",
    TEMP: process.env.TEMP || process.env.TMPDIR || "/tmp",
    TMP: process.env.TMP || process.env.TMPDIR || "/tmp",
    NODE_PATH: [RUNTIME_NODE_MODULES, process.env.NODE_PATH].filter(Boolean).join(":"),
    PYTHON: PYTHON_BIN,
  };
  const result = spawnSync(cmd, args, {
    cwd: REPO_ROOT,
    encoding: "utf8",
    stdio: options.stdio || "pipe",
    env,
  });
  if (result.status !== 0) {
    throw new Error(
      [
        `Command failed: ${cmd} ${args.join(" ")}`,
        result.stdout?.trim(),
        result.stderr?.trim(),
      ].filter(Boolean).join("\n"),
    );
  }
  return result.stdout;
}

async function captureScreenshots(baseUrl) {
  const require = createRequire(import.meta.url);
  const playwrightPath = require.resolve("playwright", { paths: [RUNTIME_NODE_MODULES] });
  const playwrightModule = await import(playwrightPath);
  const { chromium } = playwrightModule.default || playwrightModule;
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 3200 }, deviceScaleFactor: 1 });
  const response = await page.goto(`${baseUrl}/runs/demo/replay`, { waitUntil: "networkidle" });
  if (!response || response.status() !== 200) {
    throw new Error(`Replay route did not return 200: ${response?.status()}`);
  }

  await page.screenshot({ path: files.dashboardShot, fullPage: false });

  const runTrace = await page.locator("text=Run Trace").first().boundingBox();
  if (runTrace) {
    await page.screenshot({
      path: files.routeShot,
      clip: {
        x: 18,
        y: Math.max(0, runTrace.y - 90),
        width: 1404,
        height: 700,
      },
    });
  }

  const traces = await page.locator("text=Representative Item Traces").first().boundingBox();
  if (traces) {
    await page.screenshot({
      path: files.traceShot,
      clip: {
        x: 18,
        y: Math.max(0, traces.y - 40),
        width: 1404,
        height: 650,
      },
    });
  }

  await browser.close();
}

function htmlEscape(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function assetUrl(filePath) {
  return `file://${filePath}`;
}

function sharedStyles() {
  return `
    :root {
      --paper: #f4f6f1;
      --ink: #16211a;
      --muted: #5f6b61;
      --line: #d9dfd5;
      --green: #13824b;
      --amber: #b56b12;
      --red: #b23a36;
      --steel: #355e73;
      --white: #fbfcf8;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); font-family: Arial, Helvetica, sans-serif; }
    .slide, .cover { width: 1280px; height: 720px; position: relative; overflow: hidden; background: var(--paper); }
    .kicker { font-size: 13px; letter-spacing: .12em; text-transform: uppercase; color: var(--steel); font-weight: 700; }
    h1, h2 { margin: 0; letter-spacing: 0; }
    h1 { font-size: 60px; line-height: .98; max-width: 660px; }
    h2 { font-size: 39px; line-height: 1.04; max-width: 780px; }
    p { margin: 0; font-size: 21px; line-height: 1.35; color: var(--muted); }
    .chip { display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--line); border-radius: 999px; padding: 9px 13px; background: rgba(251,252,248,.92); font-size: 15px; font-weight: 700; }
    .chip.green { color: var(--green); border-color: rgba(19,130,75,.32); }
    .chip.amber { color: var(--amber); border-color: rgba(181,107,18,.35); }
    .chip.red { color: var(--red); border-color: rgba(178,58,54,.35); }
    .path { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
    .node { border: 1px solid var(--line); background: var(--white); border-radius: 8px; padding: 14px; min-height: 86px; }
    .node strong { display: block; font-size: 18px; margin-bottom: 7px; }
    .node span { font-size: 13px; color: var(--muted); line-height: 1.25; display: block; }
    .panel { border: 1px solid var(--line); background: rgba(251,252,248,.9); border-radius: 8px; }
    .proof-img { object-fit: contain; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .footer { position: absolute; left: 58px; right: 58px; bottom: 28px; display: flex; justify-content: space-between; color: #707c72; font-size: 12px; }
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .metric { border: 1px solid var(--line); background: var(--white); border-radius: 8px; padding: 14px; }
    .metric strong { display: block; font-size: 28px; }
    .metric span { display: block; color: var(--muted); font-size: 12px; line-height: 1.25; }
  `;
}

function coverHtml() {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${sharedStyles()}
    .cover { padding: 56px; display: grid; grid-template-columns: 1.02fr .98fr; gap: 34px; }
    .hero-copy { display: flex; flex-direction: column; justify-content: space-between; }
    .subtitle { max-width: 610px; margin-top: 22px; }
    .chips { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 30px; }
    .shot { width: 100%; height: 410px; object-fit: cover; object-position: top left; border: 1px solid var(--line); border-radius: 8px; box-shadow: 0 28px 70px rgba(23,33,26,.18); }
    .flow { margin-top: 18px; }
  </style></head><body><main class="cover">
    <section class="hero-copy">
      <div>
        <div class="kicker">Band of Agents Hackathon</div>
        <h1>RFP TrustRoom</h1>
        <p class="subtitle">Multi-agent RFP and security questionnaire response room for evidence-backed answers, review loops, and human approval gates.</p>
        <div class="chips">
          <span class="chip green">Band handoffs</span>
          <span class="chip amber">Evidence-backed answers</span>
          <span class="chip red">Human approval gates</span>
        </div>
      </div>
      <div class="path">
        ${["Intake", "Evidence", "Draft", "Review", "Approval", "Final Pack"].map((step, index) => `<div class="node"><strong>${step}</strong><span>${["RFP rows enter the room", "Freshness and gaps surfaced", "Bounded customer-safe wording", "Reviewer challenges risk", "Scoped human gate", "Unsafe item excluded"][index]}</span></div>`).join("")}
      </div>
    </section>
    <section>
      <img class="shot" src="${assetUrl(files.dashboardShot)}" alt="RFP TrustRoom replay dashboard screenshot">
      <div class="panel flow" style="padding:16px 18px;">
        <div class="kicker">30-second proof</div>
        <p style="font-size:18px; margin-top:8px;">Run Trace shows roles, handoffs, one core review loop, valid approvals, final-pack decision, and the replay/live boundary.</p>
      </div>
    </section>
  </main></body></html>`;
}

function slideHtml(slide, index) {
  const page = index + 1;
  const screenshotProofSlide = page === 4 || page === 5;
  const textWidth = screenshotProofSlide ? 500 : page === 8 ? 690 : 760;
  const supportWidth = screenshotProofSlide ? 500 : 680;
  const visualTop = screenshotProofSlide ? 132 : page === 8 ? 246 : 116;
  const visual = (() => {
    if (page === 1) {
      return `<img class="proof-img" style="width:535px;height:330px;" src="${assetUrl(files.dashboardShot)}" alt="Dashboard first screen">`;
    }
    if (page === 4) {
      return `<img class="proof-img" style="width:620px;height:360px;" src="${assetUrl(files.routeShot)}" alt="Run Trace route screenshot">`;
    }
    if (page === 5) {
      return `<img class="proof-img" style="width:620px;height:360px;" src="${assetUrl(files.traceShot)}" alt="Representative item traces screenshot">`;
    }
    if (page === 2) {
      return `<div class="path" style="grid-template-columns:1fr;gap:12px;width:500px;">
        ${["Sales asks for commitment", "Security hunts evidence", "Legal bounds wording", "SME approves scope", "Proposal owner packs response"].map((step, i) => `<div class="node"><strong>${step}</strong><span>${["Risk: copy outruns evidence", "Risk: stale or conflicting docs", "Risk: unconditional promises", "Risk: approval not scoped", "Risk: blocked item gets hidden"][i]}</span></div>`).join("")}
      </div>`;
    }
    if (page === 3) {
      return `<div class="path" style="grid-template-columns:repeat(2,1fr);width:610px;">
        ${["orchestrator", "decomposer", "retriever", "drafter", "reviewer", "human approver"].map((agent, i) => `<div class="node"><strong>${agent}</strong><span>${["assigns and packs", "splits requirements", "finds evidence", "writes bounded draft", "challenges risk", "scopes approval"][i]}</span></div>`).join("")}
      </div>`;
    }
    if (page === 6) {
      return `<div class="path" style="grid-template-columns:1fr;width:610px;gap:12px;">
        ${["Stale/conflicting incident evidence", "Needs human approval", "No valid approval", "Final pack excluded", "Policy owner next action"].map((step, i) => `<div class="node" style="border-color:${i < 2 ? "rgba(181,107,18,.35)" : "rgba(178,58,54,.35)"};"><strong>${step}</strong><span>${["EV-006 and EV-010 disagree", "High-risk commitment cannot pass alone", "Q-006 has no scoped approval", "Unsafe commitment stays out", "Confirm current notification language"][i]}</span></div>`).join("")}
      </div>`;
    }
    if (page === 7) {
      return `<div class="metric-grid" style="width:610px;">
        <div class="metric"><strong>7/8</strong><span>answers included</span></div>
        <div class="metric"><strong>1</strong><span>blocked item retained</span></div>
        <div class="metric"><strong>REPLAY</strong><span>fallback, not live proof</span></div>
        <div class="metric"><strong>Evidence</strong><span>titles, snippets, freshness</span></div>
        <div class="metric"><strong>Approval</strong><span>role, scope, validity</span></div>
        <div class="metric"><strong>Refs</strong><span>redacted event IDs</span></div>
      </div>`;
    }
    return `<div class="path" style="grid-template-columns:1fr;width:520px;gap:12px;">
      ${["FastAPI dashboard", "Mock/replay route", "Band REST boundary", "Autonomous reply gate"].map((step, i) => `<div class="node"><strong>${step}</strong><span>${["Public-safe app shell", "Stable judge path", "Verified separately", "Not claimed until connected peer passes"][i]}</span></div>`).join("")}
    </div>`;
  })();
  return `<section class="slide">
    <div style="position:absolute;left:58px;top:44px;width:${textWidth}px;">
      <div class="kicker">${htmlEscape(slide.kicker)}</div>
      <h2 style="margin-top:12px;">${htmlEscape(slide.title)}</h2>
      <p style="margin-top:18px;max-width:${supportWidth}px;">${htmlEscape(slide.support)}</p>
    </div>
    <div style="position:absolute;right:58px;top:${visualTop}px;">${visual}</div>
    <div class="panel" style="position:absolute;left:58px;bottom:82px;width:520px;padding:16px 18px;">
      <div class="kicker">Proof object</div>
      <p style="font-size:17px;margin-top:8px;">${htmlEscape(slide.proof)}</p>
    </div>
    <div class="footer"><span>RFP TrustRoom - Band of Agents Hackathon</span><span>${page}/8</span></div>
  </section>`;
}

function deckHtml() {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${sharedStyles()}
    @page { size: 1280px 720px; margin: 0; }
    .slide { page-break-after: always; }
  </style></head><body>${deck.map(slideHtml).join("")}</body></html>`;
}

async function renderHtmlAssets() {
  const require = createRequire(import.meta.url);
  const playwrightPath = require.resolve("playwright", { paths: [RUNTIME_NODE_MODULES] });
  const playwrightModule = await import(playwrightPath);
  const { chromium } = playwrightModule.default || playwrightModule;
  const browser = await chromium.launch({ channel: "chrome", headless: true });

  await writeFile(files.coverHtml, coverHtml());
  await writeFile(files.deckHtml, deckHtml());

  const coverPage = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  await coverPage.goto(assetUrl(files.coverHtml), { waitUntil: "networkidle" });
  await coverPage.screenshot({ path: files.coverPng });

  const deckPage = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await deckPage.goto(assetUrl(files.deckHtml), { waitUntil: "networkidle" });
  await deckPage.pdf({
    path: files.deckPdf,
    width: "1280px",
    height: "720px",
    printBackground: true,
    margin: { top: "0px", right: "0px", bottom: "0px", left: "0px" },
  });

  await browser.close();
}

function slideModuleSource(slide, index) {
  const slideNumber = index + 1;
  const screenshotProofSlide = slideNumber === 4 || slideNumber === 5;
  const titleWidth = screenshotProofSlide ? 560 : slideNumber === 8 ? 690 : 760;
  const titleFontSize = slideNumber === 1 ? 46 : slideNumber === 8 ? 32 : 36;
  const supportWidth = screenshotProofSlide ? 540 : 680;
  const imagePlacement = screenshotProofSlide
    ? { x: 662, y: 132, width: 560, height: 360 }
    : { x: 745, y: 116, width: 475, height: 330 };
  const imageForSlide =
    slideNumber === 1 ? files.dashboardShot :
    slideNumber === 4 ? files.routeShot :
    slideNumber === 5 ? files.traceShot :
    undefined;
  return `export async function slide${String(slideNumber).padStart(2, "0")}(presentation, ctx) {
  const slide = presentation.slides.add();
  ctx.addShape(slide, { x: 0, y: 0, width: 1280, height: 720, fill: "#f4f6f1" });
  ctx.addText(slide, { x: 58, y: 44, width: 220, height: 24, text: ${JSON.stringify(slide.kicker)}, fontSize: 13, bold: true, color: "#355e73" });
  ctx.addText(slide, { x: 58, y: 82, width: ${titleWidth}, height: 145, text: ${JSON.stringify(slide.title)}, fontSize: ${titleFontSize}, bold: true, color: "#16211a", face: ctx.fonts.title, insets: { left: 0, right: 0, top: 0, bottom: 0 } });
  ctx.addText(slide, { x: 58, y: 242, width: ${supportWidth}, height: 92, text: ${JSON.stringify(slide.support)}, fontSize: 20, color: "#5f6b61", insets: { left: 0, right: 0, top: 0, bottom: 0 } });
  ctx.addShape(slide, { x: 58, y: 552, width: 520, height: 86, fill: "#fbfcf8", line: { style: "solid", fill: "#d9dfd5", width: 1 } });
  ctx.addText(slide, { x: 76, y: 568, width: 140, height: 18, text: "PROOF OBJECT", fontSize: 11, bold: true, color: "#355e73" });
  ctx.addText(slide, { x: 76, y: 592, width: 470, height: 36, text: ${JSON.stringify(slide.proof)}, fontSize: 15, color: "#5f6b61" });
  ${imageForSlide ? `await ctx.addImage(slide, { x: ${imagePlacement.x}, y: ${imagePlacement.y}, width: ${imagePlacement.width}, height: ${imagePlacement.height}, path: ${JSON.stringify(imageForSlide)}, fit: "contain", alt: "RFP TrustRoom screenshot" });` : ""}
  ${!imageForSlide ? deckShapeSource(slideNumber) : ""}
  ctx.addText(slide, { x: 58, y: 676, width: 320, height: 16, text: "RFP TrustRoom - Band of Agents Hackathon", fontSize: 11, color: "#707c72" });
  ctx.addText(slide, { x: 1188, y: 676, width: 34, height: 16, text: "${slideNumber}/8", fontSize: 11, color: "#707c72" });
  return slide;
}
`;
}

function deckShapeSource(slideNumber) {
  const rows = {
    2: ["Sales asks", "Security finds", "Legal bounds", "SME approves", "Owner packs"],
    3: ["orchestrator", "decomposer", "retriever", "drafter", "reviewer", "human approver"],
    6: ["stale/conflicting", "needs approval", "no valid approval", "excluded", "policy next action"],
    7: ["7/8 included", "1 blocked", "REPLAY mode", "Evidence context", "Approval scope", "Event refs"],
    8: ["FastAPI", "mock/replay", "Band REST", "autonomous gate"],
  }[slideNumber] || [];
  return rows.map((label, i) => {
    const col = slideNumber === 3 || slideNumber === 7 ? i % 2 : 0;
    const row = slideNumber === 3 || slideNumber === 7 ? Math.floor(i / 2) : i;
    const x = slideNumber === 8 ? 835 : 745 + col * 245;
    const y = slideNumber === 8 ? 160 + row * 86 : 116 + row * (slideNumber === 7 ? 104 : 86);
    const w = slideNumber === 8 ? 360 : slideNumber === 3 || slideNumber === 7 ? 220 : 475;
    const h = slideNumber === 7 ? 78 : 66;
    return `
  ctx.addShape(slide, { x: ${x}, y: ${y}, width: ${w}, height: ${h}, fill: "#fbfcf8", line: { style: "solid", fill: "#d9dfd5", width: 1 } });
  ctx.addText(slide, { x: ${x + 14}, y: ${y + 12}, width: ${w - 28}, height: 22, text: ${JSON.stringify(label)}, fontSize: 17, bold: true, color: "${slideNumber === 6 && i >= 2 ? "#b23a36" : "#16211a"}" });
  ctx.addText(slide, { x: ${x + 14}, y: ${y + 38}, width: ${w - 28}, height: 18, text: ${JSON.stringify(stepCaption(slideNumber, i))}, fontSize: 12, color: "#5f6b61" });`;
  }).join("");
}

function stepCaption(slideNumber, index) {
  const captions = {
    2: ["request enters", "freshness checked", "wording limited", "scope recorded", "unsafe item retained"],
    3: ["assigns", "triages", "retrieves", "drafts", "challenges", "approves"],
    6: ["evidence risk", "review gate", "missing scope", "fail closed", "next action"],
    7: ["final pack", "Q-006", "fallback", "source basis", "validity", "trace chips"],
    8: ["dashboard", "stable route", "verified boundary", "separate gate"],
  };
  return captions[slideNumber]?.[index] || "";
}

async function buildPptx() {
  await fs.mkdir(SLIDES_DIR, { recursive: true });
  for (let index = 0; index < deck.length; index += 1) {
    await fs.writeFile(
      path.join(SLIDES_DIR, `slide-${String(index + 1).padStart(2, "0")}.mjs`),
      slideModuleSource(deck[index], index),
      "utf8",
    );
  }

  run(NODE_BIN, [
    path.join(SKILL_DIR, "scripts", "build_artifact_deck.mjs"),
    "--workspace", WORKSPACE,
    "--slides-dir", SLIDES_DIR,
    "--out", files.deckPptx,
    "--preview-dir", PREVIEW_DIR,
    "--layout-dir", LAYOUT_DIR,
    "--contact-sheet", path.join(PREVIEW_DIR, "contact-sheet.png"),
    "--manifest", path.join(WORKSPACE, "artifact-build-manifest.json"),
    "--slide-count", "8",
  ]);
}

async function writeMarkdownAssets() {
  await writeFile(files.videoScript, `# RFP TrustRoom 5-Minute Video Script And Shot List

Status: draft-ready for recording. Use the deployed public URL once T22 deployment is authorized; until then record the local replay route for rehearsal only.

## Route

0:00-0:20 Hook / pain
- Visual: cover image or slide 1.
- Say: B2B RFP and security questionnaires are not one chatbot problem; they are cross-team evidence and approval workflows.

0:20-0:45 Solution / roles
- Visual: Band coordination layer slide.
- Say: RFP TrustRoom uses Band as the coordination layer for specialized agents and a human approver.

0:45-1:15 Executive Decision
- Visual: /runs/demo/replay first screen.
- Say: Seven answers can enter the pack; Q-006 is excluded; the customer pack is not auto-sent.

1:15-1:55 Run Trace + Business Milestones
- Visual: Run Trace proof strip and milestones.
- Say: The judge route exposes roles, handoffs, review loop, approvals, final pack and replay mode without reading raw logs.

1:55-2:35 Agent Handoff Chain
- Visual: Agent Handoff Chain.
- Say: Band-style handoffs move shared object refs and task state from orchestrator to decomposer, retriever, drafter, reviewer and human approver.

2:35-3:25 Representative Item Traces
- Visual: Q-002, Q-004 and Q-006 traces.
- Say: Q-002 is an approved path; Q-004 shows review loop -> legal approval -> included; Q-006 shows fail-closed exclusion.

3:25-4:05 Q-006 Blocked Impact Path
- Visual: stale/conflicting evidence -> needs approval -> no valid approval -> final pack excluded -> policy owner next action.
- Say: This is the enterprise buyer value moment: unsafe incident-response language stays out of the customer pack.

4:05-4:35 Final Pack
- Visual: Final Pack / Evidence Index / Approval Workbench.
- Say: The result is not just generated copy; it is an answer pack with evidence and approval context.

4:35-5:00 Boundary / value
- Visual: replay/live boundary and no-overclaim footer.
- Say: This is a hackathon working prototype. Replay is the public-safe fallback. Band REST room and handoff boundary were separately verified; autonomous live replies remain a separate gate.

## Recording notes

- Do not scroll continuously through the entire dashboard.
- Use browser zoom around 90-100%.
- Hide bookmarks, account tabs and anything that could expose raw ids or account data.
- Avoid showing live Band account pages unless sanitized.
- Do not claim public deployment until Application URL smoke has passed.
`);

  await writeFile(files.submissionCopy, `# RFP TrustRoom Submission Copy

## Project Title

RFP TrustRoom

## Short Description

A multi-agent RFP and security questionnaire response room where specialized agents coordinate through Band to draft evidence-backed answers, review risk, and keep unsafe commitments out of the final pack.

## Long Description

RFP TrustRoom turns a messy B2B RFP and security questionnaire response into a coordinated multi-agent workflow. A human brings customer requirements, questionnaire rows and company knowledge snippets into the room, then specialized agents for requirement decomposition, evidence retrieval, answer drafting and compliance review collaborate through Band-style handoffs. They share structured context, pass object references, challenge unsupported claims, escalate high-risk answers to a human SME and produce a traceable submission pack.

The demo focuses on enterprise control rather than unchecked automation. Q-002 shows scoped SME approval, Q-004 shows a reviewer challenge followed by bounded legal-approved wording, and Q-006 shows a fail-closed blocker when incident-response evidence is stale/conflicting and no valid approval exists. The public-safe replay route makes the workflow visible for judges while keeping live credentials and raw room identifiers out of the submission. Band REST room and handoff evidence were verified separately; complete autonomous live replies remain a separate gate until connected peers pass the challenge-token smoke.

## Tags

Band, Band SDK, multi-agent systems, enterprise workflow, RFP response, security questionnaire, evidence management, AI agents, traceability, human-in-the-loop, Python, FastAPI

## Asset Files

- Cover image: docs/submission-assets/rfp-trustroom-cover.png
- Slide deck PDF: docs/submission-assets/rfp-trustroom-submission-deck.pdf
- Editable deck: docs/submission-assets/rfp-trustroom-submission-deck.pptx
- Video script / shot list: docs/submission-assets/video-script-shot-list.md
`);
}

async function main() {
  const baseUrl = process.argv.includes("--base-url")
    ? process.argv[process.argv.indexOf("--base-url") + 1]
    : "http://127.0.0.1:8053";
  await fs.mkdir(ASSET_DIR, { recursive: true });
  await fs.mkdir(WORKSPACE, { recursive: true });
  await captureScreenshots(baseUrl);
  await renderHtmlAssets();
  await buildPptx();
  await writeMarkdownAssets();
  const output = Object.fromEntries(Object.entries(files).map(([key, value]) => [key, value]));
  console.log(JSON.stringify({ status: "ok", output, workspace: WORKSPACE }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
