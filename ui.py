"""Visual layer: design tokens, animations and small HTML components.

Character art is served from ./static (Streamlit static serving) so the browser caches it.
All dynamic text is HTML-escaped before it is placed in markup.
"""

import html
import re

import streamlit as st

IMG = "app/static/{}.webp"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Caveat+Brush&family=Caveat:wght@600;700&family=Fraunces:opsz,wght@9..144,500;9..144,650&family=JetBrains+Mono:wght@400;600&family=Nunito:wght@400;600;700;800&display=swap');

:root {
  --ink: #2F2A28; --ink-soft: #62574F; --paper: #F9F2E0; --card: #FFFBF3; --card-2: #FCF4E3;
  --line: #E8DAC0; --brick: #B5473A; --brick-dark: #93352A; --blush: #F4CFC6;
  --sage: #5F8A5B; --sage-soft: #E4ECDD; --mustard: #E2B93B; --mustard-soft: #FBEDBF; --amber-soft: #FBEBD8;
  --shadow-sm: 0 1px 2px rgba(47,42,40,.06), 0 4px 14px rgba(47,42,40,.05);
  --shadow-md: 0 14px 34px -14px rgba(47,42,40,.28);
  --radius: 20px;
}

/* ---------- base ---------- */
.stApp {
  background:
    radial-gradient(circle at 12% 8%, rgba(226,185,59,.10), transparent 32%),
    radial-gradient(circle at 92% 18%, rgba(181,71,58,.07), transparent 30%),
    radial-gradient(rgba(47,42,40,.045) 1px, transparent 1px) 0 0 / 22px 22px,
    var(--paper);
}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button, [data-testid="stWidgetLabel"] {
  font-family: 'Nunito', system-ui, sans-serif;
}
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], [data-testid="stStatusWidget"], [data-testid="InputInstructions"] { display: none !important; }
h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; color: var(--ink); letter-spacing: -.01em; }
code { font-family: 'JetBrains Mono', monospace; background: var(--mustard-soft); color: var(--ink);
       padding: .08em .38em; border-radius: 6px; font-size: .86em; }
:focus-visible { outline: 3px solid rgba(181,71,58,.45) !important; outline-offset: 2px; }

/* ---------- motion ---------- */
@keyframes float   { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-10px) } }
@keyframes bob     { 0%,100% { transform: translateY(0) rotate(-3deg) } 50% { transform: translateY(-8px) rotate(3deg) } }
@keyframes sway    { 0%,100% { transform: rotate(-1.2deg) } 50% { transform: rotate(1.2deg) } }
@keyframes hop     { 0%,100% { transform: translateY(0) scale(1,1) } 30% { transform: translateY(-20px) scale(.96,1.05) }
                     55% { transform: translateY(0) scale(1.06,.94) } 70% { transform: translateY(-6px) } }
@keyframes wiggle  { 0%,100% { transform: rotate(0) } 25% { transform: rotate(-9deg) } 75% { transform: rotate(9deg) } }
@keyframes fadeUp  { from { opacity: 0; transform: translateY(12px) } to { opacity: 1; transform: none } }
@keyframes pop     { 0% { opacity: 0; transform: scale(.9) } 70% { transform: scale(1.02) } 100% { opacity: 1; transform: scale(1) } }
@keyframes stamp   { 0% { opacity: 0; transform: scale(2.3) rotate(-24deg) } 60% { opacity: 1; transform: scale(.94) rotate(-8deg) }
                     100% { transform: scale(1) rotate(-8deg) } }
@keyframes twinkle { 0%,100% { opacity: .25; transform: scale(.7) rotate(0) } 50% { opacity: 1; transform: scale(1.1) rotate(20deg) } }
@keyframes shimmer { from { background-position: 0 0 } to { background-position: 40px 0 } }
@keyframes flip    { from { opacity: 0; transform: rotateY(80deg) } to { opacity: 1; transform: none } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
.fade-up { animation: fadeUp .5s cubic-bezier(.2,.7,.2,1) both; }

/* ---------- shared bits ---------- */
.eyebrow { font-weight: 800; font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--sage); }
.kicker { display: inline-flex; align-items: center; gap: .45rem; font-weight: 800; font-size: .72rem;
          letter-spacing: .14em; text-transform: uppercase; color: var(--brick);
          background: var(--card); border: 1.5px solid var(--line); border-radius: 999px; padding: .35rem .8rem; }
.kicker .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--brick); box-shadow: 0 0 0 4px rgba(181,71,58,.15); }
.card { background: var(--card); border: 1.5px solid var(--line); border-radius: var(--radius); padding: 1.2rem 1.35rem; box-shadow: var(--shadow-sm); }
.section-head { display: flex; align-items: baseline; gap: .8rem; flex-wrap: wrap; margin: 2.6rem 0 .9rem; }
.section-head h2 { margin: 0 !important; padding: 0 !important; font-size: 1.8rem !important; }
.section-head p { margin: 0; color: var(--ink-soft); font-size: .95rem; flex-basis: 100%; }

/* ---------- hero ---------- */
.logo { font-family: 'Caveat Brush', cursive; font-size: clamp(3rem, 6.2vw, 5rem); line-height: .95;
        color: var(--ink); margin: .85rem 0 .15rem; position: relative; display: inline-block; z-index: 0; }
.logo::after { content: ""; position: absolute; left: 4%; right: 8%; bottom: -.12em; height: .22em; background: var(--mustard);
               opacity: .55; border-radius: 40% 60% 55% 45%; z-index: -1; transform: rotate(-1.5deg); }
.subtitle { font-family: 'Fraunces', serif; font-size: 1.45rem; font-weight: 500; color: var(--ink); margin: .65rem 0 .5rem; }
.subtitle em { color: var(--brick); font-style: italic; }
.lead { color: var(--ink-soft); font-size: 1.08rem; line-height: 1.65; max-width: 36rem; margin-bottom: .9rem; }
.lead strong { color: var(--ink); }
.meta { display: flex; flex-wrap: wrap; gap: 1.1rem; color: var(--ink-soft); font-size: .9rem; font-weight: 700; margin-bottom: 1.2rem; }
.meta span { display: inline-flex; align-items: center; gap: .4rem; }
.timeline { display: flex; align-items: center; gap: .4rem 1.1rem; flex-wrap: wrap; margin: .2rem 0 1.4rem; color: var(--ink-soft); font-size: .9rem; font-weight: 700; }
.timeline .n { display: inline-grid; place-items: center; width: 1.45rem; height: 1.45rem; border-radius: 50%;
               background: var(--mustard-soft); color: var(--ink); font-size: .75rem; margin-right: .35rem; }
.timeline .bar { width: 26px; height: 2px; background: repeating-linear-gradient(90deg, var(--line) 0 4px, transparent 4px 7px); }

.stage { position: relative; height: 500px; display: flex; align-items: flex-end; justify-content: center; }
.stage .halo { position: absolute; bottom: 30px; width: 380px; height: 380px; border-radius: 50%;
               background: radial-gradient(circle, var(--mustard-soft) 0%, rgba(251,237,191,.35) 55%, transparent 70%); }
.stage .ground { position: absolute; bottom: 14px; width: 300px; height: 26px; border-radius: 50%; background: rgba(47,42,40,.09); filter: blur(3px); }
.stage .tali { position: relative; height: 410px; transform-origin: 50% 100%; animation: sway 6s ease-in-out infinite; z-index: 2;
               filter: drop-shadow(0 10px 18px rgba(47,42,40,.12)); }
.stage .pip { position: absolute; height: 130px; left: calc(50% + 34px); bottom: 10px; z-index: 3;
              animation: bob 3.2s ease-in-out infinite; cursor: pointer; filter: drop-shadow(0 8px 10px rgba(47,42,40,.15)); }
.stage .pip:hover { animation: wiggle .5s ease-in-out 2; }
.stage .bubble { position: absolute; top: 0; left: 0; max-width: 200px; z-index: 4; animation: pop .6s .4s both; }
.stage .bubble::after { left: auto; right: 22px; }
.spark { position: absolute; color: var(--mustard); font-size: 1.4rem; animation: twinkle 2.6s ease-in-out infinite; z-index: 1; }

/* ---------- auth card ---------- */
.st-key-authcard { background: var(--card); border: 1.5px solid var(--line); border-radius: 24px; padding: 1.3rem 1.4rem 1rem;
                   box-shadow: var(--shadow-md); max-width: 460px; }
.auth-title { font-family: 'Fraunces', serif; font-weight: 650; font-size: 1.25rem; margin-bottom: .1rem; }
.auth-sub { color: var(--ink-soft); font-size: .9rem; margin-bottom: .2rem; }

/* ---------- speech bubbles ---------- */
.bubble { background: var(--card); border: 1.5px solid var(--ink); border-radius: 18px; padding: .75rem 1rem;
          font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.28rem; line-height: 1.2; color: var(--ink);
          box-shadow: 3px 3px 0 var(--ink); position: relative; }
.bubble::after { content: ""; position: absolute; left: 26px; bottom: -9px; width: 16px; height: 16px; background: var(--card);
                 border-right: 1.5px solid var(--ink); border-bottom: 1.5px solid var(--ink); transform: rotate(45deg); }
.brief { display: flex; gap: 1rem; align-items: center; margin: .3rem 0 1rem; }
.brief .avatar, .avatar { width: 84px; height: 84px; flex-shrink: 0; border-radius: 50%; overflow: hidden; display: flex; align-items: flex-end;
                 justify-content: center; background: var(--mustard-soft); border: 2px solid var(--ink); box-shadow: 3px 3px 0 var(--ink);
                 animation: float 5s ease-in-out infinite; }
.avatar img { width: 112%; margin-bottom: -6%; }
.brief .bubble { font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1rem; line-height: 1.55; flex: 1; }
.brief .bubble::after { left: -9px; bottom: auto; top: 50%; margin-top: -8px; border: 0; border-left: 1.5px solid var(--ink); border-bottom: 1.5px solid var(--ink); }
.brief .who { display: block; font-family: 'Caveat', cursive; font-size: 1.2rem; color: var(--brick); margin-bottom: .1rem; }

/* ---------- evidence room ---------- */
.evidence { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .8rem; margin-bottom: 1rem; }
@media (max-width: 1100px) { .evidence { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 620px) { .evidence { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .evidence { grid-template-columns: 1fr; } }
.evidence .card { padding: .95rem 1rem; transition: transform .2s ease, box-shadow .2s ease; animation: fadeUp .5s both; }
.evidence .card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.evidence .name { font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: .95rem; color: var(--brick); }
.evidence .rows { float: right; font-size: .72rem; font-weight: 800; color: var(--sage); background: var(--sage-soft);
                  border-radius: 999px; padding: .1rem .5rem; }
.evidence .rows::before { content: "● "; font-size: .6rem; vertical-align: 1px; }
.evidence ul { list-style: none; margin: .55rem 0 0; padding: 0; }
.evidence li { display: flex; justify-content: space-between; gap: .5rem; font-size: .78rem; padding: .18rem 0; border-bottom: 1px dashed var(--line); }
.evidence li:last-child { border-bottom: 0; }
.evidence li .c { font-family: 'JetBrains Mono', monospace; color: var(--ink); }
.evidence li .t { color: var(--ink-soft); font-size: .72rem; }

/* ---------- case board ---------- */
.board-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .8rem; }
.clue-card { border-radius: 18px; padding: .9rem 1rem; min-height: 132px; position: relative; font-size: .88rem; line-height: 1.5; }
.clue-card.open { background: #FFFDF6; border: 1.5px solid var(--ink); box-shadow: 3px 3px 0 var(--mustard); animation: flip .5s both; }
.clue-card.locked { background: repeating-linear-gradient(-45deg, var(--card-2) 0 10px, var(--card) 10px 20px);
                    border: 1.5px dashed var(--line); color: var(--ink-soft); display: grid; place-items: center; text-align: center; }
.clue-card .pin { position: absolute; top: -7px; left: 50%; width: 14px; height: 14px; margin-left: -7px; border-radius: 50%;
                  background: var(--brick); box-shadow: 0 2px 0 rgba(0,0,0,.2); }
.clue-card .lbl { font-weight: 800; font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; color: var(--brick); display: block; margin-bottom: .25rem; }
.clue-card .q { font-family: 'Caveat Brush', cursive; font-size: 2.2rem; color: var(--line); line-height: 1; }
.clue-card.suspect.open { background: var(--blush); }

/* ---------- pill radios (mission stepper, table picker, sign-in mode) ---------- */
[data-testid="stRadio"] [role="radiogroup"] { gap: .45rem; flex-wrap: wrap; }
[data-testid="stRadio"] label[data-baseweb="radio"] { margin: 0; padding: .42rem .95rem; border-radius: 14px; cursor: pointer;
  border: 1.5px solid var(--line); background: var(--card-2); transition: transform .15s ease, border-color .15s ease; }
[data-testid="stRadio"] label[data-baseweb="radio"]:hover { transform: translateY(-2px); border-color: var(--ink); }
[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { display: none; }
[data-testid="stRadio"] label[data-baseweb="radio"] p { font-weight: 700; font-size: .9rem; }
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) { background: var(--ink); border-color: var(--ink); }
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p { color: var(--paper) !important; }
.st-key-peek label[data-baseweb="radio"] p { font-family: 'JetBrains Mono', monospace; font-size: .82rem; }

/* ---------- mission ---------- */
.st-key-missioncard { background: var(--card); border: 1.5px solid var(--line); border-radius: 26px; padding: 1.6rem 1.7rem;
                      box-shadow: var(--shadow-sm); margin-top: .6rem; }
.mhead { display: flex; align-items: center; gap: 1rem; position: relative; margin-bottom: .6rem; animation: fadeUp .45s both; }
.medal { flex-shrink: 0; width: 58px; height: 58px; border-radius: 16px; display: grid; place-items: center;
         background: var(--ink); color: var(--paper); font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 650;
         box-shadow: 3px 3px 0 var(--mustard); transform: rotate(-3deg); }
.mhead h3 { margin: 0 !important; padding: 0 !important; font-size: 1.6rem !important; }
.chips { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .35rem; }
.chip { font-size: .76rem; font-weight: 700; border-radius: 999px; padding: .15rem .6rem; border: 1px solid var(--line); background: var(--card-2); color: var(--ink-soft); }
.chip.pts { background: var(--mustard-soft); border-color: #EBCF7A; color: #6E5410; }
.chip.skill { background: var(--sage-soft); border-color: #C8D6BE; color: #3E5A3B; }
.chip.ok { background: var(--sage-soft); border-color: #BFD0B4; color: #2F5A2C; }
.chip.bad { background: var(--amber-soft); border-color: #EDCFA8; color: #7A4A12; }
.stamp { position: absolute; right: .4rem; top: -.2rem; font-family: 'Caveat Brush', cursive; font-size: 1.7rem; color: var(--brick);
         border: 3px solid var(--brick); border-radius: 10px; padding: .05rem .7rem; letter-spacing: .06em; opacity: .9;
         transform: rotate(-8deg); animation: stamp .55s cubic-bezier(.2,.8,.3,1.2) both; }
.task { background: var(--card-2); border-left: 4px solid var(--brick); border-radius: 0 14px 14px 0; padding: .85rem 1.1rem;
        margin: .2rem 0 1.1rem; line-height: 1.6; }
.label { display: block; font-weight: 800; font-size: .7rem; letter-spacing: .14em; text-transform: uppercase; color: var(--brick); margin-bottom: .25rem; }
.concept { background: linear-gradient(180deg, #FFFDF7, var(--card)); border: 1.5px solid var(--line); border-radius: 18px; padding: 1rem 1.1rem; margin-bottom: .8rem; }
.concept h4 { margin: 0 0 .35rem !important; padding: 0 !important; font-size: 1.12rem !important; }
.concept p { margin: 0 0 .6rem; color: var(--ink-soft); font-size: .93rem; line-height: 1.6; }
.concept .code { margin: 0; background: #2F2A28; color: #F9F2E0; border-radius: 12px; padding: .75rem .9rem; font-family: 'JetBrains Mono', monospace;
               font-size: .8rem; line-height: 1.55; white-space: normal; overflow-x: auto; }
.concept .code .kw { color: #E2B93B; font-weight: 600; }
.colhead { display: flex; align-items: center; justify-content: space-between; margin-bottom: .45rem; }
.colhead .t { font-family: 'Fraunces', serif; font-weight: 650; font-size: 1.05rem; }
.grading-note { color: var(--ink-soft); font-size: .8rem; margin-top: .2rem; }

/* ---------- feedback ---------- */
.react { display: flex; align-items: center; gap: 1rem; border-radius: 18px; padding: .8rem 1.1rem; margin: .8rem 0;
         border: 1.5px solid var(--line); animation: pop .45s both; }
.react img { height: 80px; flex-shrink: 0; }
.react.correct { background: var(--sage-soft); border-color: #BFD0B4; }
.react.correct img { animation: hop 1s ease-in-out 2; }
.react.wrong { background: var(--amber-soft); border-color: #EDCFA8; }
.react.wrong img { animation: wiggle .6s ease-in-out 2; }
.react.match { background: #EEF4FB; border-color: #C9D9EC; }
.react.locked { background: var(--card-2); }
.react.locked img { height: 64px; animation: bob 3.2s ease-in-out infinite; }
.react .title { font-family: 'Fraunces', serif; font-weight: 650; font-size: 1.08rem; }
.react .msg { color: var(--ink-soft); font-size: .94rem; line-height: 1.5; }
.react .raw { margin-top: .4rem; font-family: 'JetBrains Mono', monospace; font-size: .75rem; color: #8A4B3F; background: rgba(255,255,255,.6);
              border-radius: 8px; padding: .3rem .5rem; word-break: break-word; }
.summary { display: flex; flex-wrap: wrap; gap: .4rem; margin: .6rem 0 .5rem; }

.reveal { display: flex; gap: 1rem; align-items: center; background: #FFFDF6; border: 1.5px solid var(--ink); border-radius: 20px;
          padding: 1rem 1.2rem; box-shadow: 4px 4px 0 var(--mustard); margin: 1rem 0 .6rem; animation: flip .55s both; }
.reveal img { height: 88px; animation: hop 1.1s ease-in-out 2; }
.reveal .title { font-family: 'Caveat Brush', cursive; font-size: 1.7rem; color: var(--brick); line-height: 1; margin-bottom: .2rem; }

.closed { display: grid; grid-template-columns: auto 1fr; gap: 1.4rem; align-items: center; margin-top: 1rem;
          background: linear-gradient(135deg, var(--card) 0%, var(--mustard-soft) 100%); border: 1.5px solid #EBCF7A;
          border-radius: 24px; padding: 1.2rem 1.6rem; box-shadow: var(--shadow-md); animation: pop .6s both; }
.closed .duo { display: flex; align-items: flex-end; }
.closed .duo .t { height: 190px; animation: hop 1.6s ease-in-out infinite; }
.closed .duo .p { height: 96px; margin-left: -18px; animation: hop 1.6s .25s ease-in-out infinite; }
.closed h4 { font-family: 'Caveat Brush', cursive !important; font-size: 2.2rem !important; margin: 0 0 .3rem !important; color: var(--brick); }

/* ---------- signed-in header ---------- */
.progress-card { background: var(--card); border: 1.5px solid var(--line); border-radius: 22px; padding: 1rem 1.2rem; box-shadow: var(--shadow-sm); }
.progress-card .num { font-family: 'Fraunces', serif; font-weight: 650; font-size: 2.2rem; line-height: 1; }
.progress-card .of { color: var(--ink-soft); font-weight: 700; margin-left: .25rem; }
.meter { height: 14px; border-radius: 999px; background: var(--card-2); border: 1.5px solid var(--ink); overflow: hidden; margin: .55rem 0 .3rem; }
.meter > div { height: 100%; border-radius: 999px; transition: width .8s cubic-bezier(.2,.8,.2,1);
               background: repeating-linear-gradient(-45deg, var(--mustard) 0 10px, #EAC65A 10px 20px); animation: shimmer 1.2s linear infinite; }
.badges { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .5rem; }
.badge { font-size: .72rem; font-weight: 800; border-radius: 999px; padding: .18rem .6rem; border: 1.5px solid var(--line); color: #B2A58F; background: var(--card-2); }
.badge.on { color: var(--ink); background: var(--mustard-soft); border-color: var(--mustard); }
.badge.on::before { content: "★ "; color: var(--brick); }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #F6EBD3 0%, var(--paper) 100%); border-right: 1.5px dashed var(--line); }
.profile { display: flex; align-items: center; gap: .7rem; }
.profile img { height: 58px; animation: bob 3.4s ease-in-out infinite; }
.profile .hi { font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.35rem; line-height: 1; }
.profile .mail { font-size: .8rem; color: var(--ink-soft); word-break: break-all; }
.board { margin-top: 1rem; display: flex; flex-direction: column; gap: .4rem; }
.clue { display: flex; align-items: center; gap: .6rem; background: var(--card); border: 1.5px solid var(--line);
        border-radius: 12px; padding: .45rem .65rem; font-size: .86rem; font-weight: 600; }
.clue .n { width: 1.55rem; height: 1.55rem; border-radius: 8px; display: grid; place-items: center; font-weight: 800; font-size: .78rem;
           background: var(--card-2); border: 1.5px solid var(--line); flex-shrink: 0; }
.clue.solved .n { background: var(--sage); border-color: var(--sage); color: white; }
.clue .p { margin-left: auto; font-size: .72rem; color: var(--ink-soft); font-weight: 800; }

/* ---------- Streamlit widgets ---------- */
.stButton > button, .stFormSubmitButton > button {
  border-radius: 999px; border: 1.5px solid var(--ink); font-weight: 800; padding: .45rem 1.2rem;
  box-shadow: 2px 2px 0 var(--ink); transition: transform .12s ease, box-shadow .12s ease; background: var(--card); color: var(--ink);
}
.stButton > button:hover, .stFormSubmitButton > button:hover { transform: translate(-1px,-1px); box-shadow: 3px 3px 0 var(--ink); border-color: var(--ink); color: var(--ink); }
.stButton > button:active, .stFormSubmitButton > button:active { transform: translate(1px,1px); box-shadow: 0 0 0 var(--ink); }
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] { background: var(--brick) !important; color: #FFF8EC !important; }
[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover { background: var(--brick-dark) !important; color: #FFF8EC !important; }
[data-testid="stBaseButton-tertiary"] { box-shadow: none !important; border: 0 !important; color: var(--ink-soft) !important; text-decoration: underline; }

[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { background: #FFFDF8 !important; }
[data-baseweb="input"] *, [data-baseweb="textarea"] * { background-color: transparent !important; }
[data-testid="stTextArea"] textarea { font-family: 'JetBrains Mono', monospace !important; font-size: .88rem; line-height: 1.6; }
[data-testid="stTextArea"] [data-baseweb="textarea"], [data-testid="stTextInput"] [data-baseweb="input"], [data-baseweb="select"] > div {
  border-radius: 14px !important; border: 1.5px solid var(--line) !important; }
.st-key-editor [data-baseweb="textarea"] { border: 1.5px solid var(--ink) !important; box-shadow: 3px 3px 0 var(--mustard); }
[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within, [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
  border-color: var(--brick) !important; box-shadow: 0 0 0 3px rgba(181,71,58,.14); }

[data-testid="stExpander"] details { border: 1.5px solid var(--line); border-radius: 14px; background: #FFFDF8; }
[data-testid="stExpander"] summary { font-weight: 700; }
[data-testid="stExpander"] summary:hover { color: var(--brick); }
[data-testid="stDataFrame"] { border: 1.5px solid var(--line); border-radius: 14px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 14px; }
[data-testid="stCode"] pre { border-radius: 12px; }

.footer { text-align: center; color: var(--ink-soft); font-size: .82rem; margin-top: 3rem; }
.footer .sig { font-family: 'Caveat', cursive; font-size: 1.3rem; color: var(--ink); }

/* ---------- landing ---------- */
.nav { display: flex; align-items: center; gap: .6rem; }
.st-key-navrow { flex-wrap: nowrap !important; } .st-key-navrow [data-testid="stMarkdown"] { width: auto !important; }
.wordmark { font-family: 'Caveat Brush', cursive; font-size: 1.85rem; color: var(--ink); line-height: 1; }
.wordmark .dot { color: var(--brick); }
.st-key-navsignin button { box-shadow: none !important; border: 1.5px solid var(--line) !important; background: var(--card) !important; }
.st-key-navsignin button:hover { border-color: var(--ink) !important; }

.hero { padding-top: 1.2rem; }
.hero .eyebrow-warm { font-weight: 800; font-size: .74rem; letter-spacing: .18em; text-transform: uppercase; color: var(--brick); }
.hero .logo { margin-top: .5rem; }
.hero .headline { font-family: 'Fraunces', serif; font-weight: 650; font-size: clamp(1.6rem, 3vw, 2.2rem); line-height: 1.15;
                  color: var(--ink); margin: .9rem 0 .5rem; letter-spacing: -.015em; }
.hero .headline em { color: var(--brick); font-style: italic; font-weight: 500; }
.hero .lead { margin-bottom: 1rem; }
.facts { display: flex; flex-wrap: wrap; gap: .45rem; margin: 1.1rem 0 .2rem; }
.fact { display: inline-flex; align-items: center; gap: .4rem; font-size: .82rem; font-weight: 800; color: var(--ink);
        background: var(--card); border: 1.5px solid var(--line); border-radius: 999px; padding: .3rem .75rem; }
.fact i { font-style: normal; width: 8px; height: 8px; border-radius: 50%; background: var(--sage); }
.fact.live i { background: #4C9A5B; box-shadow: 0 0 0 0 rgba(76,154,91,.5); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(76,154,91,.45) } 70% { box-shadow: 0 0 0 8px rgba(76,154,91,0) } 100% { box-shadow: 0 0 0 0 rgba(76,154,91,0) } }
.st-key-herocta button { padding: .7rem 1.6rem !important; font-size: 1.05rem !important; box-shadow: 3px 3px 0 var(--ink) !important; }

.scene { position: relative; height: 520px; display: flex; align-items: flex-end; justify-content: center; padding-top: 8px; }
.scene .halo { position: absolute; bottom: 40px; left: 50%; width: 400px; height: 400px; margin-left: -200px; border-radius: 50%;
               background: radial-gradient(circle, var(--mustard-soft) 0%, rgba(251,237,191,.35) 55%, transparent 70%); }
.scene .paper { position: absolute; bottom: 70px; left: 50%; width: 250px; height: 190px; margin-left: -225px; border-radius: 6px;
                background: #FFFDF6; border: 1.5px solid var(--line); transform: rotate(-6deg); box-shadow: var(--shadow-sm); }
.scene .paper::before { content: "CASE 001"; position: absolute; top: 14px; left: 18px; font-weight: 800; font-size: .66rem; letter-spacing: .2em; color: var(--brick); }
.scene .paper::after { content: ""; position: absolute; top: 40px; left: 18px; right: 40px; height: 70px;
                       background: repeating-linear-gradient(180deg, var(--line) 0 1.5px, transparent 1.5px 14px); }
.scene .ground { position: absolute; bottom: 16px; left: 50%; width: 320px; height: 24px; margin-left: -160px; border-radius: 50%;
                 background: rgba(47,42,40,.10); filter: blur(4px); }
.duo-hero { position: relative; width: 310px; height: 470px; z-index: 2; }
.duo-hero .tali { position: absolute; left: 16px; bottom: 6px; height: 430px; transform-origin: 50% 100%; animation: sway 6s ease-in-out infinite;
                  filter: drop-shadow(0 10px 18px rgba(47,42,40,.12)); }
.duo-hero .pip { position: absolute; left: 138px; bottom: 0; height: 132px; z-index: 3; animation: bob 3.2s ease-in-out infinite; cursor: pointer;
                 filter: drop-shadow(0 8px 10px rgba(47,42,40,.15)); }
.duo-hero .pip:hover { animation: wiggle .5s ease-in-out 2; }
.duo-hero .bubble { position: absolute; left: 142px; top: -4px; width: 166px; z-index: 4; font-size: 1.22rem; animation: pop .6s .5s both; }
.duo-hero .bubble::after { left: 16px; bottom: -9px; }
.scene .spark { z-index: 1; }

.tali-says { display: flex; gap: 1rem; align-items: center; max-width: 760px; margin: 2.4rem auto .4rem; }
.tali-says .avatar { width: 76px; height: 76px; }
.tali-says .bubble { font-size: 1.35rem; flex: 1; }
.tali-says .bubble::after { left: -9px; bottom: auto; top: 50%; margin-top: -8px; border: 0; border-left: 1.5px solid var(--ink); border-bottom: 1.5px solid var(--ink); }

.steps3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.4rem; counter-reset: step; }
.step3 { position: relative; background: var(--card); border: 1.5px solid var(--line); border-radius: 22px; padding: 1.2rem 1.1rem 1.1rem;
         box-shadow: var(--shadow-sm); transition: transform .2s ease, box-shadow .2s ease; animation: fadeUp .5s both; }
.step3:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.step3 .icon { width: 50px; height: 50px; border-radius: 16px; display: grid; place-items: center; font-size: 1.5rem; margin-bottom: .7rem;
               border: 1.5px solid var(--ink); box-shadow: 2px 2px 0 var(--ink); }
.step3:nth-child(1) .icon { background: var(--sage-soft); } .step3:nth-child(2) .icon { background: var(--mustard-soft); } .step3:nth-child(3) .icon { background: var(--blush); }
.step3 .k { font-weight: 800; font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; color: var(--ink-soft); }
.step3 h4 { margin: .1rem 0 .3rem !important; padding: 0 !important; font-size: 1.3rem !important; }
.step3 p { margin: 0; color: var(--ink-soft); font-size: .92rem; line-height: 1.55; }
.step3:not(:last-child)::after { content: "→"; position: absolute; right: -.85rem; top: 50%; transform: translateY(-50%); z-index: 2;
         width: 1.5rem; height: 1.5rem; border-radius: 50%; background: var(--ink); color: var(--paper); display: grid; place-items: center; font-size: .8rem; }

.st-key-featured { position: relative; background: #F3E2BE; border: 1.5px solid #D9C08C; border-radius: 6px 26px 26px 26px;
                   padding: 2rem 2rem 1.6rem; margin-top: 3.2rem; box-shadow: var(--shadow-md); }
.st-key-featured::before { content: "CASE 001"; position: absolute; top: -30px; left: -1.5px; height: 30px; padding: 0 1.2rem; display: grid; place-items: center;
                           background: #F3E2BE; border: 1.5px solid #D9C08C; border-bottom: 0; border-radius: 12px 12px 0 0;
                           font-weight: 800; font-size: .7rem; letter-spacing: .2em; color: var(--brick-dark); }
.case-file .kicker2 { font-weight: 800; font-size: .72rem; letter-spacing: .18em; text-transform: uppercase; color: var(--brick-dark); }
.case-file h3 { font-size: clamp(1.7rem, 3vw, 2.3rem) !important; margin: .2rem 0 .6rem !important; padding: 0 !important; }
.case-file p { color: #4E443D; line-height: 1.7; font-size: 1rem; max-width: 34rem; }
.case-file .stamp2 { display: inline-block; font-family: 'Caveat Brush', cursive; font-size: 1.4rem; color: var(--brick); border: 2.5px solid var(--brick);
                     border-radius: 8px; padding: 0 .6rem; transform: rotate(-6deg); margin-left: .6rem; vertical-align: middle; opacity: .85; }
.case-stats { display: flex; flex-wrap: wrap; gap: .8rem 2.2rem; margin: 1.1rem 0 1.2rem; }
.case-stats b { display: block; font-family: 'Fraunces', serif; font-size: 1.7rem; line-height: 1; color: var(--ink); }
.case-stats span { font-size: .74rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #7A6A58; }
.case-skills { display: flex; flex-wrap: wrap; gap: .35rem; margin-bottom: 1.3rem; }
.case-skills span { font-family: 'JetBrains Mono', monospace; font-size: .74rem; background: rgba(255,253,246,.75); border: 1px solid #D9C08C;
                    border-radius: 6px; padding: .1rem .45rem; }
.case-art { position: relative; width: 300px; max-width: 100%; height: 320px; margin: 0 auto; }
.case-art .string { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }
.case-art .polaroid { position: absolute; top: 6px; right: 6px; width: 176px; padding: 10px 10px 34px; background: #FFFDF6; transform: rotate(5deg);
                      box-shadow: var(--shadow-md); border-radius: 4px; }
.case-art .polaroid div { height: 130px; background: radial-gradient(circle at 50% 70%, var(--mustard-soft), #E9DDC6); display: grid; place-items: center;
                          font-family: 'Caveat Brush', cursive; font-size: 3.4rem; color: rgba(47,42,40,.25); }
.case-art .polaroid span { position: absolute; bottom: 8px; left: 0; right: 0; text-align: center; font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.1rem; }
.case-art .tape { position: absolute; top: -10px; left: 50%; width: 70px; height: 22px; margin-left: -35px; background: rgba(226,185,59,.55); transform: rotate(-4deg); }
.case-art .pipm { position: absolute; left: 0; bottom: 4px; height: 140px; z-index: 3; animation: float 4.5s ease-in-out infinite;
                  filter: drop-shadow(0 8px 10px rgba(47,42,40,.15)); }
.case-art .polaroid { z-index: 2; }
.preview-note { text-align: center; color: var(--ink-soft); font-size: .92rem; margin-top: 3rem; }

[data-testid="stDialog"] [role="dialog"] { background: var(--card); border-radius: 24px; border: 1.5px solid var(--line); }
.dialog-head { display: flex; align-items: center; gap: .8rem; margin-bottom: .4rem; }
.dialog-head img { height: 64px; animation: bob 3.2s ease-in-out infinite; }
.dialog-head p { margin: 0; color: var(--ink-soft); font-size: .9rem; line-height: 1.5; }

@media (max-width: 680px) {
  .steps3 { grid-template-columns: 1fr; } .step3:not(:last-child)::after { content: "↓"; right: 50%; top: auto; bottom: -.95rem; transform: translateX(50%); }
}
@media (max-width: 640px) {
  .scene { height: 410px; } .duo-hero { transform: scale(.86); transform-origin: 50% 100%; }
  .scene .paper { width: 240px; margin-left: -130px; } .scene .halo { width: 320px; height: 320px; margin-left: -160px; }
  .tali-says .bubble { font-size: 1.15rem; } .st-key-featured { padding: 1.5rem 1.1rem 1.2rem; } .case-art { height: 300px; }
}

@media (max-width: 640px) {
  .closed { grid-template-columns: 1fr; } .stage { height: 380px; } .stage .tali { height: 340px; } .stage .pip { height: 110px; left: calc(50% + 50px); }
  .stage .bubble { top: 10px; } .st-key-missioncard { padding: 1.1rem; } .mhead .stamp { position: static; display: inline-block; }
  .mhead { align-items: flex-start; gap: .7rem; flex-wrap: wrap; } .medal { width: 44px; height: 44px; font-size: 1.15rem; border-radius: 12px; }
  .mhead h3 { font-size: 1.3rem !important; } .brief { gap: .7rem; } .brief .avatar, .avatar { width: 56px; height: 56px; }
  .brief .bubble { font-size: .93rem; padding: .6rem .8rem; }
}
"""

_SQL_KEYWORDS = r"\b(SELECT|FROM|WHERE|AND|OR|ORDER BY|GROUP BY|HAVING|LIMIT|JOIN|ON|AS|DESC|ASC|COUNT|SUM|EXTRACT|HOUR)\b"


def inject_css() -> None:
    _render(f"<style>{CSS}</style>")


def _render(markup: str) -> None:
    """Collapse to one line so Markdown never treats indented HTML as a code block."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def inline_md(text: str) -> str:
    """Escape text, then allow **bold**, *italic* and `code` (the only Markdown the quiz copy uses)."""
    text = html.escape(text).replace("$", "&#36;")
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)


def _sql_html(sql: str) -> str:
    """Escaped SQL with keywords highlighted; newlines kept as <br> (the markup is collapsed to one line)."""
    escaped = html.escape(sql)
    escaped = re.sub(_SQL_KEYWORDS, r'<span class="kw">\1</span>', escaped)
    return escaped.replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")


def img(name: str, cls: str = "", alt: str = "") -> str:
    return f'<img src="{IMG.format(name)}" class="{cls}" alt="{html.escape(alt)}">'


# ---------- landing (signed out) ----------

def nav_wordmark() -> None:
    _render('<div class="nav"><span class="wordmark">tali\'s casebook<span class="dot">.</span></span></div>')


def landing_hero() -> None:
    _render("""
    <div class="hero fade-up">
      <span class="eyebrow-warm">Welcome, curious mind</span><br>
      <div class="logo">Tali's Casebook</div>
      <div class="headline">A little mystery. <em>A lot of SQL.</em></div>
      <p class="lead">Something went missing from the roastery overnight. Follow the clues, write real
      queries against a live database, and uncover the story hidden in the data, with Tali &amp; Pip
      at your side.</p>
    </div>""")


def landing_facts() -> None:
    _render("""
    <div class="facts">
      <span class="fact"><i></i>5 missions</span><span class="fact"><i></i>20 points</span>
      <span class="fact live"><i></i>Live PostgreSQL</span><span class="fact"><i></i>About 25 minutes</span>
    </div>""")


def landing_scene(line: str) -> None:
    _render(f"""
    <div class="scene" aria-hidden="true">
      <div class="halo"></div><div class="ground"></div>
      <span class="spark" style="right:12%;top:24%">✦</span>
      <span class="spark" style="left:14%;top:44%;animation-delay:1.1s">✦</span>
      <span class="spark" style="right:22%;top:70%;animation-delay:.6s;font-size:1rem">✦</span>
      <div class="duo-hero">
        {img("tali_smile", "tali", "Tali, the investigator")}
        {img("pip", "pip", "Pip, Tali's companion")}
        <div class="bubble">{html.escape(line)}</div>
      </div>
    </div>""")


def tali_says(line: str) -> None:
    _render(f"""
    <div class="tali-says fade-up">
      <div class="avatar">{img("tali_smile_bust", "", "Tali")}</div>
      <div class="bubble">{html.escape(line)}</div>
    </div>""")


def three_steps() -> None:
    steps = [
        ("🔎", "Step 1", "Investigate", "Read the case notes and follow the clues from the inventory to the vault."),
        ("⌨️", "Step 2", "Query", "Write real SQL against a live PostgreSQL database and see the rows instantly."),
        ("🧩", "Step 3", "Discover", "Connect the evidence, earn all 20 points, and name the person behind the heist."),
    ]
    cards = "".join(
        f'<div class="step3" style="animation-delay:{i * 90}ms"><div class="icon" aria-hidden="true">{icon}</div>'
        f'<span class="k">{k}</span><h4>{t}</h4><p>{d}</p></div>'
        for i, (icon, k, t, d) in enumerate(steps)
    )
    _render(f'<div class="steps3">{cards}</div>')


def featured_case_text(skills: list[str]) -> None:
    chips = "".join(f"<span>{html.escape(s)}</span>" for s in skills)
    _render(f"""
    <div class="case-file">
      <span class="kicker2">Featured case</span>
      <h3>The Roastery Heist <span class="stamp2">OPEN</span></h3>
      <p>Overnight, the roastery's climate vault lost its rarest coffee. No forced entry, no witnesses:
      just five tables of records. Somewhere between the inventory, the shipments and the badge reader,
      the data knows exactly what happened.</p>
      <div class="case-stats">
        <div><b>5</b><span>missions</span></div><div><b>20</b><span>points</span></div>
        <div><b>5</b><span>tables</span></div><div><b>~25</b><span>minutes</span></div>
      </div>
      <div class="case-skills">{chips}</div>
    </div>""")


def featured_case_art() -> None:
    _render(f"""
    <div class="case-art" aria-hidden="true">
      <svg class="string" viewBox="0 0 300 320" preserveAspectRatio="none"><path d="M104 236 C 140 210, 165 196, 192 158"
        fill="none" stroke="#B5473A" stroke-width="2" stroke-dasharray="5 5" stroke-linecap="round"/></svg>
      <div class="polaroid"><span class="tape"></span><div>?</div><span>prime suspect</span></div>
      {img("pip_magnify", "pipm", "Pip with a magnifying glass")}
    </div>""")


def dialog_intro(creating: bool) -> None:
    text = ("Create a free account to save your progress. No email confirmation needed."
            if creating else "Welcome back, detective. Your progress is waiting.")
    _render(f'<div class="dialog-head">{img("pip_magnify", "", "Pip")}<p>{html.escape(text)}</p></div>')


def signed_in_title() -> None:
    _render("""
    <div class="fade-up">
      <span class="kicker"><span class="dot"></span>Investigation in progress</span><br>
      <div class="logo" style="font-size:clamp(2.6rem,5vw,3.7rem)">Tali's Casebook</div>
      <div class="subtitle" style="margin-top:.5rem">Case 001: <em>The Roastery Heist</em></div>
    </div>""")


def progress_card(earned: int, total: int, badges: list[tuple[str, bool]]) -> None:
    pct = round(100 * earned / total)
    chips = "".join(f'<span class="badge{" on" if on else ""}">{html.escape(b)}</span>' for b, on in badges)
    _render(f"""
    <div class="progress-card">
      <span class="eyebrow">Case progress</span><br>
      <span class="num">{earned}</span><span class="of">/ {total} points</span>
      <div class="meter" role="progressbar" aria-valuenow="{earned}" aria-valuemax="{total}"><div style="width:{pct}%"></div></div>
      <div class="badges">{chips}</div>
    </div>""")


# ---------- sections ----------

def section(title: str, subtitle: str = "") -> None:
    sub = f"<p>{inline_md(subtitle)}</p>" if subtitle else ""
    _render(f'<div class="section-head"><h2>{html.escape(title)}</h2>{sub}</div>')


def evidence_grid(schema: dict[str, list[tuple[str, str]]], row_counts: dict[str, int]) -> None:
    cards = []
    for i, (table, columns) in enumerate(schema.items()):
        items = "".join(f'<li><span class="c">{html.escape(c)}</span><span class="t">{html.escape(t)}</span></li>'
                        for c, t in columns)
        count = f'<span class="rows">{row_counts[table]} rows</span>' if table in row_counts else ""
        cards.append(f'<div class="card" style="animation-delay:{i * 70}ms">{count}'
                     f'<div class="name">{html.escape(table)}</div><ul>{items}</ul></div>')
    _render(f'<div class="evidence">{"".join(cards)}</div>')


def case_board(missions, scores: dict[int, int], culprit: str | None) -> None:
    cards = []
    for m in missions:
        if scores.get(m.id, 0) > 0:
            cards.append(f'<div class="clue-card open"><span class="pin"></span><span class="lbl">Clue {m.id}</span>'
                         f'{inline_md(m.clue)}</div>')
        else:
            cards.append(f'<div class="clue-card locked"><div><div class="q">?</div>Solve Mission {m.id} to reveal</div></div>')
    if culprit:
        cards.append(f'<div class="clue-card open suspect"><span class="pin"></span><span class="lbl">Culprit</span>'
                     f'<strong style="font-size:1.1rem">{html.escape(culprit)}</strong><br>Case closed.</div>')
    else:
        cards.append('<div class="clue-card locked"><div><div class="q">?</div>Suspect unknown</div></div>')
    _render(f'<div class="board-grid">{"".join(cards)}</div>')


def case_brief(intro: str) -> None:
    _render(f"""
    <div class="brief">
      <div class="avatar">{img("tali_smile_bust", "", "Tali")}</div>
      <div class="bubble"><span class="who">Tali · case briefing</span>{inline_md(intro)}</div>
    </div>""")


# ---------- mission ----------

def mission_header(number: int, title: str, skill: str, points: int, tables: str, solved: bool) -> None:
    stamp = '<div class="stamp">SOLVED</div>' if solved else ""
    _render(f"""
    <div class="mhead">
      <div class="medal">{number:02d}</div>
      <div>
        <h3>{html.escape(title)}</h3>
        <div class="chips"><span class="chip pts">{points} pts</span><span class="chip skill">{html.escape(skill)}</span>
          <span class="chip">tables: {html.escape(tables)}</span></div>
      </div>
      {stamp}
    </div>""")


def briefing(story: str, instruction: str) -> None:
    _render(f"""
    <div class="brief">
      <div class="avatar">{img("tali_think_bust", "", "Tali thinking")}</div>
      <div class="bubble"><span class="who">Tali</span>{inline_md(story)}</div>
    </div>
    <div class="task"><span class="label">Your task</span>{inline_md(instruction)}</div>""")


def concept_card(title: str, lesson: str, pattern: str) -> None:
    _render(f"""
    <div class="concept">
      <span class="label" style="color:var(--sage)">Concept</span>
      <h4>{html.escape(title)}</h4>
      <p>{inline_md(lesson)}</p>
      <div class="code">{_sql_html(pattern)}</div>
    </div>""")


def column_head(title: str, eyebrow: str) -> None:
    _render(f'<div class="colhead"><span class="t">{html.escape(title)}</span><span class="eyebrow">{html.escape(eyebrow)}</span></div>')


def reaction(kind: str, title: str, message: str, raw: str = "") -> None:
    pic = {"correct": "pip_cheer", "wrong": "pip_magnify", "match": "pip", "locked": "pip"}[kind]
    raw_html = f'<div class="raw">{html.escape(raw)}</div>' if raw else ""
    _render(f"""
    <div class="react {kind}">
      {img(pic, "", "Pip")}
      <div><div class="title">{html.escape(title)}</div><div class="msg">{inline_md(message)}</div>{raw_html}</div>
    </div>""")


def comparison_summary(columns_ok: bool, rows_ok: bool, matched: int, expected: int, returned: int, n_cols: int, want_cols: int) -> None:
    def chip(ok: bool, text: str) -> str:
        return f'<span class="chip {"ok" if ok else "bad"}">{"✓" if ok else "✗"} {html.escape(text)}</span>'
    _render('<div class="summary">'
            + chip(columns_ok, f"Columns {n_cols}/{want_cols}")
            + chip(rows_ok, f"Rows {returned}/{expected}")
            + chip(matched == expected, f"Matching rows {matched}/{expected}")
            + "</div>")


def clue_reveal(number: int, clue: str) -> None:
    _render(f"""
    <div class="reveal">
      {img("pip_cheer", "", "Pip celebrating")}
      <div><div class="title">Clue {number} unlocked</div><div>{inline_md(clue)}</div></div>
    </div>""")


def case_closed(text: str) -> None:
    _render(f"""
    <div class="closed">
      <div class="duo">{img("tali_cheer", "t", "Tali cheering")}{img("pip_cheer", "p", "Pip cheering")}</div>
      <div><h4>Case closed!</h4><div>{inline_md(text)}</div></div>
    </div>""")


# ---------- sidebar ----------

def profile(email: str) -> None:
    _render(f"""
    <div class="profile">
      {img("pip_magnify", "", "Pip")}
      <div><div class="hi">Welcome back, detective</div><div class="mail">{html.escape(email)}</div></div>
    </div>""")


def mission_list(missions: list[tuple[int, str, int, bool]]) -> None:
    clues = "".join(
        f'<div class="clue{" solved" if solved else ""}"><span class="n">{"✓" if solved else n}</span>'
        f'{html.escape(title)}<span class="p">{pts} pts</span></div>'
        for n, title, pts, solved in missions
    )
    _render(f'<div class="board">{clues}</div>')


def footer() -> None:
    _render("""
    <div class="footer">
      <div class="sig">Tali &amp; Pip</div>
      IDS 706 · Supabase PostgreSQL · Supabase Auth · Streamlit
    </div>""")
