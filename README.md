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