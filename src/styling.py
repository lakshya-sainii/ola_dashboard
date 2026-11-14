"""Design tokens + global CSS. One token set drives every page."""
TOKENS = {"bg": "#07080B", "bg2": "#0F1115", "panel": "#14171D", "line": "rgba(255,255,255,.08)",
          "orange": "#FF6A13", "amber": "#F5A524", "ink": "#F4F1EA", "mute": "#9AA0AB",
          "good": "#3DDC97", "bad": "#FF5C5C", "blue": "#5B9DFF"}
FONT = "'Inter','Segoe UI',system-ui,sans-serif"


def css() -> str:
    t = TOKENS
    return f"""
<style>
:root {{ --bg:{t['bg']}; --bg2:{t['bg2']}; --panel:{t['panel']}; --line:{t['line']}; --orange:{t['orange']};
  --amber:{t['amber']}; --ink:{t['ink']}; --mute:{t['mute']}; --good:{t['good']}; --bad:{t['bad']}; --r:14px; --t:.25s; }}
html, body, [data-testid="stAppViewContainer"], .stApp {{ background: radial-gradient(1200px 600px at 80% -10%, #1b120b 0%, var(--bg) 55%); color:var(--ink); font-family:{FONT}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: var(--bg2); border-right:1px solid var(--line); }}
h1,h2,h3,h4 {{ font-family:{FONT}; letter-spacing:-.01em; color:var(--ink); }}
.eyebrow {{ color:var(--orange); font-size:.72rem; letter-spacing:.22em; text-transform:uppercase; font-weight:600; }}
.hero-title {{ font-size:clamp(2rem,5vw,3.6rem); font-weight:800; line-height:1.05; margin:.2rem 0 .4rem; }}
.hero-sub {{ color:var(--mute); max-width:760px; font-size:1.02rem; }}
.kpi {{ background:linear-gradient(180deg,var(--panel),var(--bg2)); border:1px solid var(--line); border-radius:var(--r);
  padding:16px 18px; transition:transform var(--t), border-color var(--t), box-shadow var(--t); min-height:118px; }}
.kpi:hover {{ transform:translateY(-3px); border-color:rgba(255,106,19,.55); box-shadow:0 10px 30px rgba(255,106,19,.12); }}
.kpi .l {{ color:var(--mute); font-size:.74rem; letter-spacing:.08em; text-transform:uppercase; }}
.kpi .v {{ font-size:1.9rem; font-weight:700; font-variant-numeric:tabular-nums; margin:.1rem 0; }}
.kpi .n {{ color:var(--mute); font-size:.76rem; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:var(--r); padding:16px 18px; margin-bottom:12px; }}
.card h4 {{ margin:0 0 6px; font-size:.95rem; color:var(--amber); }}
.tag {{ display:inline-block; font-size:.68rem; padding:2px 8px; border-radius:99px; border:1px solid var(--line); color:var(--mute); margin-right:6px; }}
.tag.hi {{ color:var(--bad); border-color:rgba(255,92,92,.4); }} .tag.mid {{ color:var(--amber); border-color:rgba(245,165,36,.4); }}
.tag.lo {{ color:var(--good); border-color:rgba(61,220,151,.4); }}
.note {{ color:var(--mute); font-size:.85rem; border-left:2px solid var(--orange); padding-left:10px; margin:6px 0 14px; }}
.stButton>button {{ background:linear-gradient(90deg,var(--orange),var(--amber)); color:#120a03; font-weight:700; border:0; border-radius:10px; transition:transform var(--t); }}
.stButton>button:hover {{ transform:translateY(-1px); color:#000; }}
.intro-line {{ height:2px; width:0; background:linear-gradient(90deg,transparent,var(--orange),transparent); animation:grow 1.6s ease forwards; margin:18px 0; }}
.fade {{ opacity:0; animation:fade .9s ease .3s forwards; }}
@keyframes grow {{ to {{ width:100%; }} }} @keyframes fade {{ to {{ opacity:1; }} }}
@media (prefers-reduced-motion: reduce) {{ .intro-line,.fade,.kpi {{ animation:none!important; transition:none!important; opacity:1; width:100%; }} }}
@media (max-width:760px) {{ .kpi .v {{ font-size:1.5rem; }} }}
</style>"""
