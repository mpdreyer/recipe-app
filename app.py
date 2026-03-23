"""
🍳 Mattias Receptsamling — Streamlit App v2
Claude-genererade SVG-matillustrationer + utökad receptinformation
Kör: streamlit run app.py
"""
import streamlit as st
import json, os, re, hashlib
import anthropic

st.set_page_config(page_title="Mattias Receptsamling", page_icon="🍳",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:#FAF7F2;}

.site-header{text-align:center;padding:2.5rem 1rem 0.5rem;border-bottom:2px solid #E2D9CE;margin-bottom:1.5rem;}
.site-header h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.2rem);color:#2C1A0E;margin:0;letter-spacing:-1px;}
.site-header .tagline{font-size:.78rem;letter-spacing:3px;text-transform:uppercase;color:#9B7B5B;margin-top:.4rem;}

.stats-row{display:flex;justify-content:center;gap:2rem;padding:1rem 2rem;background:#2C1A0E;border-radius:12px;margin-bottom:1.5rem;flex-wrap:wrap;}
.stat{text-align:center;}
.stat-n{font-family:'Playfair Display',serif;font-size:2rem;color:#D4A853;line-height:1;display:block;}
.stat-l{font-size:.6rem;letter-spacing:2px;text-transform:uppercase;color:#A89070;margin-top:2px;}

/* Recipe cards */
.recipe-card{background:#fff;border-radius:14px;border:1px solid #E8DDD3;overflow:hidden;transition:transform .22s,box-shadow .22s;margin-bottom:1.5rem;height:100%;}
.recipe-card:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(44,26,14,.13);}
.card-image-wrap{position:relative;overflow:hidden;}
.card-image-wrap img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;transition:transform .3s;}
.card-image-wrap:hover img{transform:scale(1.04);}
.card-img-ph{width:100%;aspect-ratio:4/3;background:linear-gradient(135deg,#F0E8DF,#D4C5B3);display:flex;align-items:center;justify-content:center;font-size:3.5rem;}
.card-difficulty{position:absolute;top:.6rem;right:.6rem;background:rgba(44,26,14,.75);color:#FAF0E6;border-radius:6px;padding:.2rem .5rem;font-size:.65rem;font-weight:500;letter-spacing:1px;text-transform:uppercase;}
.card-body{padding:.9rem 1.1rem 1.1rem;}
.card-cat{font-size:.62rem;font-weight:500;letter-spacing:2.5px;text-transform:uppercase;color:#B85C2A;margin-bottom:.3rem;}
.card-title{font-family:'Playfair Display',serif;font-size:1rem;font-weight:600;color:#2C1A0E;line-height:1.3;margin-bottom:.4rem;}
.card-desc{font-size:.78rem;color:#7A6252;line-height:1.5;margin-bottom:.5rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.card-meta{display:flex;flex-wrap:wrap;gap:.4rem;font-size:.7rem;color:#8B6F55;margin-bottom:.4rem;}
.card-meta-item{display:flex;align-items:center;gap:.2rem;}
.card-creator{font-size:.68rem;color:#6B8C5A;font-weight:500;margin-top:.3rem;}
.tag{display:inline-block;background:#FAF0E6;border:1px solid #E2D0BC;color:#7A5C3A;border-radius:20px;padding:.1rem .5rem;font-size:.62rem;margin:.1rem .1rem 0 0;}

/* Detail view */
.detail-header{border-bottom:2px solid #E2D9CE;padding-bottom:1.2rem;margin-bottom:1.5rem;}
.detail-header h2{font-family:'Playfair Display',serif;font-size:2rem;color:#2C1A0E;margin:0 0 .3rem;}
.detail-cat{font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:#B85C2A;}
.meta-pill{display:inline-block;background:#2C1A0E;color:#FAF0E6;border-radius:6px;padding:.35rem .8rem;font-size:.73rem;font-weight:500;margin:.2rem .2rem 0 0;}
.meta-pill.highlight{background:#B85C2A;}
.ing-line{padding:.45rem 0;border-bottom:1px solid #F0E8DF;font-size:.87rem;color:#3A2510;display:flex;align-items:flex-start;gap:.5rem;}
.ing-line:last-child{border-bottom:none;}
.step-block{background:#FAF7F2;border-left:3px solid #D4A853;padding:.65rem .9rem;border-radius:0 8px 8px 0;margin-bottom:.5rem;font-size:.87rem;color:#3A2510;line-height:1.6;}
.step-num{color:#D4A853;font-weight:700;margin-right:.3rem;}
.nutrition-box{background:#2C1A0E;border-radius:10px;padding:1rem 1.2rem;color:#FAF0E6;margin-top:1rem;}
.nutrition-box h4{font-family:'Playfair Display',serif;color:#D4A853;margin:0 0 .6rem;font-size:1rem;}
.nut-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;}
.nut-item{text-align:center;}
.nut-val{font-size:1.1rem;font-weight:600;color:#D4A853;display:block;}
.nut-lbl{font-size:.6rem;letter-spacing:1px;text-transform:uppercase;color:#A89070;}
.pro-tip{background:#FFF8F0;border:1px solid #E8D8C0;border-left:4px solid #D4A853;border-radius:0 8px 8px 0;padding:.7rem 1rem;margin:.5rem 0;font-size:.85rem;color:#5A3820;font-style:italic;}
.instagram-btn{display:inline-flex;align-items:center;gap:.4rem;background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);color:white;border-radius:8px;padding:.4rem .9rem;font-size:.78rem;font-weight:500;text-decoration:none;margin-top:.5rem;}
.similar-card{background:#fff;border:1px solid #E8DDD3;border-radius:10px;padding:.7rem;display:flex;align-items:center;gap:.6rem;margin-bottom:.5rem;cursor:pointer;transition:background .2s;}
.similar-card:hover{background:#FAF0E6;}
.similar-emoji{font-size:1.8rem;}
.similar-info small{color:#9B7B5B;font-size:.7rem;}

/* Sidebar */
[data-testid="stSidebar"]{background:#2C1A0E !important;}
[data-testid="stSidebar"] *{color:#E8DDD3 !important;}
[data-testid="stSidebar"] .stTextInput input{background:#3D2510 !important;border:1px solid #5A3820 !important;color:#F0E8DF !important;border-radius:8px !important;}
[data-testid="stSidebar"] .stSelectbox > div > div{background:#3D2510 !important;border:1px solid #5A3820 !important;}
[data-testid="stSidebar"] label{color:#D4A853 !important;font-size:.7rem !important;letter-spacing:1.5px !important;text-transform:uppercase !important;}
[data-testid="stSidebar"] .stMultiSelect > div > div{background:#3D2510 !important;border:1px solid #5A3820 !important;}

.stButton>button{background:#2C1A0E !important;color:#FAF0E6 !important;border:none !important;border-radius:8px !important;font-size:.8rem !important;font-weight:500 !important;transition:background .2s !important;}
.stButton>button:hover{background:#B85C2A !important;}

/* Search bar */
.search-wrap input{background:#fff !important;border:2px solid #E2D9CE !important;border-radius:10px !important;font-size:.9rem !important;}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
EMOJI = {"Förrätt":"🥗","Frukost":"🍳","Huvudrätt":"🍽️","Dessert":"🍰",
         "Bakverk":"🎂","Snacks":"🧀","Tillbehör":"🥔","Sås":"🫙","Dryck":"🥂","Övrigt":"🍴"}

DIFFICULTY_COLOR = {"Lätt":"#4CAF50", "Medel":"#FF9800", "Avancerad":"#F44336"}

# Fallback-näringsvärden (används om recipe["nutrition"] saknas)
NUTRITION_FALLBACKS = {
    "Varmrätt":  {"kcal": "490", "protein": "34g", "kolhydrat": "40g", "fett": "19g"},
    "Huvudrätt": {"kcal": "490", "protein": "34g", "kolhydrat": "40g", "fett": "19g"},
    "Förrätt":   {"kcal": "185", "protein": "10g", "kolhydrat": "14g", "fett": "10g"},
    "Dessert":   {"kcal": "340", "protein": "5g",  "kolhydrat": "48g", "fett": "14g"},
    "Bakverk":   {"kcal": "290", "protein": "5g",  "kolhydrat": "42g", "fett": "12g"},
    "Snacks":    {"kcal": "210", "protein": "8g",  "kolhydrat": "18g", "fett": "13g"},
    "Frukost":   {"kcal": "390", "protein": "16g", "kolhydrat": "50g", "fett": "14g"},
    "Tillbehör": {"kcal": "180", "protein": "3g",  "kolhydrat": "26g", "fett": "7g"},
    "Sås":       {"kcal": "95",  "protein": "1g",  "kolhydrat": "4g",  "fett": "8g"},
    "Dryck":     {"kcal": "140", "protein": "0g",  "kolhydrat": "14g", "fett": "0g"},
}

PRO_TIPS = {
    "Carbonara": "Nyckeln är att aldrig lägga pasta i het panna med ägg — residualvärmen räcker för perfekt krämig konsistens.",
    "Cacio e Pepe": "Rosta svartpepparn torrt innan — det aktiverar oljorna och ger djupare, mer komplex smak.",
    "Tiramisù": "Doppa ladyfingers max 1-2 sekunder — annars blir de mosiga. De ska fortfarande ha lite bett.",
    "kladdkaka": "Baka alltid kortare tid än du tror. En sann kladdkaka ska darra mitt i när du tar ut den.",
    "Lasagna": "Lägg råa pastaplåtar direkt — ingen förgräddning behövs. De absorberar vätskan från ragùn.",
    "Gravlax": "Salt/socker-förhållandet 1:1 ger klassisk smak. Vill du ha sötare, öka sockret till 1.5:1.",
    "Smash Burger": "Pressa KUN en gång och HÅRT. Det är Maillard-reaktionen mot stekplattans yta som ger smaken.",
    "Brisket": "Vila ALLTID i minst 2 timmar inlindad. Temperaturen omfördelas och köttet blir saftigare.",
    "Pulled Pork": "Intern temperatur 90-95°C är målet, inte tid. Varje bit kött är annorlunda.",
    "Hollandaise": "Häll smöret i en OTROligt tunn stråle under konstant vispning för perfekt emulsion.",
}

def get_pro_tip(recipe):
    title = recipe.get('title','').lower()
    for key, tip in PRO_TIPS.items():
        if key.lower() in title:
            return tip
    return None

# ── Claude API client ─────────────────────────────────────────────────────────
def _get_api_key() -> str:
    """Hämtar API-nyckel — INGEN st.secrets (kraschar om toml saknas)."""
    # 1. Miljövariabel (kör: export ANTHROPIC_API_KEY=sk-ant-...)
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # 2. .env-filer — letar i projektmapp, hemkatalog och dreyer-council
    env_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.expanduser("~/.env"),
        os.path.expanduser("~/dreyer-council/.env"),
    ]
    for path in env_paths:
        if os.path.exists(path):
            try:
                for line in open(path):
                    s = line.strip()
                    if s.startswith("ANTHROPIC_API_KEY") and "=" in s:
                        k = s.split("=", 1)[1].strip().strip(chr(34)+chr(39))
                        if k:
                            return k
            except Exception:
                pass
    return ""

@st.cache_resource
def get_claude_client():
    key = _get_api_key()
    if not key:
        return None
    return anthropic.Anthropic(api_key=key)

# ── SVG Illustration generator ────────────────────────────────────────────────
SVG_SYSTEM = """Du är en matillustratör som ritar SVG-skisser av maträtter. Skapa vackra, stiliserade illustrationer.

TEKNISKA KRAV (följ EXAKT):
- Öppna med: <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
- Bakgrund: <rect width="400" height="300" fill="#FAF7F2"/>
- Alltid en tallrik/skål som grund med skugga under
- Skugga: <ellipse cx="200" cy="272" rx="135" ry="14" fill="#E2D9CE" opacity="0.5"/>

FÄRGPALETT (bara dessa):
#FAF7F2 bakgrund | #FFFFFF tallrik | #E8DDD3 tallrik-kant/skugga
#C4622D röd/tomat/paprika | #D4A853 guld/pasta/ost/smör | #6B8C5A grönt/örter/sallad
#8B4513 brun/kött/choklad/kaffe | #F5DEB3 ljus/bröd/deg/kex | #2C1A0E mörkbrun/kontur
#FF6B6B ljusröd | #FFD700 gul/ägg | #87CEEB ljusblå/skaldjur | #DEB887 beige/potatis

DESIGNREGLER:
- Rita 5-8 igenkänningsbara matelement ovanpå tallriken
- Använd enkla former: cirklar, ellipser, rektanglar med rundade hörn, enkla paths
- Lägg till detaljer: ånglinjer (böjda paths, opacity 0.3), garneringar
- Variera storleken på element för djup
- INGA externa resurser, INGEN JavaScript, INGA fonter
- Returnera BARA ren SVG-kod utan ```-backticks eller förklaringar"""

@st.cache_data(show_spinner=False, ttl=86400*30)  # Cache 30 dagar
def generate_illustration(recipe_url: str, title: str, category: str, 
                          ingredients_str: str, tags_str: str) -> str:
    """Generera SVG-illustration med Claude Haiku. Cachas per recept-URL."""
    client = get_claude_client()
    if not client:
        return _fallback_svg(title, category)
    
    prompt = f"""Rita en vacker matillustration av: {title}
Kategori: {category}
Nyckelingredienser: {ingredients_str}
Taggar: {tags_str}

Skapa en aptitlig och igenkännbar SVG-skiss. Rita det som är mest karakteristiskt för rätten."""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2500,
            system=SVG_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        svg = resp.content[0].text.strip()
        svg = re.sub(r'^```(svg|xml)?\s*', '', svg, flags=re.IGNORECASE)
        svg = re.sub(r'\s*```$', '', svg)
        # Säkerhetskoll — måste börja med <svg
        if not svg.strip().startswith('<svg'):
            return _fallback_svg(title, category)
        return svg
    except Exception as e:
        return _fallback_svg(title, category)

def _fallback_svg(title: str, category: str) -> str:
    """Enkel fallback-illustration om API ej tillgänglig."""
    emoji_map = {"Huvudrätt":"🍽","Förrätt":"🥗","Dessert":"🍰","Bakverk":"🎂",
                 "Snacks":"🧀","Frukost":"🍳","Tillbehör":"🥔","Sås":"🫙"}
    emoji = emoji_map.get(category, "🍴")
    short = (title[:22] + "…") if len(title) > 24 else title
    return f"""<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FAF7F2"/>
  <ellipse cx="200" cy="272" rx="135" ry="14" fill="#E2D9CE" opacity="0.5"/>
  <circle cx="200" cy="148" r="120" fill="white" stroke="#E8DDD3" stroke-width="2"/>
  <circle cx="200" cy="148" r="100" fill="#FFF8F0" stroke="#F0E8DF" stroke-width="1"/>
  <text x="200" y="130" text-anchor="middle" font-size="52">{emoji}</text>
  <text x="200" y="185" text-anchor="middle" font-size="13" fill="#9B7B5B" font-family="Georgia,serif">{short}</text>
</svg>"""

def get_illustration(recipe: dict) -> str:
    """Hämta eller generera illustration för ett recept."""
    url = recipe.get('url', recipe.get('title',''))
    title = recipe.get('title', '')
    category = recipe.get('category', '')
    ings = ', '.join((recipe.get('ingredients') or [])[:6])
    tags = ', '.join((recipe.get('tags') or [])[:4])
    return generate_illustration(url, title, category, ings, tags)

def svg_to_data_uri(svg: str) -> str:
    """Konvertera SVG till data URI för img-taggar."""
    import base64
    encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded}"

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_recipes():
    p = os.path.join(os.path.dirname(__file__), "recipes_extracted.json")
    if not os.path.exists(p):
        return []
    return [r for r in json.load(open(p, encoding="utf-8")) if r.get("is_recipe")]

def filter_recipes(recipes, search, cats, cuisines, diffs, max_time):
    if cats and "Alla" not in cats:
        recipes = [r for r in recipes if r.get("category") in cats]
    if cuisines and "Alla" not in cuisines:
        recipes = [r for r in recipes if r.get("cuisine") in cuisines]
    if diffs and "Alla" not in diffs:
        recipes = [r for r in recipes if r.get("difficulty") in diffs]
    if max_time < 120:
        def total_min(r):
            def parse(t):
                if not t: return 0
                n = re.search(r'\d+', str(t))
                return int(n.group()) if n else 0
            return parse(r.get('prep_time')) + parse(r.get('cook_time'))
        recipes = [r for r in recipes if total_min(r) <= max_time]
    if search:
        s = search.lower()
        recipes = [r for r in recipes if
            s in (r.get("title","")).lower() or
            s in (r.get("description","")).lower() or
            s in (r.get("creator","")).lower() or
            any(s in t.lower() for t in (r.get("tags") or [])) or
            any(s in i.lower() for i in (r.get("ingredients") or []))]
    return recipes

def similar_recipes(recipe, all_recipes, n=4):
    """Hitta liknande recept baserat på kategori, kök och taggar."""
    cat = recipe.get('category','')
    cui = recipe.get('cuisine','')
    tags = set(recipe.get('tags') or [])
    url = recipe.get('url','')
    
    scored = []
    for r in all_recipes:
        if r.get('url') == url: continue
        score = 0
        if r.get('category') == cat: score += 3
        if r.get('cuisine') == cui: score += 2
        common_tags = tags & set(r.get('tags') or [])
        score += len(common_tags)
        if score > 0:
            scored.append((score, r))
    
    scored.sort(key=lambda x: -x[0])
    return [r for _, r in scored[:n]]

# ── Card HTML ──────────────────────────────────────────────────────────────────
def card_html(r: dict, svg: str) -> str:
    cat = r.get("category",""); cui = r.get("cuisine","")
    cat_line = " · ".join(filter(None,[cat,cui]))
    tags = "".join(f'<span class="tag">{t}</span>' for t in (r.get("tags") or [])[:3])
    diff = r.get("difficulty","")
    diff_badge = f'<div class="card-difficulty">{diff}</div>' if diff else ""

    meta_parts = []
    if r.get("prep_time"): meta_parts.append(f'<span class="card-meta-item">⏱ {r["prep_time"]}</span>')
    if r.get("cook_time"): meta_parts.append(f'<span class="card-meta-item">🔥 {r["cook_time"]}</span>')
    if r.get("servings"):  meta_parts.append(f'<span class="card-meta-item">👥 {r["servings"]}</span>')
    meta = "".join(meta_parts)

    creator = r.get("creator","")
    svg_uri = svg_to_data_uri(svg)
    return f"""
<div class="recipe-card">
  <div class="card-image-wrap">
    <img src="{svg_uri}" alt="{r.get('title','')}" style="width:100%;aspect-ratio:4/3;object-fit:cover;display:block"/>
    {diff_badge}
  </div>
  <div class="card-body">
    <div class="card-cat">{cat_line}</div>
    <div class="card-title">{r.get('title','Recept')}</div>
    <div class="card-desc">{(r.get('description') or '')[:110]}</div>
    {"<div class='card-meta'>"+meta+"</div>" if meta else ""}
    {"<div class='card-creator'>@"+creator+"</div>" if creator else ""}
    <div style='margin-top:.4rem'>{tags}</div>
  </div>
</div>"""

# ── Detail view ────────────────────────────────────────────────────────────────
def show_detail(recipe: dict, all_recipes: list):
    cat = recipe.get("category",""); cui = recipe.get("cuisine","")
    cat_line = " · ".join(filter(None,[cat,cui]))

    # Header
    st.markdown(f"""
    <div class="detail-header">
      <div class="detail-cat">{cat_line}</div>
      <h2>{recipe.get('title','Recept')}</h2>
      {"<p style='color:#7A6252;font-size:.9rem;margin:.3rem 0 0;font-style:italic'>"+recipe['description']+"</p>" if recipe.get('description') else ""}
    </div>""", unsafe_allow_html=True)

    col_img, col_info = st.columns([1.2, 1.8])

    with col_img:
        # Generera SVG-illustration
        with st.spinner("Genererar illustration…"):
            svg = get_illustration(recipe)
        svg_uri = svg_to_data_uri(svg)
        st.markdown(f"""
        <div style="border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(44,26,14,.15);background:#FAF7F2">
          <img src="{svg_uri}" style="width:100%;display:block"/>
        </div>""", unsafe_allow_html=True)

        # Instagram link
        url = recipe.get("url","")
        creator = recipe.get("creator","")
        if url and creator:
            st.markdown(f'<a href="{url}" target="_blank" class="instagram-btn">📸 Se på Instagram @{creator}</a>',
                       unsafe_allow_html=True)

        # Nutrition estimate
        # Näringsvärden — per portion OCH per 100g
        raw_nut = recipe.get('nutrition') or {}
        fb = NUTRITION_FALLBACKS.get(cat, NUTRITION_FALLBACKS.get("Varmrätt", {}))
        is_calc = raw_nut.get('calculated', False)

        # Stöd både nytt format (per_portion/per_100g) och gammalt (flat)
        if 'per_portion' in raw_nut:
            pp  = raw_nut['per_portion']
            p100 = raw_nut['per_100g']
            pg  = raw_nut.get('portion_g')
        elif raw_nut.get('kcal'):
            pp = raw_nut
            p100 = fb.get('per_100g', {})
            pg = None
        else:
            pp   = fb.get('per_portion', fb)
            p100 = fb.get('per_100g', {})
            pg   = None
            is_calc = False

        portion_label = f"Per portion ({pg}g)" if pg else "Per portion"
        calc_note = "" if is_calc else '<div style="font-size:.61rem;color:#A89070;opacity:.8;margin-top:.35rem">⚠️ Uppskattning baserad på kategori</div>'

        st.markdown(f"""
        <div class="nutrition-box">
          <h4>📊 Näringsvärde</h4>
          <div style="font-size:.65rem;letter-spacing:1px;text-transform:uppercase;color:#D4A853;margin-bottom:.4rem">{portion_label}</div>
          <div class="nut-grid">
            <div class="nut-item"><span class="nut-val">{pp.get("kcal","–")}</span><span class="nut-lbl">kcal</span></div>
            <div class="nut-item"><span class="nut-val">{pp.get("protein","–")}</span><span class="nut-lbl">Protein</span></div>
            <div class="nut-item"><span class="nut-val">{pp.get("kolhydrat","–")}</span><span class="nut-lbl">Kolhydrat</span></div>
            <div class="nut-item"><span class="nut-val">{pp.get("fett","–")}</span><span class="nut-lbl">Fett</span></div>
          </div>
          <div style="border-top:1px solid rgba(255,255,255,.15);margin:.55rem 0 .4rem"></div>
          <div style="font-size:.65rem;letter-spacing:1px;text-transform:uppercase;color:#A89070;margin-bottom:.4rem">Per 100g</div>
          <div class="nut-grid">
            <div class="nut-item"><span class="nut-val" style="font-size:.9rem">{p100.get("kcal","–")}</span><span class="nut-lbl">kcal</span></div>
            <div class="nut-item"><span class="nut-val" style="font-size:.9rem">{p100.get("protein","–")}</span><span class="nut-lbl">Protein</span></div>
            <div class="nut-item"><span class="nut-val" style="font-size:.9rem">{p100.get("kolhydrat","–")}</span><span class="nut-lbl">Kolhydrat</span></div>
            <div class="nut-item"><span class="nut-val" style="font-size:.9rem">{p100.get("fett","–")}</span><span class="nut-lbl">Fett</span></div>
          </div>
          {calc_note}
        </div>""", unsafe_allow_html=True)

    with col_info:
        # Meta pills
        pills = ""
        meta_items = [
            ("⏱️","Förberedelsetid", recipe.get("prep_time")),
            ("🔥","Tillagningstid", recipe.get("cook_time")),
            ("👥","Portioner", recipe.get("servings")),
            ("📊","Svårighet", recipe.get("difficulty")),
            ("🌍","Kök", recipe.get("cuisine")),
        ]
        for icon, label, val in meta_items:
            if val:
                color = "highlight" if label == "Svårighet" else ""
                pills += f'<span class="meta-pill {color}" title="{label}">{icon} {val}</span>'
        if pills:
            st.markdown(pills, unsafe_allow_html=True)
            st.write("")

        # Tags
        tags = recipe.get("tags") or []
        if tags:
            st.markdown("**Taggar:** " + " ".join(f"`{t}`" for t in tags))
            st.write("")

        # Pro tip
        tip = get_pro_tip(recipe)
        if tip:
            st.markdown(f'<div class="pro-tip">💡 <strong>Proffstips:</strong> {tip}</div>',
                       unsafe_allow_html=True)

        # Ingredients
        st.markdown("### 🛒 Ingredienser")
        ings = recipe.get("ingredients") or []
        if ings:
            ing_html = "".join(f'<div class="ing-line">✓ {i}</div>' for i in ings)
            st.markdown(ing_html, unsafe_allow_html=True)
        else:
            st.markdown("*Se originalinlägget på Instagram.*")

    # Instructions — full width
    st.markdown("---")
    inst = recipe.get("instructions","")
    if inst:
        st.markdown("### 👨‍🍳 Tillagning steg för steg")
        parts = [p.strip() for p in re.split(r'(?=\d+\.)', inst.strip()) if p.strip()]
        if len(parts) > 1:
            cols = st.columns(min(len(parts), 3))
            for i, (col, step) in enumerate(zip(cols * 10, parts)):
                with col:
                    # Extract step number
                    num_match = re.match(r'(\d+)\.(.+)', step, re.DOTALL)
                    if num_match:
                        num, text = num_match.group(1), num_match.group(2).strip()
                        st.markdown(f'<div class="step-block"><span class="step-num">Steg {num}</span>{text}</div>',
                                   unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="step-block">{step}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="step-block">{inst}</div>', unsafe_allow_html=True)

    # Similar recipes
    st.markdown("---")
    st.markdown("### 🍽️ Du kanske också gillar")
    sims = similar_recipes(recipe, all_recipes)
    if sims:
        sim_cols = st.columns(len(sims))
        for col, sim in zip(sim_cols, sims):
            with col:
                sim_svg = _fallback_svg(sim.get('title',''), sim.get('category',''))
                sim_uri = svg_to_data_uri(sim_svg)
                sim_cat = sim.get('category','')
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #E8DDD3;border-radius:10px;overflow:hidden;cursor:pointer;transition:transform .2s"
                     onmouseover="this.style.transform='translateY(-3px)'"
                     onmouseout="this.style.transform=''">
                  <img src="{sim_uri}" style="width:100%;aspect-ratio:3/2;object-fit:cover;display:block"/>
                  <div style="padding:.6rem .8rem">
                    <div style="font-size:.6rem;color:#B85C2A;text-transform:uppercase;letter-spacing:1.5px">{sim_cat}</div>
                    <div style="font-family:'Playfair Display',serif;font-size:.9rem;color:#2C1A0E;line-height:1.3">{sim.get('title','')}</div>
                    <div style="font-size:.7rem;color:#6B8C5A;margin-top:.2rem">@{sim.get('creator','')}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button("Öppna", key=f"sim_{sim.get('url','')[-8:]}_{sim.get('title','')[:8]}", use_container_width=True):
                    st.session_state.sel = sim
                    st.rerun()

    st.markdown("---")
    if st.button("← Tillbaka till alla recept", key="back"):
        st.session_state.sel = None
        st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────────
def fetch_instagram_caption(url: str) -> tuple[str, str]:
    """Hämta caption + creator från Instagram-post via og:description."""
    import urllib.request, urllib.error, html as html_mod
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        # og:description
        import re as _re
        m = _re.search(r'property="og:description" content="([^"]+)"', html)
        caption = html_mod.unescape(m.group(1)) if m else ""
        # creator från "comments - HANDLE "
        cm = _re.search(r'comments - ([a-zA-Z0-9_.]+) ', caption)
        creator = cm.group(1) if cm else ""
        if not creator:
            cm2 = _re.search(r'"username":"([^"]+)"', html)
            creator = cm2.group(1) if cm2 else ""
        return caption, creator
    except Exception as e:
        return "", str(e)


def extract_recipe_from_caption(caption: str, url: str, creator: str) -> dict | None:
    """Kör Claude Haiku på captionen och returnera strukturerat recept."""
    client = get_claude_client()
    if not client:
        return None

    SYSTEM = """Du analyserar Instagram-captions och extraherar matrecept.
Returnera BARA giltig JSON utan backticks.

Om det är ett recept:
{"is_recipe":true,"title":"...","description":"...","ingredients":["..."],
 "instructions":"...","category":"Varmrätt/Förrätt/Dessert/Bakverk/Snacks/Frukost/Tillbehör/Sås/Dryck",
 "cuisine":"Svensk/Italiensk/Asiatisk/Franskt/Övrigt/Dryck",
 "difficulty":"Lätt/Medel/Avancerad","servings":"...","prep_time":"...","cook_time":"...","tags":["..."]}

Om det INTE är ett recept: {"is_recipe":false}"""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=SYSTEM,
            messages=[{"role": "user", "content": f"Caption:\n{caption[:1500]}"}]
        )
        import json as _json, re as _re
        text = resp.content[0].text.strip()
        text = _re.sub(r'^```(json)?', '', text).strip().rstrip('`').strip()
        data = _json.loads(text)
        if data.get("is_recipe"):
            data["url"] = url
            data["creator"] = creator
            data["jenny_pick"] = True
            data["added_by"] = "instagram_import"
            data["is_recipe"] = True
        return data
    except Exception as e:
        return {"is_recipe": False, "error": str(e)}


def save_recipe_to_file(recipe: dict) -> bool:
    """Spara nytt recept till recipes_extracted.json."""
    import json as _json, sys as _sys
    _sys.path.insert(0, '.')
    try:
        from nutrition_engine import calculate_nutrition, NUTRITION_FALLBACKS
        nutrition = calculate_nutrition(recipe)
        if nutrition:
            recipe['nutrition'] = nutrition
        else:
            fb = NUTRITION_FALLBACKS.get(recipe.get('category','Varmrätt'),
                                          NUTRITION_FALLBACKS.get('Varmrätt',{}))
            recipe['nutrition'] = {**fb, 'calculated': False}
    except Exception:
        pass

    path = "recipes_extracted.json"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            recipes = _json.load(f)
    except Exception:
        recipes = []

    # Dubblettcheck på URL
    existing_urls = {r.get('url','') for r in recipes}
    if recipe.get('url','') in existing_urls:
        return False

    recipes.append(recipe)
    with open(path, 'w', encoding='utf-8') as f:
        _json.dump(recipes, f, ensure_ascii=False, indent=2)
    return True


def show_add_recipe_page():
    """Sida för att lägga till recept från Instagram-URL."""
    import re as _re

    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem'>
      <div style='font-family:"Playfair Display",serif;font-size:2.2rem;color:#1C1208'>
        📲 Lägg till recept
      </div>
      <div style='font-size:.9rem;color:#6B5B45;margin-top:.4rem;letter-spacing:1px;text-transform:uppercase'>
        Från Instagram direkt till receptsamlingen
      </div>
    </div>""", unsafe_allow_html=True)

    # ── URL-input ──────────────────────────────────────────────────────────────
    st.markdown("### 1. Klistra in Instagram-URL")
    url = st.text_input("", placeholder="https://www.instagram.com/p/ABC123/",
                        label_visibility="collapsed", key="ig_url_input")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        fetch_btn = st.button("🔍 Hämta recept", use_container_width=True, type="primary")

    if fetch_btn and url:
        url = url.strip().split("?")[0]
        if not _re.match(r'https?://(www\.)?instagram\.com/(p|reel)/', url):
            st.error("⚠️ Verkar inte vara en giltig Instagram-URL. Försök med t.ex. https://www.instagram.com/p/ABC123/")
            return

        with st.spinner("Hämtar caption från Instagram..."):
            caption, creator = fetch_instagram_caption(url)

        if not caption:
            st.error("❌ Kunde inte hämta captionen. Kontrollera att länken är publik.")
            return

        with st.spinner("Claude extraherar receptet..."):
            recipe = extract_recipe_from_caption(caption, url, creator)

        if not recipe or not recipe.get("is_recipe"):
            st.warning("🤔 Hittade inget recept i det här inlägget. Prova ett annat!")
            with st.expander("Visa caption"):
                st.text(caption[:500])
            return

        # ── Förhandsgranska ────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 2. Förhandsgranska")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Titel:** {recipe.get('title','?')}")
            st.markdown(f"**@kreatör:** {recipe.get('creator','?')}")
            st.markdown(f"**Kategori:** {recipe.get('category','?')} · {recipe.get('cuisine','?')}")
            st.markdown(f"**Svårighet:** {recipe.get('difficulty','?')}")
            st.markdown(f"**Tid:** {recipe.get('prep_time','?')} prep + {recipe.get('cook_time','?')} tillagning")
        with c2:
            ings = recipe.get('ingredients', [])
            st.markdown(f"**{len(ings)} ingredienser:**")
            for i in ings[:6]:
                st.markdown(f"• {i}")
            if len(ings) > 6:
                st.markdown(f"*…och {len(ings)-6} till*")

        st.markdown(f"**Beskrivning:** {recipe.get('description','')}")

        # Spara-knapp
        st.markdown("---")
        st.markdown("### 3. Spara till samlingen")

        # Låt användaren välja om det är Jennys val
        jenny = st.checkbox("👩 Markera som Jennys val", value=True)
        recipe['jenny_pick'] = jenny

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            save_btn = st.button("💾 Spara recept", use_container_width=True, type="primary")

        if save_btn:
            saved = save_recipe_to_file(recipe)
            if saved:
                st.success(f"✅ **{recipe['title']}** sparad i receptsamlingen!")
                st.balloons()
                st.info("💡 Receptet syns direkt i appen — tryck 'Receptsamlingen' i menyn!")
            else:
                st.warning("⚠️ Det här receptet finns redan i samlingen (samma URL).")

    # ── iOS Shortcut-sektion ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📱 iOS Shortcut — Share direkt från Instagram")
    st.markdown("""
    Lägg till denna shortcut på din iPhone — sedan kan du och Jenny trycka
    **Share → Receptsamlingen** direkt i Instagram!
    """)

    # Hämta app-URL dynamiskt
    try:
        app_url = st.query_params.get("_streamlit_origin", "https://recipe-app-dreyer.streamlit.app")
    except Exception:
        app_url = "https://recipe-app-dreyer.streamlit.app"

    shortcut_url = f"{app_url}?add_recipe={{Input}}"

    with st.expander("🔧 Hur man installerar iOS Shortcut (3 steg)", expanded=True):
        st.markdown(f"""
**Steg 1 — Öppna Shortcuts-appen** på din iPhone

**Steg 2 — Skapa ny shortcut** med dessa åtgärder:
1. `Receive` → **Share Sheet** → Allow **Safari web URLs**
2. `URL` → `{app_url}?ig_url=` + **Shortcut Input**
3. `Open URL` i **Safari**

**Steg 3 — Namnge den** "Lägg till recept" och lägg till på hemskärmen

---
**Eller** — använd denna direktlänk för att installera färdig shortcut:
""")

        # Generera iCloud Shortcut-länk
        st.code(f"""
Shortcut-namn: Lägg till recept
Åtgärder:
1. Receive input from Share Sheet (Safari URLs)  
2. Open URL: {app_url}?ig_url=[Shortcut Input]
        """, language="text")

        st.markdown("""
> **Tips:** I Instagram — tryck på **···** (tre punkter) på ett inlägg →
> **Share to** → **Lägg till recept** → appen öppnas med receptet redo att spara!
""")


def main():
    all_recipes = load_recipes()

    # ── Hantera ?ig_url= från iOS Shortcut ───────────────────────────────────
    try:
        ig_url_param = st.query_params.get("ig_url", "")
    except Exception:
        ig_url_param = ""
    if ig_url_param and "ig_url_input" not in st.session_state:
        st.session_state["ig_url_input"] = ig_url_param

    # ── Tab-navigation ────────────────────────────────────────────────────────
    tab_recipe, tab_add = st.tabs(["🍳 Receptsamlingen", "📲 Lägg till recept"])

    with tab_add:
        show_add_recipe_page()

    with tab_recipe:
        # ── Sidebar ───────────────────────────────────────────────────────────────
        with st.sidebar:
            st.markdown('<div style="padding:1rem 0 .5rem;font-family:Playfair Display,serif;font-size:1.5rem;color:#D4A853">🍳 Filter</div>',
                       unsafe_allow_html=True)
            search = st.text_input("", placeholder="Recept, ingrediens, @kreatör…", label_visibility="collapsed")

            all_cats = sorted(set(r.get("category","") for r in all_recipes if r.get("category")))
            cats = st.multiselect("Kategorier", ["Alla"] + all_cats, default=["Alla"])

            all_cuis = sorted(set(r.get("cuisine","") for r in all_recipes if r.get("cuisine")))
            cuisines = st.multiselect("Kök", ["Alla"] + all_cuis, default=["Alla"])

            diffs = st.multiselect("Svårighet", ["Alla","Lätt","Medel","Avancerad"], default=["Alla"])

            max_time = st.slider("Max tillagningstid (minuter)", 10, 120, 120, 5,
                                help="Prep + tillagning totalt")

            sort_by = st.selectbox("Sortera", ["Standard","A-Ö","Svårighet: Lätt först","Svårighet: Avancerad först","Kortast tid"])

            jenny_only = st.toggle("👩 Jennys val", value=False, help="Visa bara recept från Jennys sparade samlingar")

            st.markdown("---")
            st.markdown(f'<div style="color:#A89070;font-size:.78rem;line-height:1.6">'
                       f'📖 {len(all_recipes)} recept<br>'
                       f'👥 {len(set(r.get("creator","") for r in all_recipes))} kreatörer<br>'
                       f'🌍 {len(set(r.get("cuisine","") for r in all_recipes))} olika kök<br><br>'
                       f'<em>Scrapad från @mpdreyer\'s Instagram</em></div>',
                       unsafe_allow_html=True)

            # Popular creators
            st.markdown('<div style="color:#D4A853;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;margin-top:1rem">Populära kreatörer</div>',
                       unsafe_allow_html=True)
            creators_count = {}
            for r in all_recipes:
                c = r.get('creator','')
                if c: creators_count[c] = creators_count.get(c,0)+1
            top_creators = sorted(creators_count.items(), key=lambda x:-x[1])[:8]
            for creator, count in top_creators:
                st.markdown(f'<div style="color:#A89070;font-size:.75rem;padding:.1rem 0">@{creator} <span style="color:#6B7C5A">({count})</span></div>',
                           unsafe_allow_html=True)

        # ── Header ─────────────────────────────────────────────────────────────────
        st.markdown("""
        <div class="site-header">
          <h1>Mattias Receptsamling</h1>
          <div class="tagline">Sparade Instagram-recept · @mpdreyer · Mat-samlingen</div>
        </div>""", unsafe_allow_html=True)

        # ── Detail view ─────────────────────────────────────────────────────────────
        if st.session_state.get("sel"):
            show_detail(st.session_state.sel, all_recipes)
            return

        # ── Filter & Sort ───────────────────────────────────────────────────────────
        shown = filter_recipes(all_recipes, search, cats, cuisines, diffs, max_time)
        if jenny_only:
            shown = [r for r in shown if r.get('jenny_pick')]

        diff_order = {"Lätt":0,"Medel":1,"Avancerad":2}
        def total_time(r):
            def p(t):
                if not t: return 999
                n = re.search(r'\d+', str(t))
                return int(n.group()) if n else 999
            return p(r.get('prep_time',0)) + p(r.get('cook_time',0))

        if sort_by == "A-Ö":
            shown = sorted(shown, key=lambda r: r.get('title',''))
        elif sort_by == "Svårighet: Lätt först":
            shown = sorted(shown, key=lambda r: diff_order.get(r.get('difficulty','Medel'),1))
        elif sort_by == "Svårighet: Avancerad först":
            shown = sorted(shown, key=lambda r: -diff_order.get(r.get('difficulty','Medel'),1))
        elif sort_by == "Kortast tid":
            shown = sorted(shown, key=total_time)

        # ── Stats ───────────────────────────────────────────────────────────────────
        n_cats = len(set(r.get("category","") for r in shown))
        n_cre = len(set(r.get("creator","") for r in shown))
        n_easy = sum(1 for r in shown if r.get("difficulty") == "Lätt")
        n_quick = sum(1 for r in shown if total_time(r) <= 30)
        st.markdown(f"""
        <div class="stats-row">
          <div class="stat"><span class="stat-n">{len(shown)}</span><span class="stat-l">Recept</span></div>
          <div class="stat"><span class="stat-n">{n_cats}</span><span class="stat-l">Kategorier</span></div>
          <div class="stat"><span class="stat-n">{n_cre}</span><span class="stat-l">Kreatörer</span></div>
          <div class="stat"><span class="stat-n">{n_easy}</span><span class="stat-l">Enkla</span></div>
          <div class="stat"><span class="stat-n">{n_quick}</span><span class="stat-l">Under 30 min</span></div>
        </div>""", unsafe_allow_html=True)

        if not shown:
            st.info("Inga recept matchar dina filter. Prova att ändra sökning eller filter.")
            return

        # ── Featured recipe ─────────────────────────────────────────────────────────
        if not search and "Alla" in (cats or ["Alla"]):
            featured = shown[hash(str(len(shown))) % len(shown)]
            feat_cat = featured.get('category','')
            feat_cui = featured.get('cuisine','')
            feat_cat_line = " · ".join(filter(None,[feat_cat,feat_cui]))

            with st.expander("⭐ Utvalt recept", expanded=True):
                fc1, fc2 = st.columns([1, 1.5])
                with fc1:
                    with st.spinner("Ritar illustration…"):
                        feat_svg = get_illustration(featured)
                    feat_uri = svg_to_data_uri(feat_svg)
                    st.markdown(f'<img src="{feat_uri}" style="width:100%;border-radius:12px"/>',
                               unsafe_allow_html=True)
                with fc2:
                    st.markdown(f'<div style="font-size:.65rem;color:#B85C2A;letter-spacing:2px;text-transform:uppercase">{feat_cat_line}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-family:Playfair Display,serif;font-size:1.8rem;color:#2C1A0E;line-height:1.2;margin:.3rem 0">{featured.get("title","")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color:#7A6252;font-size:.88rem;margin-bottom:.8rem">{featured.get("description","")}</div>', unsafe_allow_html=True)
                    m = []
                    if featured.get("prep_time"): m.append(f"⏱ {featured['prep_time']}")
                    if featured.get("cook_time"): m.append(f"🔥 {featured['cook_time']}")
                    if featured.get("servings"): m.append(f"👥 {featured['servings']}")
                    if featured.get("difficulty"): m.append(f"📊 {featured['difficulty']}")
                    st.markdown(" &nbsp;·&nbsp; ".join(f"<small>{x}</small>" for x in m), unsafe_allow_html=True)
                    if st.button("Visa fullständigt recept →", key="featured_btn", type="primary"):
                        st.session_state.sel = featured
                        st.rerun()

        # ── Recipe grid — illustrationer genereras vid visning ────────────────────
        # Visa max 12 i taget för att hålla laddningstiden nere
        page_size = 12
        page = st.session_state.get("page", 0)
        page_recipes = shown[page*page_size:(page+1)*page_size]
        total_pages = (len(shown) - 1) // page_size + 1

        cols = st.columns(3, gap="medium")
        for i, recipe in enumerate(page_recipes):
            with cols[i % 3]:
                # Fallback-SVG direkt — generera bara vid klick
                fallback = _fallback_svg(recipe.get('title',''), recipe.get('category',''))
                st.markdown(card_html(recipe, fallback), unsafe_allow_html=True)
                if st.button("Visa recept", key=f"btn_{page}_{i}_{recipe.get('url','')[-8:]}",
                            use_container_width=True):
                    st.session_state.sel = recipe
                    st.rerun()

        # Pagination
        if total_pages > 1:
            st.markdown("---")
            pcols = st.columns([1,3,1])
            with pcols[0]:
                if page > 0 and st.button("← Föregående"):
                    st.session_state.page = page - 1
                    st.rerun()
            with pcols[1]:
                st.markdown(f'<div style="text-align:center;color:#9B7B5B;font-size:.85rem">Sida {page+1} av {total_pages} &nbsp;·&nbsp; {len(shown)} recept totalt</div>',
                           unsafe_allow_html=True)
            with pcols[2]:
                if page < total_pages - 1 and st.button("Nästa →"):
                    st.session_state.page = page + 1
                    st.rerun()

if __name__ == "__main__":
    if "sel" not in st.session_state:
        st.session_state.sel = None
    if "page" not in st.session_state:
        st.session_state.page = 0
    main()


# ─────────────────────────────────────────────────────────────────────────────
# LÄGG TILL RECEPT — Instagram URL → Claude extraktion → sparas i JSON
# ─────────────────────────────────────────────────────────────────────────────
