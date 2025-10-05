import os

engagements_dir = "engagements"
logo_path = "logos/logo-header.jpg"

def parse_engagement(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
    
    data = {}
    current_key = None
    current_value = []

    for line in lines:
        if line.isupper() and not line.startswith("•"):
            if current_key:
                data[current_key] = "\n".join(current_value).strip()
            current_key = line.strip()
            current_value = []
        else:
            current_value.append(line)
    
    if current_key:
        data[current_key] = "\n".join(current_value).strip()

    # Periode uit bestandsnaam halen
    filename = os.path.basename(file_path)
    periode = filename.replace("opdracht_", "").replace(".txt", "").replace("_", " – ")
    data = {"PERIODE": periode, **data}  # Zorg dat PERIODE altijd bovenaan staat

    return data

def extract_year(filename):
    parts = filename.replace(".txt", "").split("_")
    for part in reversed(parts):
        if part.isdigit():
            return int(part)
    return 0

tables_html = ""
for filename in sorted(os.listdir(engagements_dir), key=extract_year, reverse=True):
    if filename.endswith(".txt"):
        filepath = os.path.join(engagements_dir, filename)
        engagement_data = parse_engagement(filepath)

        table_rows = "".join(
            f"<tr><td class='label'>{key}</td><td><div class='tekstblok'>{value}</div></td></tr>"
            for key, value in engagement_data.items()
        )

        tables_html += f"<table>{table_rows}</table><br><br>"

html_content = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <title>CV - Werkervaring</title>
    <style>
        @font-face {{
            font-family: 'Univers';
            src: local('Univers'), local('Arial');
        }}
        body {{
            font-family: 'Univers', Arial, sans-serif;
            font-size: 10pt;
            color: black;
            margin: 40px;
            background-color: #ffffff;
        }}
        .logo {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 75px;
        }}
        h1 {{
            font-weight: bold;
            margin-top: 120px;
            margin-bottom: 40px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        td {{
            vertical-align: top;
            padding: 10px;
            border-bottom: 1px solid #ccc;
        }}
        td.label {{
            width: 25%;
            font-weight: bold;
        }}
        .tekstblok {{
            white-space: pre-wrap;
            font-family: inherit;
            margin: 0;
            text-indent: -0.5em;
            padding-left: 0.5em;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <img src="{logo_path}" alt="Logo" class="logo" />
    <h1>Werkervaring</h1>
    {tables_html}
</body>
</html>
"""

with open("cv.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML-CV gegenereerd als 'cv.html'")
