#!/usr/bin/env python3
"""
Förhandsberäkna SVG-illustrationer för alla recept.
Kör lokalt: python3 generate_svgs.py
Kräver: ANTHROPIC_API_KEY i ~/dreyer-council/.env
"""
import json, os, re, time, base64, urllib.request
import anthropic

# ── API-nyckel ─────────────────────────────────────────────────────────────
def get_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        for path in [os.path.expanduser("~/dreyer-council/.env"), os.path.expanduser("~/.env")]:
            if os.path.exists(path):
                for line in open(path):
                    if "ANTHROPIC_API_KEY" in line and "=" in line:
                        key = line.split("=", 1)[1].strip().strip('"\'')
                        if key: break
            if key: break
    return key

# ── SVG-prompt ──────────────────────────────────────────────────────────────
SVG_SYSTEM = """Du ritar matillustrationer som rena SVG. Returnera BARA SVG-kod, inga backticks, inga förklaringar.

STRUKTUR (exakt detta format):
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FAF7F2"/>
  <ellipse cx="200" cy="265" rx="130" ry="12" fill="#D9CFC4" opacity="0.6"/>
  <circle cx="200" cy="155" r="118" fill="#FFFFFF" stroke="#E0D5C8" stroke-width="3"/>
  <circle cx="200" cy="155" r="100" fill="#FFFDF9" stroke="#EDE5DB" stroke-width="1"/>
  <!-- MATEN HÄR -->
  <path d="M180 90 Q178 80 180 70" stroke="#CCC" stroke-width="1.5" fill="none" opacity="0.4"/>
  <path d="M200 88 Q198 78 200 68" stroke="#CCC" stroke-width="1.5" fill="none" opacity="0.4"/>
</svg>

FÄRGER per råvara:
pasta/gnocchi=#D4A853 | kött/biff=#8B3A2A | sås/tomat=#C4622D | ost=#F5DEB3
grönsaker=#5A8A47 | örter=#7AAD5A | fisk=#6EB5C0 | ägg=#FFD166
bröd/deg=#C8A870 | choklad=#5C3317 | grädde=#F9EDD8 | citron=#FFE066
lax=#E8845A | räkor=#F4A67A | avokado=#6B8C3A | svamp=#8B7355

REGLER:
1. Rita det TYPISKA för rätten: pasta=böjda rör/tofsar, kött=brun oval, fisk=avlång, sallad=ojämna blad
2. Placera maten PÅ tallriken, naturligt och centrerat
3. Sås/buljong som oval pool i bakgrunden på tallriken
4. 4-7 element, variera storlek för djup
5. En liten garnering i förgrunden (örtskvast, citronskiva, riven ost)
6. INGA text-element, INGA externa resurser, INGEN JavaScript"""

def generate_svg(client, recipe):
    title = recipe.get('title', '')
    category = recipe.get('category', '')
    ings = recipe.get('ingredients') or []
    ing_str = ', '.join(str(i) for i in ings[:5])
    tags = ', '.join(recipe.get('tags') or [])[:60]

    prompt = f"""Rita: {title}
Visa visuellt: {ing_str}
Kategori: {category}
Instruktioner:
- Rita de viktigaste ingredienserna igenkännbart
- Välj rätt former: pasta=böjda rör, kött=oval, fisk=avlång, sallad=ojämna blad
- Lägg sås som pool på tallriken, mat ovanpå
- Avsluta med en garnering"""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2500,
            system=SVG_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        svg = resp.content[0].text.strip()
        svg = re.sub(r'^```(svg|xml)?\s*', '', svg, flags=re.IGNORECASE)
        svg = re.sub(r'\s*```$', '', svg).strip()
        if svg.startswith('<svg'):
            return svg
    except Exception as e:
        print(f"    ❌ API-fel: {e}")
    return None

# ── Push till GitHub ────────────────────────────────────────────────────────
def push_to_github(token, filepath):
    repo = "mpdreyer/recipe-app"
    path = "recipes_extracted.json"
    with open(filepath, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    # Hämta SHA
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    )
    with urllib.request.urlopen(req) as r:
        sha = json.loads(r.read()).get("sha")

    body = json.dumps({
        "message": f"✨ Förberäknade SVG-illustrationer",
        "content": content, "sha": sha
    }).encode()
    req2 = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        data=body, method="PUT",
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github.v3+json",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req2):
        print("✅ recipes_extracted.json pushad till GitHub!")

# ── Huvud ───────────────────────────────────────────────────────────────────
def main():
    key = get_key()
    if not key:
        print("❌ ANTHROPIC_API_KEY saknas")
        return

    client = anthropic.Anthropic(api_key=key)

    recipes_path = os.path.join(os.path.dirname(__file__), 'recipes_extracted.json')
    recipes = json.load(open(recipes_path, encoding='utf-8'))

    todo = [r for r in recipes if r.get('is_recipe') and not r.get('svg')]
    print(f"🎨 Genererar SVG för {len(todo)} recept (ca {len(todo)*2//60} min)...")
    print("   Modell: claude-haiku — snabb och billig\n")

    done = 0
    errors = 0
    for i, recipe in enumerate(todo):
        title = recipe.get('title', '?')[:45]
        print(f"  [{i+1}/{len(todo)}] {title}...", end=' ', flush=True)

        svg = generate_svg(client, recipe)
        if svg:
            recipe['svg'] = svg
            done += 1
            print("✅")
        else:
            errors += 1
            print("⏭ (fallback)")

        # Spara var 10:e recept
        if (i + 1) % 10 == 0:
            json.dump(recipes, open(recipes_path, 'w'), ensure_ascii=False, indent=2)
            print(f"\n  💾 Sparade {i+1} recept...\n")

        time.sleep(0.3)  # Rate limit-paus

    # Slutsparning
    json.dump(recipes, open(recipes_path, 'w'), ensure_ascii=False, indent=2)
    print(f"\n✅ Klart! {done} SVGs genererade, {errors} fallbacks")

    # Push till GitHub
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    if not gh_token:
        gh_token = input("\nGitHub token (tryck Enter för att skippa push): ").strip()
    if gh_token:
        push_to_github(gh_token, recipes_path)
    else:
        print("ℹ️  Skippar GitHub-push — kopiera recipes_extracted.json manuellt")

if __name__ == "__main__":
    main()
