"""Atualiza data.json a partir da planilha Performance_Showroom_Dados_Mensais (Google Sheets).
Roda automaticamente pelo GitHub Actions nos dias 03 e 15 de cada mês (ver .github/workflows/atualizar.yml).
A planilha precisa estar compartilhada como "Qualquer pessoa com o link: Leitor"."""
import csv, io, json, re, sys, unicodedata, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

SHEET_ID = "1xlHmxdtxSro1pBFfuVB8xkMlF_qTS6pU3IGGewdSVz0"
MESES = ["janeiro","fevereiro","marco","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]

def norm(s): return unicodedata.normalize("NFD", str(s)).encode("ascii","ignore").decode().strip().lower()

def baixar(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&headers=0&sheet={urllib.parse.quote(aba)}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return list(csv.reader(io.StringIO(r.read().decode("utf-8"))))

def num(x):
    s = re.sub(r"R\$|\s|%", "", str(x or ""))
    if not s: return None
    c, d = s.rfind(","), s.rfind(".")
    if c > -1 and d > -1: s = s.replace(".", "").replace(",", ".") if c > d else s.replace(",", "")
    elif c > -1: s = s.replace(",", "") if re.search(r",\d{3}$", s) else s.replace(",", ".")
    elif d > -1 and re.fullmatch(r"\d{1,3}(\.\d{3})+", s): s = s.replace(".", "")
    try: return float(s)
    except ValueError: return None

rows = []
for c in baixar("Dados Mensais"):
    if len(c) < 6 or not re.fullmatch(r"\s*20\d\d\s*", c[0] or ""): continue
    m = norm(c[1])
    if m not in MESES: continue
    v = [num(x) for x in c[2:6]]
    if any(x is None for x in v): continue
    rows.append([int(c[0]), MESES.index(m) + 1, int(v[0]), int(v[1]), int(v[2]), round(v[3], 2)])

if len(rows) < 12:
    sys.exit(f"Leitura falhou: só {len(rows)} meses encontrados. data.json não foi alterado.")

pct = json.load(open("data.json", encoding="utf-8")).get("pct", {})
try:
    pr = baixar("Premissas")
    anos = next(c for c in pr if any(re.fullmatch(r"\s*20\d\d\s*", x or "") for x in c))
    vals = next(c for c in pr if "comandas novas" in norm(c[0] if c else ""))
    for i, y in enumerate(anos):
        if re.fullmatch(r"\s*20\d\d\s*", y or "") and i < len(vals):
            v = num(vals[i])
            if v is not None: pct[y.strip()] = v / 100 if v > 1 else v
except Exception as e:
    print("Aviso: aba Premissas não lida, mantendo % anteriores:", e)

agora = datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="seconds")
json.dump({"updated": agora, "rows": rows, "pct": pct}, open("data.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"OK: {len(rows)} meses, último {rows[-1][1]:02d}/{rows[-1][0]}")
