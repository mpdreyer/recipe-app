"""
🍳 Mattias Receptsamling — Streamlit App v2
Claude-genererade SVG-matillustrationer + utökad receptinformation
Kör: streamlit run app.py
"""
import streamlit as st
import json, os, re, hashlib
import anthropic
try:
    from supabase import create_client as _supa_create
    _SUPABASE_OK = True
except ImportError:
    _SUPABASE_OK = False

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
SVG_SYSTEM = """Du ritar matillustrationer som rena SVG. Returnera BARA SVG-kod, inga backticks, inga förklaringar.

STRUKTUR (exakt detta format):
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <!-- bakgrund -->
  <rect width="400" height="300" fill="#FAF7F2"/>
  <!-- tallriksskugga -->
  <ellipse cx="200" cy="265" rx="130" ry="12" fill="#D9CFC4" opacity="0.6"/>
  <!-- tallrik -->
  <circle cx="200" cy="155" r="118" fill="#FFFFFF" stroke="#E0D5C8" stroke-width="3"/>
  <circle cx="200" cy="155" r="100" fill="#FFFDF9" stroke="#EDE5DB" stroke-width="1"/>
  <!-- MATEN HÄR — rita det specifika receptet -->
  <!-- ångdunst -->
  <path d="M180 90 Q178 80 180 70" stroke="#CCC" stroke-width="1.5" fill="none" opacity="0.4"/>
  <path d="M200 88 Q198 78 200 68" stroke="#CCC" stroke-width="1.5" fill="none" opacity="0.4"/>
  <path d="M220 90 Q218 80 220 70" stroke="#CCC" stroke-width="1.5" fill="none" opacity="0.4"/>
</svg>

FÄRGER per råvara:
pasta/gnocchi = #D4A853 (gyllengul)  |  kött/biff = #8B3A2A (mörkrött-brunt)
sås/tomat = #C4622D (röd)            |  ost/parmesan = #F5DEB3 (ljusbeige)
grönsaker = #5A8A47 (mörkgrönt)      |  sallad/örter = #7AAD5A (ljusgrönt)
fisk/skaldjur = #6EB5C0 (blågrön)   |  ägg = #FFD166 (gul)
bröd/deg = #C8A870 (brungul)         |  choklad = #5C3317 (mörk)
grädde/sås = #F9EDD8 (krämvit)       |  citron = #FFE066 (citrongul)
lax = #E8845A (laxrosa)              |  räkor = #F4A67A (ljusorange)

ILLUSTRATIONSPRINCIPER:
1. Rita det TYPISKA för rätten — för pasta: nudeltofsar/rör, för sallad: gröna blad, för biff: brun oval
2. Lägg mat naturligt PÅ tallriken — inte utanför
3. Använd 4-7 element, variera storlek för djup (bakre element lite mindre)
4. Gör sås som en oval pool, kött som rundade organiska former, pasta som böjda rör
5. Lägg en garnering (örtskvast, citronskiva, eller parmesanflaga) i förgrunden
6. INGA text, INGA externa resurser, INGEN JavaScript"""

@st.cache_data(show_spinner=False, ttl=86400*7)  # Cache 7 dagar
def generate_illustration(recipe_url: str, title: str, category: str, 
                          ingredients_str: str, tags_str: str, cache_v: int = 3) -> str:
    """Generera SVG-illustration med Claude Haiku. Cachas per recept-URL."""
    client = get_claude_client()
    if not client:
        return _fallback_svg(title, category)
    
    # Bygg en konkret prompt med visuella instruktioner
    ing_list = [i.strip() for i in ingredients_str.split(',') if i.strip()][:5]
    main_ings = ', '.join(ing_list)
    
    prompt = f"""Rita en matillustration av: {title}
Huvudingredienser att VISA VISUELLT: {main_ings}
Kategori: {category}

Instruktioner:
- Placera maten centrerat på tallriken
- Rita de viktigaste ingredienserna igenkännbart: {main_ings}
- Välj rätt former: pasta=böjda rör/tofsar, kött=oval brun form, fisk=avlång, sallad=ojämna gröna blad
- Lägg till en sås eller buljong som bakgrund PÅ tallriken
- Avsluta med en liten garnering (örtkvast, citronskiva eller riven ost i hörnet)
- Rita BARA SVG, inga förklaringar"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
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
    """Hämta illustration — från JSON om förberäknad, annars generera."""
    # 1. Förberäknad SVG i JSON — direkt, ingen väntan
    if recipe.get('svg'):
        return recipe['svg']
    # 2. Annars generera (cachas i 7 dagar)
    url = recipe.get('url', recipe.get('title',''))
    title = recipe.get('title', '')
    category = recipe.get('category', '')
    ings = ', '.join((recipe.get('ingredients') or [])[:6])
    tags = ', '.join((recipe.get('tags') or [])[:4])
    return generate_illustration(url, title, category, ings, tags, cache_v=3)

def svg_to_data_uri(svg: str) -> str:
    """Konvertera SVG till data URI för img-taggar."""
    import base64
    encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded}"

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
@st.cache_resource(show_spinner=False)
def _get_supa():
    if not _SUPABASE_OK:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            return _supa_create(url, key)
    except Exception:
        pass
    return None


def load_recipes():
    # Bas: JSON-filen (förberäknade recept)
    p = os.path.join(os.path.dirname(__file__), "recipes_extracted.json")
    base = [r for r in json.load(open(p, encoding="utf-8")) if r.get("is_recipe")] if os.path.exists(p) else []

    # Extra: recept tillagda via appen (sparade i Supabase)
    try:
        supa = _get_supa()
        if supa:
            rows = supa.table("user_recipes").select("recipe_json").order("created_at").execute()
            extra = [json.loads(r["recipe_json"]) for r in (rows.data or [])]
            # Dedup på URL
            existing = {r.get("url", r.get("title","")) for r in base}
            for r in extra:
                key = r.get("url", r.get("title",""))
                if key not in existing:
                    base.append(r)
                    existing.add(key)
    except Exception:
        pass

    return base

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
    """Hämta caption via Instagram oEmbed API — funkar utan inloggning."""
    import urllib.request, urllib.error, urllib.parse, json as _json
    
    # 1. Försök oEmbed API (public, ingen auth)
    oembed_url = f"https://api.instagram.com/oembed/?url={urllib.parse.quote(url)}&omitscript=true"
    try:
        req = urllib.request.Request(oembed_url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; RecipeApp/1.0)'
        })
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
            title = data.get('title', '')
            author = data.get('author_name', '')
            if title:
                return title, author
    except Exception:
        pass

    # 2. Fallback: og:description med mobile user-agent
    import re as _re, html as _html
    for ua in [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1',
        'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
    ]:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua})
            with urllib.request.urlopen(req, timeout=8) as r:
                html_raw = r.read().decode('utf-8', errors='ignore')
            m = _re.search(r'property="og:description" content="([^"]+)"', html_raw)
            if m:
                caption = _html.unescape(m.group(1))
                cm = _re.search(r'comments - ([a-zA-Z0-9_.]+) ', caption)
                creator = cm.group(1) if cm else ""
                return caption, creator
        except Exception:
            continue

    return "", ""


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
    """Spara nytt recept i Supabase (persistent på Streamlit Cloud)."""
    import sys as _sys
    _sys.path.insert(0, '.')

    # Beräkna näringsvärde
    try:
        from nutrition_engine import calculate_nutrition, NUTRITION_FALLBACKS
        nut = calculate_nutrition(recipe)
        recipe['nutrition'] = nut if nut else {
            **NUTRITION_FALLBACKS.get(recipe.get('category','Varmrätt'),
                                       NUTRITION_FALLBACKS.get('Varmrätt',{})),
            'calculated': False
        }
    except Exception:
        pass

    recipe['is_recipe'] = True

    # Supabase — primär lagring
    supa = _get_supa()
    if supa:
        try:
            url_key = recipe.get('url') or recipe.get('title', '')
            # Dubblettcheck
            existing = supa.table("user_recipes").select("id").eq("url_key", url_key).execute()
            if existing.data:
                return False
            supa.table("user_recipes").insert({
                "url_key":     url_key,
                "title":       recipe.get('title',''),
                "recipe_json": json.dumps(recipe, ensure_ascii=False)
            }).execute()
            return True
        except Exception as e:
            st.warning(f"Supabase-fel: {e} — försöker spara lokalt")

    # Fallback: lokal fil (funkar bara lokalt, ej på Streamlit Cloud)
    path = "recipes_extracted.json"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        existing_urls = {r.get('url','') for r in recipes}
        if recipe.get('url','') in existing_urls:
            return False
        recipes.append(recipe)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def show_add_recipe_page():
    """Lägg till recept via paste, uppladdad bild eller text."""
    import base64 as _b64, json as _json, re as _re

    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem'>
      <div style='font-family:"Playfair Display",serif;font-size:2.2rem;color:#1C1208'>
        📲 Lägg till recept
      </div>
      <div style='font-size:.9rem;color:#6B5B45;margin-top:.4rem;
                  letter-spacing:1px;text-transform:uppercase'>
        Från Instagram direkt till receptsamlingen
      </div>
    </div>""", unsafe_allow_html=True)

    tab_paste, tab_upload, tab_txt, tab_manual = st.tabs([
        "📋 Klistra in bild",
        "📁 Ladda upp bild",
        "✍️ Klistra in text",
        "📝 Fyll i manuellt",
    ])

    # ── TAB 1: Klistra in bild via paste ──────────────────────────────────────
    with tab_paste:
        st.markdown("""
        <div style='background:#FFF8EE;border-left:4px solid #D4A853;
                    padding:.8rem 1.1rem;border-radius:8px;margin:.5rem 0 1rem;font-size:.9rem'>
        <b>iPhone:</b> Ta screenshot → öppna Foton → tryck länge på bilden → <b>Kopiera</b><br>
        Öppna sedan appen → tryck länge i rutan nedan → <b>Klistra in</b>
        </div>""", unsafe_allow_html=True)

        # HTML paste-komponent som skickar base64-data till Streamlit
        paste_result = st.components.v1.html("""
        <div id="paste-area" contenteditable="true" style="
            min-height: 160px; border: 2px dashed #D4A853; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            background: #FFFDF7; cursor: pointer; position: relative;
            font-family: sans-serif; color: #A89070; font-size: 0.95rem;
            padding: 1rem; text-align: center; outline: none;">
            <span id="hint">📸 Klistra in bild här (Ctrl+V / Cmd+V eller tryck länge → Klistra in)</span>
            <img id="preview" style="max-width:100%;max-height:300px;display:none;border-radius:8px">
        </div>
        <div id="status" style="margin-top:.5rem;font-size:.8rem;color:#6B5B45;text-align:center"></div>
        <button id="send-btn" onclick="sendImage()" style="
            display:none; margin-top:.8rem; width:100%; padding:.7rem;
            background:#1C1208; color:white; border:none; border-radius:8px;
            font-size:.95rem; cursor:pointer; font-weight:600">
            ✨ Extrahera recept
        </button>
        <input type="hidden" id="img-data">

        <script>
        const area = document.getElementById('paste-area');
        const hint = document.getElementById('hint');
        const preview = document.getElementById('preview');
        const status = document.getElementById('status');
        const btn = document.getElementById('send-btn');

        // Paste-händelse
        area.addEventListener('paste', function(e) {
            e.preventDefault();
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let item of items) {
                if (item.type.startsWith('image/')) {
                    const blob = item.getAsFile();
                    const reader = new FileReader();
                    reader.onload = function(ev) {
                        const b64 = ev.target.result;
                        preview.src = b64;
                        preview.style.display = 'block';
                        hint.style.display = 'none';
                        document.getElementById('img-data').value = b64;
                        btn.style.display = 'block';
                        status.textContent = '✅ Bild inklistrad — tryck Extrahera recept';
                        area.style.borderColor = '#4CAF50';
                    };
                    reader.readAsDataURL(blob);
                    break;
                }
            }
        });

        // Skicka base64 till Streamlit via sessionStorage + message
        function sendImage() {
            const data = document.getElementById('img-data').value;
            if (!data) return;
            // Skicka till förälder-fönstret (Streamlit iframe)
            window.parent.postMessage({type: 'paste_image', data: data}, '*');
            status.textContent = '⏳ Skickar bild till Claude...';
            btn.disabled = true;
        }

        // Lyssna på klick utanför knapp
        area.addEventListener('click', function() { area.focus(); });
        </script>
        """, height=280)

        # Streamlit kan inte ta emot postMessage direkt — använd session_state trick
        # Visa istället ett file_uploader som backup med tydlig paste-instruktion
        st.markdown("**Eller** — välj bilden direkt:")
        pasted = st.file_uploader(
            "Välj screenshot från Foton",
            type=["jpg","jpeg","png","webp"],
            key="paste_uploader",
            label_visibility="collapsed"
        )
        if pasted:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.image(pasted, use_container_width=True)
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("✨ Extrahera recept", use_container_width=True,
                             type="primary", key="go_paste"):
                    st.session_state.pop("extracted_recipe_paste_import", None)
                    _extract_from_image(pasted, "paste_import")
        if "extracted_recipe_paste_import" in st.session_state:
            _show_recipe_preview_and_save(st.session_state["extracted_recipe_paste_import"], "paste_import")

    # ── TAB 2: Ladda upp bild ──────────────────────────────────────────────────
    with tab_upload:
        st.markdown("""
        <div style='background:#FFF8EE;border-left:4px solid #D4A853;
                    padding:.8rem 1.1rem;border-radius:8px;margin:.5rem 0 1rem;font-size:.9rem'>
        <b>iPhone:</b> Ta screenshot → välj bilden nedan från Foton-appen
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Välj screenshot eller foto av receptet",
            type=["jpg","jpeg","png","webp"],
            key="file_uploader"
        )
        if uploaded:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.image(uploaded, use_container_width=True)
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("✨ Extrahera recept", use_container_width=True,
                             type="primary", key="go_upload"):
                    st.session_state.pop("extracted_recipe_upload_import", None)
                    _extract_from_image(uploaded, "upload_import")
        if "extracted_recipe_upload_import" in st.session_state:
            _show_recipe_preview_and_save(st.session_state["extracted_recipe_upload_import"], "upload_import")

    # ── TAB 3: Klistra in text ─────────────────────────────────────────────────
    with tab_txt:
        st.markdown("""
        <div style='background:#FFF8EE;border-left:4px solid #D4A853;
                    padding:.8rem 1.1rem;border-radius:8px;margin:.5rem 0 1rem;font-size:.9rem'>
        <b>Instagram:</b> Håll inne på texten → <b>Markera allt</b> → <b>Kopiera</b> → klistra in nedan
        </div>""", unsafe_allow_html=True)

        caption = st.text_area(
            "Recepttext:", height=200,
            placeholder="Klistra in recepttexten från Instagram här...",
            key="txt_caption"
        )
        col_a, col_b = st.columns(2)
        with col_a:
            creator = st.text_input("@kreatör (valfritt):",
                                    placeholder="t.ex. the_pastaqueen", key="txt_creator")
        with col_b:
            ig_url = st.text_input("Instagram-länk (valfritt):",
                                   placeholder="https://instagram.com/p/...", key="txt_url")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✨ Extrahera recept", use_container_width=True,
                         type="primary", key="go_txt", disabled=not bool(caption)):
                url = ig_url.strip().split("?")[0] if ig_url else ""
                with st.spinner("Claude extraherar receptet..."):
                    recipe = extract_recipe_from_caption(caption, url, creator)
                if recipe and recipe.get("is_recipe"):
                    st.session_state["extracted_recipe_text_import"] = recipe
                    st.rerun()
                else:
                    st.warning("Hittade inget recept i texten.")
        if "extracted_recipe_text_import" in st.session_state:
            _show_recipe_preview_and_save(st.session_state["extracted_recipe_text_import"], "text_import")

    # ── TAB 4: Manuellt formulär (ingen API krävs) ────────────────────────────
    with tab_manual:
        st.markdown("""
        <div style='background:#FFF8EE;border-left:4px solid #D4A853;
                    padding:.8rem 1.1rem;border-radius:8px;margin:.5rem 0 1rem;font-size:.9rem'>
        Fyll i receptet direkt — ingen AI behövs. Perfekt när extraktionen krånglar.
        </div>""", unsafe_allow_html=True)

        m_title   = st.text_input("Receptnamn *", placeholder="t.ex. Spaghetti Carbonara", key="m_title")
        m_desc    = st.text_input("Kort beskrivning", placeholder="Klassisk italiensk pasta", key="m_desc")
        m_creator = st.text_input("@kreatör", placeholder="the_pastaqueen", key="m_creator")
        m_url     = st.text_input("Instagram-länk", placeholder="https://instagram.com/p/...", key="m_url")

        col_a, col_b = st.columns(2)
        with col_a:
            m_cat  = st.selectbox("Kategori", ["Varmrätt","Förrätt","Dessert","Bakverk","Snacks","Frukost","Tillbehör","Sås","Dryck"], key="m_cat")
            m_diff = st.selectbox("Svårighet", ["Lätt","Medel","Avancerad"], key="m_diff")
            m_serv = st.text_input("Portioner", placeholder="4 portioner", key="m_serv")
        with col_b:
            m_cui  = st.selectbox("Kök", ["Svensk","Italiensk","Asiatisk","Franskt","Övrigt"], key="m_cui")
            m_prep = st.text_input("Förberedelsetid", placeholder="15 min", key="m_prep")
            m_cook = st.text_input("Tillagningstid", placeholder="30 min", key="m_cook")

        m_ings = st.text_area("Ingredienser (en per rad) *", height=150,
                               placeholder="400g spaghetti\n200g guanciale\n4 äggulor", key="m_ings")
        m_inst = st.text_area("Tillagning *", height=150,
                               placeholder="Koka pastan al dente...", key="m_inst")
        jenny_m = st.checkbox("Jennys val 👩", value=True, key="m_jenny")

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("💾 Spara recept", use_container_width=True, type="primary",
                         key="btn_manual", disabled=not bool(m_title and m_ings and m_inst)):
                recipe = {
                    "is_recipe":    True,
                    "title":        m_title.strip(),
                    "description":  m_desc.strip(),
                    "creator":      m_creator.strip(),
                    "url":          m_url.strip().split("?")[0] if m_url else "",
                    "category":     m_cat,
                    "cuisine":      m_cui,
                    "difficulty":   m_diff,
                    "servings":     m_serv or "4 portioner",
                    "prep_time":    m_prep or "",
                    "cook_time":    m_cook or "",
                    "ingredients":  [i.strip() for i in m_ings.strip().splitlines() if i.strip()],
                    "instructions": m_inst.strip(),
                    "tags":         [],
                    "jenny_pick":   jenny_m,
                    "added_by":     "manual",
                }
                if save_recipe_to_file(recipe):
                    st.success(f"🎉 **{recipe['title']}** sparad!")
                    st.balloons()
                else:
                    st.warning("Receptet finns redan i samlingen.")


def _extract_from_image(img_source, source_key: str):
    """Gemensam bildextraktion via Claude Vision."""
    import base64 as _b64, json as _json, re as _re

    client = get_claude_client()
    if not client:
        st.error("Claude API-nyckel saknas — kontrollera Streamlit secrets.")
        return

    try:
        if hasattr(img_source, 'read'):
            img_source.seek(0)
            img_bytes = img_source.read()
            media_type = getattr(img_source, 'type', 'image/jpeg') or 'image/jpeg'
        else:
            # Hantera både UploadedFile och bytes
            import io
            buf = io.BytesIO()
            img_source.save(buf, format='PNG')
            img_bytes = buf.getvalue()
            media_type = 'image/png'
    except Exception as e:
        st.error(f"Kunde inte läsa bilden: {e}")
        return

    img_b64 = _b64.standard_b64encode(img_bytes).decode()

    SYSTEM = (
        "Du är ett recept-OCR-system. Extrahera receptet från bilden. "
        "Returnera BARA giltig JSON utan backticks.\n"
        'Om recept: {"is_recipe":true,"title":"...","description":"...","creator":"",'
        '"ingredients":["..."],"instructions":"...","category":"Varmrätt/Förrätt/Dessert/'
        'Bakverk/Snacks/Frukost/Tillbehör/Sås/Dryck","cuisine":"Svensk/Italiensk/Asiatisk/'
        'Franskt/Övrigt","difficulty":"Lätt/Medel/Avancerad","servings":"...","prep_time":"...",'
        '"cook_time":"...","tags":["..."]}\n'
        'Om inget recept: {"is_recipe":false}'
    )

    with st.spinner("Claude Vision läser bilden..."):
        try:
            resp = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1500,
                system=SYSTEM,
                messages=[{"role": "user", "content": [
                    {"type": "image",
                     "source": {"type": "base64",
                                "media_type": media_type,
                                "data": img_b64}},
                    {"type": "text", "text": "Extrahera receptet. Bara JSON."}
                ]}]
            )
            raw = _re.sub(r'^```(json)?', '',
                          resp.content[0].text.strip()).strip().rstrip('`').strip()
            recipe = _json.loads(raw)
        except Exception as e:
            st.error(f"Fel: {e}")
            return

    if not recipe.get("is_recipe"):
        st.warning("Hittade inget recept i bilden — prova en tydligare bild.")
        return

    st.session_state[f"extracted_recipe_{source_key}"] = recipe
    st.rerun()


def _show_recipe_preview_and_save(recipe: dict, source: str):
    """Gemensam förhandsgranskning och spara-knapp."""
    import json as _json

    st.markdown("---")
    st.success(f"✅ **{recipe.get('title', '?')}** hittad!")

    with st.expander("Förhandsgranska", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            if recipe.get("creator"):
                st.markdown(f"**@kreatör:** {recipe['creator']}")
            st.markdown(f"**Kategori:** {recipe.get('category','?')} · {recipe.get('cuisine','?')}")
            st.markdown(f"**Svårighet:** {recipe.get('difficulty','?')}")
            st.markdown(f"**Tid:** {recipe.get('prep_time') or '?'} + {recipe.get('cook_time') or '?'}")
            st.markdown(f"**Portioner:** {recipe.get('servings') or '?'}")
        with c2:
            ings = recipe.get("ingredients", [])
            st.markdown(f"**{len(ings)} ingredienser:**")
            for ing in ings[:8]:
                st.markdown(f"• {ing}")
            if len(ings) > 8:
                st.markdown(f"*…och {len(ings)-8} till*")
        if recipe.get("description"):
            st.caption(recipe["description"])

    jenny = st.checkbox("Jennys val 👩", value=True, key=f"jenny_{source}")
    recipe["jenny_pick"] = jenny
    recipe["added_by"]   = source
    recipe["is_recipe"]  = True
    recipe.setdefault("url", "")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        clicked = st.button("💾 Spara till samlingen", use_container_width=True,
                            type="primary", key=f"save_{source}")

    if clicked:
        try:
            from nutrition_engine import calculate_nutrition, NUTRITION_FALLBACKS
            nut = calculate_nutrition(recipe)
            recipe["nutrition"] = nut if nut else {
                **NUTRITION_FALLBACKS.get(recipe.get("category", "Varmrätt"),
                                          NUTRITION_FALLBACKS.get("Varmrätt", {})),
                "calculated": False
            }
        except Exception:
            pass
        try:
            saved = save_recipe_to_file(recipe)
        except Exception as e:
            st.error(f"Fel vid sparning: {e}")
            saved = False
        if saved:
            st.session_state.pop(f"extracted_recipe_{source}", None)
            st.success(f"🎉 **{recipe.get('title','')}** sparad i samlingen!")
            st.balloons()
        else:
            st.warning("Receptet finns redan i samlingen.")


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
