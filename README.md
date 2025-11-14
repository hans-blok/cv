# CV HTML Builder

Bouw je CV als statische HTML-pagina op basis van eenvoudige tekstbestanden (voor opdrachten/werkervaring en opleidingen). Je kunt ook afbeeldingen toevoegen, zoals een header-logo en een profielfoto.

WAAROM
- Versiebeheer met Git: elke wijziging aan je CV is traceerbaar.
- Losse contentbestanden: schrijf in plain text, presentatie gebeurt in HTML.
- Eenvoudig hosten via GitHub Pages (optioneel).

FEATURES

Content uit tekstbestanden voor:

- Opdrachten / werkervaring
- Opleidingen

Ondersteuning voor afbeeldingen:

logo-header.* – logo linksbovenaan de pagina
profille-photo.* – foto in je profielsectie
DE BESTANDEN MOETEN AAN HET DEZE NAAMGEVING VOLDOEN. Geaccepteerd worden .jpg en .png bestanden.

MAPPENSTRUCTUUR

Het CV kan worden opgebouwd als de volgende mappen zijn gevuld met .txt-bestanden.
.
├─ index.html    
├─ /logos/          # twee afbeeldinge (logo-header.* en profile-photo.*)
├─ /personal/       # een tekstbestand met je persoonlijke gegevens
├─ /career-summary/ # een tekstbestand dat helpt om de lezer snel een beeld te geven van je profiel
├─ /certifications/ # een tekstbestand je certificerigen
├─ /engagements/    # tekstbestanden met opdrachten/werkervaring (per opdracht een bestand)
├─ /education/      # een tekstbestand met je gevolgde opleidingen
├─ /courses/        # een tekstbestand met gevolgde cursussen en certificerigen
