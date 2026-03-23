"""
Näringsvärdesmotor v3
- Beräknar per portion OCH per 100g
- Hanterar "parts"-format (drinkar)
- Robust enhetshantering
"""
import re

# Näringsvärden per 100g: (kcal, protein_g, fett_g, kolhydrat_g)
NUTRIENT_DB = {
    # Kött
    "nötfärs":       (250,18,20, 0), "köttfärs":      (250,18,20, 0),
    "oxfilé":        (158,26, 6, 0), "entrecôte":     (270,22,20, 0),
    "oxkind":        (200,22,12, 0), "biff":          (200,24,12, 0),
    "brisket":       (240,25,15, 0), "ribeye":        (290,21,23, 0),
    "fläsk":         (280,17,24, 0), "fläskfilé":     (140,22, 5, 0),
    "fläskkarré":    (300,17,26, 0), "fläskytterfilé":(145,22, 6, 0),
    "bacon":         (410,13,40, 0), "pancetta":      (425,14,42, 0),
    "guanciale":     (435,11,44, 0), "prosciutto":    (250,27,16, 0),
    "skinka":        (145,20, 7, 1), "salami":        (400,22,35, 1),
    "korv":          (280,14,24, 3), "chorizo":       (455,24,38, 2),
    "kyckling":      (165,25, 7, 0), "kycklinglår":   (180,20,11, 0),
    "kycklingfilé":  (110,23, 2, 0), "kalkon":        (135,22, 5, 0),
    "lamm":          (250,20,18, 0), "kalv":          (140,20, 6, 0),
    "hjort":         (120,23, 2, 0), "and":           (337,19,29, 0),
    # Fisk & skaldjur
    "lax":           (208,20,13, 0), "rökt lax":      (180,25, 9, 0),
    "torsk":         ( 82,18, 1, 0), "hälleflundra":  (110,21, 3, 0),
    "sej":           ( 82,18, 1, 0), "rödtunga":      ( 85,18, 1, 0),
    "abborre":       ( 91,19, 1, 0), "tonfisk":       (130,28, 1, 0),
    "räkor":         ( 99,21, 2, 0), "hummer":        ( 90,19, 1, 0),
    "musslor":       ( 86,12, 2, 4), "blåmusslor":    ( 86,12, 2, 4),
    "pilgrimsmusslor":( 88,17, 1, 3),"ansjovis":      (210,29,10, 0),
    "kaviar":        (264,26,18, 0), "löjrom":        (180,26,10, 0),
    "stenbitsrom":   (200,27,11, 0),
    # Mejeri
    "ägg":           (155,13,11, 1), "äggula":        (322,16,27, 3),
    "smör":          (717, 1,81, 0), "grädde":        (300, 2,30, 3),
    "vispgrädde":    (300, 2,30, 3), "lättgrädde":    (120, 3,11, 4),
    "matlagningsgrädde":(120,3,11,4),"crème fraîche": (290, 2,30, 3),
    "smetana":       (230, 3,23, 3), "gräddfil":      (193, 3,20, 3),
    "mjölk":         ( 61, 3, 4, 5), "kärnmjölk":     ( 38, 3, 1, 5),
    "parmesan":      (431,38,29, 0), "parmigiano":    (431,38,29, 0),
    "pecorino":      (389,25,32, 0), "mozzarella":    (280,22,22, 2),
    "burrata":       (280,14,25, 2), "brie":          (334,20,28, 0),
    "camembert":     (300,20,24, 0), "fetaost":       (264,14,21, 4),
    "feta":          (264,14,21, 4), "gorgonzola":    (353,21,29, 2),
    "gruyère":       (413,30,32, 0), "cheddar":       (403,25,33, 1),
    "ricotta":       (174,11,13, 3), "mascarpone":    (429, 7,44, 4),
    "cream cheese":  (350, 6,35, 4), "yoghurt":       ( 59, 3, 3, 5),
    # Pasta & spannmål (torra)
    "pasta":         (352,12, 2,71), "spaghetti":     (352,12, 2,71),
    "tagliatelle":   (352,12, 2,71), "penne":         (352,12, 2,71),
    "rigatoni":      (352,12, 2,71), "linguine":      (352,12, 2,71),
    "fettuccine":    (352,12, 2,71), "gnocchi":       (159, 4, 1,33),
    "ris":           (360, 7, 1,79), "orzo":          (352,12, 2,71),
    "couscous":      (356,12, 1,72), "mjöl":          (364,10, 1,76),
    "havre":         (389,17, 7,66), "havregryn":     (389,17, 7,66),
    "mandelmjöl":    (571,21,49,10), "potatismjöl":   (357, 0, 0,86),
    # Bröd & bakning
    "bröd":          (265, 9, 3,49), "surdeg":        (250, 9, 2,46),
    "bagel":         (257, 9, 2,49), "tortilla":      (305,10, 8,48),
    "focaccia":      (257, 7, 7,42), "smördeg":       (400, 5,27,34),
    "ströbröd":      (395,12, 4,76), "panko":         (395,12, 4,77),
    # Grönsaker
    "lök":           ( 40, 1, 0, 9), "vitlök":        (149, 6, 1,33),
    "tomat":         ( 18, 1, 0, 4), "körsbärstomater":( 18,1, 0, 4),
    "paprika":       ( 31, 1, 0, 6), "aubergine":     ( 25, 1, 0, 5),
    "zucchini":      ( 17, 1, 0, 3), "spenat":        ( 23, 3, 0, 4),
    "broccoli":      ( 34, 3, 0, 7), "potatis":       ( 77, 2, 0,17),
    "sötpotatis":    ( 86, 2, 0,20), "morot":         ( 41, 1, 0, 9),
    "selleri":       ( 16, 1, 0, 3), "purjolök":      ( 61, 2, 0,14),
    "avokado":       (160, 2,15, 9), "kikärtor":      (164, 9, 3,27),
    "svamp":         ( 22, 3, 0, 3), "kantareller":   ( 38, 2, 1, 7),
    "porcini":       ( 35, 2, 1, 6), "champinjoner":  ( 22, 3, 0, 3),
    # Frukt
    "citron":        ( 29, 1, 0, 9), "lime":          ( 30, 1, 0,11),
    "apelsin":       ( 47, 1, 0,12), "grapefrukt":    ( 42, 1, 0,11),
    "äpple":         ( 52, 0, 0,14), "päron":         ( 57, 0, 0,15),
    "banan":         ( 89, 1, 0,23), "hallon":        ( 52, 1, 1,12),
    "jordgubbar":    ( 32, 1, 0, 8), "blåbär":        ( 57, 1, 0,14),
    "mango":         ( 60, 1, 0,15), "druvor":        ( 67, 1, 0,17),
    "persika":       ( 39, 1, 0,10), "fikon":         ( 74, 1, 0,19),
    "dadlar":        (282, 2, 0,75),
    # Oljor & fetter
    "olivolja":      (884, 0,100, 0), "olja":         (884, 0,100, 0),
    "sesamolja":     (884, 0,100, 0), "kokosolja":    (862, 0, 99, 0),
    # Socker & sötsaker
    "socker":        (387, 0, 0,100), "farinsocker":  (380, 0, 0,98),
    "florsocker":    (387, 0, 0,100), "honung":       (304, 0, 0,82),
    "lönnsirap":     (260, 0, 0,67), "sirap":         (280, 0, 0,73),
    "choklad":       (546, 5,31,60), "mörk choklad":  (598, 8,43,46),
    "vit choklad":   (539, 6,30,59), "kakao":         (228,20,14,58),
    "nötter":        (607,15,54,28), "mandel":        (579,21,50,22),
    "valnötter":     (654,15,65,14), "hasselnötter":  (628,15,61,17),
    "pistasch":      (562,20,45,28), "pinjenötter":   (673,14,68,13),
    "kokosflingor":  (354, 3,33,43),
    # Sås & kryddor
    "soja":          ( 53, 8, 0, 5), "miso":          (199,12, 6,26),
    "tahini":        (595,17,54,21), "majonnäs":      (680, 1,75, 1),
    "senap":         ( 66, 4, 4, 5), "ketchup":       (100, 1, 0,25),
    "sriracha":      ( 93, 1, 1,19), "oyster sauce":  ( 78, 3, 0,16),
    "harissa":       ( 65, 2, 4, 6),
    # ALKOHOL (per 100ml = 100g)
    "prosecco":      ( 80, 0, 0, 2), "champagne":     ( 77, 0, 0, 2),
    "vitt vin":      ( 83, 0, 0, 3), "rödvin":        ( 85, 0, 0, 3),
    "öl":            ( 43, 0, 0, 4), "cider":         ( 47, 0, 0,11),
    "gin":           (263, 0, 0, 0), "vodka":         (231, 0, 0, 0),
    "tequila":       (231, 0, 0, 0), "rom":           (231, 0, 0, 0),
    "bourbon":       (250, 0, 0, 0), "whisky":        (250, 0, 0, 0),
    "cointreau":     (320, 0, 0,30), "triple sec":    (310, 0, 0,29),
    "aperol":        (150, 0, 0,20), "campari":       (230, 0, 0,25),
    "baileys":       (327, 4,12,37), "kahlúa":        (327, 0, 0,50),
    "st-germain":    (280, 0, 0,70), "amaretto":      (330, 0, 0,42),
    "limoncello":    (290, 0, 0,33), "peach liqueur": (290, 0, 0,33),
    "martini rosso": (150, 0, 0,15), "vermouth":      (150, 0, 0,15),
    # Dryck (alkoholfri)
    "espresso":      (  9, 1, 0, 2), "kaffe":         (  2, 0, 0, 0),
    "tonic":         ( 34, 0, 0, 9), "soda":          (  0, 0, 0, 0),
    "grapefruktsjuice":(39,1, 0,10), "apelsinjuice":  ( 45, 1, 0,10),
    "kokosmjölk":    (230, 2,24, 3),
    # Misc
    "marshmallows":  (318, 2, 0,81), "gelatin":       (335,86, 0, 0),
}

# Enheter → ml/g
UNIT_TO_G = {
    "kg": 1000, "g": 1, "hg": 100, "mg": 0.001,
    "l": 1000, "dl": 100, "cl": 10, "ml": 1,
    "msk": 15, "tsk": 5, "krm": 1, "nypa": 2,
    "tbsp": 15, "tsp": 5, "cup": 240, "cups": 240,
    "oz": 28.35, "fl oz": 29.6, "lb": 453.6, "pint": 473,
    "st": None, "stycken": None, "styck": None, "st.": None,
    "burk": None, "förp": None, "knippe": None, "knippa": None,
    "skiva": None, "skivor": None, "klyfta": None, "klyftor": None,
    "näve": 30, "handfull": 30,
}

PIECE_WEIGHTS = {
    "ägg": 60, "äggula": 20, "äggvita": 40,
    "vitlök": 5, "vitlöksklyfta": 5, "vitlöksklyftor": 5,
    "lök": 150, "schalottenlök": 40, "rödlök": 150,
    "citron": 120, "lime": 80, "apelsin": 180, "grapefrukt": 250,
    "tomat": 120, "körsbärstomat": 15, "paprika": 150,
    "potatis": 150, "sötpotatis": 200, "morot": 80,
    "avokado": 200, "persika": 150, "päron": 160, "äpple": 180, "banan": 120,
    "bagel": 100, "bröd": 35, "tortilla": 45, "naan": 90,
    "dadel": 20, "fikon": 40,
}

# Standardvolym för drinkar (1 portion)
DRINK_PART_ML = 30  # 1 "part" ≈ 30ml


def clean_string(s: str) -> str:
    """Rensa bort emojis och specialtecken."""
    s = re.sub(r'[▪️•●◆✦★☆→⤵️⤴️🍹🍸🥃🍺🍷🥂]+', '', s)
    s = re.sub(r'[\U00010000-\U0010ffff]', '', s)  # emojis
    return s.strip()


def parse_amount(ingredient_str: str) -> tuple:
    """
    Parsa ingredienssträng → (gram, namn).
    Hanterar: "400g pasta", "3 dl grädde", "2 msk smör",
              "50ml gin", "3 parts prosecco", "2 ägg", "½ avokado"
    """
    s = clean_string(ingredient_str).lower()
    s = (s.replace(',', '.').replace('½', '0.5').replace('¼', '0.25')
          .replace('¾', '0.75').replace('⅓', '0.33').replace('⅔', '0.67'))

    # Ta bort inledande bullet-chars
    s = re.sub(r'^[▪•\-–—]+\s*', '', s)

    # Hoppa över rena kryddor/garnering utan mängd
    if re.match(r'^(salt|peppar|svartpeppar|vitpeppar|chiliflakes?|paprika|oregano|timjan|rosmarin|'
                r'basilika|persilja|koriander|dill|dragon|gräslök|muskotnöt|kanel|kardemumma|'
                r'ingefära|saffran|lagerblad|flingsalt|is|vatten|valfritt|garnering)', s):
        return 0, s

    # --- Format: "NAME - 50ml", "gin - 30ml" (drinkar med bindestreck) ---
    m = re.match(r'^(.+?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(ml|cl|dl|l)\s*$', s)
    if m:
        name, val, unit = m.group(1).strip(), float(m.group(2)), m.group(3)
        return val * UNIT_TO_G[unit], name

    # --- Format: "prosecco 3 parts", "campari 1 part" (namn FÖRE siffra) ---
    m = re.match(r'^(.+?)\s+(\d+(?:\.\d+)?)\s+parts?$', s)
    if m:
        name, parts = m.group(1).strip(), float(m.group(2))
        return parts * DRINK_PART_ML, name

    # --- Format: "50ml gin", "25ml cointreau" ---
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(ml|cl|dl|l)\s+(.+)$', s)
    if m:
        val, unit, name = float(m.group(1)), m.group(2), m.group(3).strip()
        return val * UNIT_TO_G[unit], name

    # --- Format: "3 parts prosecco", "2 part gin" ---
    m = re.match(r'^(\d+(?:\.\d+)?)\s+parts?\s+(.+)$', s)
    if m:
        parts, name = float(m.group(1)), m.group(2).strip()
        return parts * DRINK_PART_ML, name

    # --- Format: "400g nötfärs", "1.5 kg fläsk" ---
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(kg|hg|g|mg)\s+(.+)$', s)
    if m:
        val, unit, name = float(m.group(1)), m.group(2), m.group(3).strip()
        return val * UNIT_TO_G[unit], name

    # --- Format: "3 dl grädde", "2 msk smör", "1 tsk vanilj" ---
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(dl|cl|l|msk|tsk|krm|tbsp|tsp|cup|cups|fl oz|pint|nypa|näve|handfull)\s+(.+)$', s)
    if m:
        val, unit, name = float(m.group(1)), m.group(2).replace(' ',''), m.group(3).strip()
        multiplier = UNIT_TO_G.get(unit, 15)
        return val * multiplier, name

    # --- Format: "2 ägg", "1 citron", "3 vitlöksklyftor" ---
    m = re.match(r'^(\d+(?:\.\d+)?)\s+(.+)$', s)
    if m:
        val, name = float(m.group(1)), m.group(2).strip()
        # Kolla om namnet matchar ett räknat livsmedel
        for key, weight in PIECE_WEIGHTS.items():
            if key in name:
                return val * weight, name
        # Okänt räknat — försök matcha nutrient ändå, använd 100g default
        if lookup_nutrient(name):
            return val * 80, name  # rimlig genomsnittsportionsvikt
        return 0, name

    # Inget matchade
    return 0, s


def lookup_nutrient(name: str) -> tuple | None:
    """Slå upp näringsvärde — exakt eller partiell matchning."""
    n = name.lower().strip()
    # Ta bort eventuellt tal i slutet
    n = re.sub(r'\s*\d+%.*$', '', n).strip()
    if n in NUTRIENT_DB:
        return NUTRIENT_DB[n]
    # Partiell: längsta nyckel som finns i strängen
    best, best_len = None, 0
    for key, val in NUTRIENT_DB.items():
        if key in n and len(key) > best_len:
            best, best_len = val, len(key)
    return best


def calculate_nutrition(recipe: dict) -> dict | None:
    """
    Beräkna näringsvärden.
    Returnerar: {
        "per_portion": {"kcal","protein","fett","kolhydrat"},
        "per_100g":    {"kcal","protein","fett","kolhydrat"},
        "portion_g":   gram per portion (int),
        "calculated":  True/False
    }
    """
    ingredients = recipe.get('ingredients') or []
    servings = _parse_servings(recipe.get('servings', ''))

    total_g   = 0.0
    total_kcal = 0.0
    total_prot = 0.0
    total_fat  = 0.0
    total_carb = 0.0
    matched = 0

    for ing in ingredients:
        if not ing or len(str(ing).strip()) < 2:
            continue
        grams, name = parse_amount(str(ing))
        if grams <= 0 or grams > 4000:
            continue
        nutrient = lookup_nutrient(name)
        if nutrient:
            kcal, prot, fat, carb = nutrient
            f = grams / 100.0
            total_g    += grams
            total_kcal += kcal * f
            total_prot += prot * f
            total_fat  += fat  * f
            total_carb += carb * f
            matched += 1

    if matched == 0 or total_g < 10:
        return None

    # Per portion
    pp_kcal = total_kcal / servings
    pp_prot = total_prot / servings
    pp_fat  = total_fat  / servings
    pp_carb = total_carb / servings
    portion_g = total_g / servings

    # Sanitetskontroll per portion
    pp_kcal = max(20, min(2500, pp_kcal))
    pp_prot = max(0,  min(200, pp_prot))
    pp_fat  = max(0,  min(200, pp_fat))
    pp_carb = max(0,  min(300, pp_carb))

    # Per 100g (baserat på total vikt)
    if total_g > 0:
        f100 = 100.0 / total_g
        p100_kcal = min(900, total_kcal * f100)
        p100_prot = min(100, total_prot * f100)
        p100_fat  = min(100, total_fat  * f100)
        p100_carb = min(100, total_carb * f100)
    else:
        p100_kcal = p100_prot = p100_fat = p100_carb = 0

    return {
        "per_portion": {
            "kcal":      str(round(pp_kcal)),
            "protein":   str(round(pp_prot)) + "g",
            "fett":      str(round(pp_fat))  + "g",
            "kolhydrat": str(round(pp_carb)) + "g",
        },
        "per_100g": {
            "kcal":      str(round(p100_kcal)),
            "protein":   str(round(p100_prot)) + "g",
            "fett":      str(round(p100_fat))  + "g",
            "kolhydrat": str(round(p100_carb)) + "g",
        },
        "portion_g":  round(portion_g),
        "calculated": True,
    }


def _parse_servings(s) -> int:
    if not s:
        return 4
    m = re.search(r'(\d+)', str(s))
    return max(1, int(m.group(1))) if m else 4


# ── Fallbacks ──────────────────────────────────────────────────────────────────
NUTRITION_FALLBACKS = {
    "Varmrätt":  {"per_portion":{"kcal":"490","protein":"34g","fett":"19g","kolhydrat":"40g"},
                  "per_100g":   {"kcal":"140","protein":"10g","fett":"5g", "kolhydrat":"11g"}},
    "Huvudrätt": {"per_portion":{"kcal":"490","protein":"34g","fett":"19g","kolhydrat":"40g"},
                  "per_100g":   {"kcal":"140","protein":"10g","fett":"5g", "kolhydrat":"11g"}},
    "Förrätt":   {"per_portion":{"kcal":"185","protein":"10g","fett":"10g","kolhydrat":"14g"},
                  "per_100g":   {"kcal":"130","protein":"7g", "fett":"7g", "kolhydrat":"10g"}},
    "Snacks":    {"per_portion":{"kcal":"210","protein":"8g", "fett":"13g","kolhydrat":"18g"},
                  "per_100g":   {"kcal":"300","protein":"11g","fett":"19g","kolhydrat":"26g"}},
    "Dessert":   {"per_portion":{"kcal":"340","protein":"5g", "fett":"14g","kolhydrat":"48g"},
                  "per_100g":   {"kcal":"290","protein":"4g", "fett":"12g","kolhydrat":"41g"}},
    "Bakverk":   {"per_portion":{"kcal":"290","protein":"5g", "fett":"12g","kolhydrat":"42g"},
                  "per_100g":   {"kcal":"340","protein":"6g", "fett":"14g","kolhydrat":"49g"}},
    "Frukost":   {"per_portion":{"kcal":"390","protein":"16g","fett":"14g","kolhydrat":"50g"},
                  "per_100g":   {"kcal":"175","protein":"7g", "fett":"6g", "kolhydrat":"22g"}},
    "Tillbehör": {"per_portion":{"kcal":"180","protein":"3g", "fett":"7g", "kolhydrat":"26g"},
                  "per_100g":   {"kcal":"150","protein":"3g", "fett":"6g", "kolhydrat":"22g"}},
    "Sås":       {"per_portion":{"kcal":"95", "protein":"1g", "fett":"8g", "kolhydrat":"4g"},
                  "per_100g":   {"kcal":"200","protein":"3g", "fett":"18g","kolhydrat":"8g"}},
    "Dryck":     {"per_portion":{"kcal":"140","protein":"0g", "fett":"0g", "kolhydrat":"14g"},
                  "per_100g":   {"kcal":"100","protein":"0g", "fett":"0g", "kolhydrat":"10g"}},
}


if __name__ == "__main__":
    tests = [
        {"title": "Aperol Spritz",
         "servings": "1 person",
         "ingredients": ["▪️Prosecco 3 parts","▪️Aperol 2 parts","▪️Splash of soda","▪️Orange slice and ice"]},
        {"title": "Negroni",
         "servings": "1 person",
         "ingredients": ["▪️Gin - 30ml","▪️Campari - 30ml","▪️Sweet Vermouth - 30ml","▪️Orange peel"]},
        {"title": "Espresso Martini",
         "servings": "1 person",
         "ingredients": ["▪️Vodka - 50ml","▪️Kahlúa - 20ml","▪️Fresh espresso - 30ml","▪️Simple syrup - 10ml"]},
        {"title": "Spaghetti Carbonara",
         "servings": "4 portioner",
         "ingredients": ["400g spaghetti","200g guanciale","4 äggulor","100g pecorino","Svartpeppar"]},
        {"title": "Vitlökssmör",
         "servings": "8 portioner",
         "ingredients": ["200g smör","4 vitlöksklyftor","2 msk hackad persilja","1 citron (zest)"]},
    ]

    for t in tests:
        r = calculate_nutrition(t)
        if r:
            pp = r['per_portion']
            p100 = r['per_100g']
            print(f"\n{t['title']} ({r['portion_g']}g/portion):")
            print(f"  Per portion: {pp['kcal']} kcal  P:{pp['protein']}  F:{pp['fett']}  K:{pp['kolhydrat']}")
            print(f"  Per 100g:    {p100['kcal']} kcal  P:{p100['protein']}  F:{p100['fett']}  K:{p100['kolhydrat']}")
        else:
            print(f"\n{t['title']}: Ingen matchning")
