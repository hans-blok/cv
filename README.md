# CV HTML Builder
CV gerealiseerd met de CV HTML Builder

## Pages
https://hans-blok.github.io/cv/

## Lokaal starten

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.\serve.ps1
```

(of `serve.bat`). Open daarna http://127.0.0.1:8000/cv/cv.html. De pagina herlaadt automatisch bij wijzigingen in `docs/`.

Volledige build (site + PDF + DOCX): `.\build.ps1` (of `build.bat`).

---

## Inhoud aanpassen

Alle CV-inhoud staat in `docs/data/`. Wijzig de bestanden en genereer daarna opnieuw (zie onderaan).

### Persoonlijke gegevens — `docs/data/personal-data.yml`

```yaml
photo: assets/img/profile-photo.jpg   # pad naar profielfoto
fields:
  - label: Naam
    value: Johannes Blok
  - label: Functie
    value: IT-Architect
  - label: Beschikbaar per
    value: 1 september 2026
```

Voeg `label`/`value`-paren toe of verwijder ze naar wens.

### Persoonlijke tekst — `docs/data/personal-text.md`

Vrije Markdown-tekst die verschijnt in de sectie **PERSOONLIJK**.

### Opleidingen — `docs/data/educations.yml`

```yaml
- period: 1989–1995
  name: WO Algemene Economie
  institute: Erasmus Universiteit
  place: Rotterdam
  description: Korte omschrijving (optioneel).
```

### Cursussen — `docs/data/courses.yml` en `courses-short.yml`

```yaml
- period: '2024'
  items_text: Naam cursus, Instituut, Naam cursus 2, Instituut 2
```

Meerdere cursussen per jaar scheiden met een komma in `items_text`.  
`courses-short.yml` heeft dezelfde structuur en verschijnt onder **OVERIGE CURSUSSEN**.

### Certificeringen — `docs/data/certifications.yml`

Zelfde structuur als `educations.yml`.

### Opdrachten / werkervaring — `docs/data/engagements/`

Eén YAML-bestand per opdracht, bestandsnaam bepaalt de sorteervolgorde (bijv. `2026-heden.yml`):

```yaml
period: 2026 – heden
order: 20260101          # getal voor sortering (hoog = bovenaan)
organisation: Gemeente Utrecht
role: Solution Architect Common Ground
activities: |-
  - Werkzaamheid 1.
  - Werkzaamheid 2.
achievements: |-
  - Prestatie 1.
keywords: Common Ground, GEMMA, PSA
```

Nieuw bestand toevoegen = nieuwe opdracht. Verwijder het bestand om de opdracht te verwijderen.

### Afbeeldingen

Zet in `docs/assets/img/`:
- `logo-header.*` — logo linksboven in de sidebar (`.jpg` of `.png`)
- `profile-photo.*` — profielfoto (.jpg` of `.png`)

---

## PDF en DOCX genereren

Gebruik de VS Code-taak **"Genereer PDF en DOCX"** (⇧⌘B of via *Terminal → Run Build Task*).

Dit voert `build.ps1` uit, dat:
1. De site bouwt (`mkdocs build`)
2. `docs/assets/cv.pdf` genereert via Chrome headless
3. `docs/assets/cv.docx` genereert
4. De site opnieuw bouwt zodat PDF en DOCX als download beschikbaar zijn

> **Let op:** sluit Adobe Acrobat (of een andere PDF-viewer) vóór het genereren — een open bestand blokkeert het overschrijven en geeft een foutmelding.

De gegenereerde bestanden staan in `docs/assets/` en worden meegenomen bij de volgende git-push.
