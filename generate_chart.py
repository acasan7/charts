import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import os
import json

# ------------------------------
# 1️⃣ Leer el Service Account desde la variable de entorno (Secret)
# ------------------------------
# GitHub Actions pondrá el contenido del JSON en la variable de entorno GOOGLE_SERVICE_ACCOUNT
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT")

if not service_account_info:
    raise ValueError("No se encontró la variable de entorno GOOGLE_SERVICE_ACCOUNT")

# Convertir el string JSON a diccionario
creds_dict = json.loads(service_account_info)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Crear credenciales desde diccionario
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# Conectar con Google Sheets
client = gspread.authorize(creds)

# ------------------------------
# 2️⃣ Abrir la hoja y leer los datos
# ------------------------------
sheet = client.open("Investments").sheet1  # Nombre exacto de tu Sheet
data = sheet.get_all_records()

# ------------------------------
# 3️⃣ Convertir a DataFrame y calcular porcentaje por categoría
# ------------------------------
df = pd.DataFrame(data)

total = df['Amount'].sum()
summary = df.groupby('Category', as_index=False)['Amount'].sum()
summary['Percentage'] = summary['Amount'] / total * 100

# ------------------------------
# 4️⃣ Generar gráfico interactivo tipo donut
# ------------------------------
fig = px.pie(
    summary,
    names='Category',
    values='Amount',
    title='Investment Allocation',
    hole=0.4
)
fig.update_traces(textinfo="percent+label")

# ------------------------------
# 5️⃣ Guardar como HTML listo para Notion / GitHub Pages
# ------------------------------
fig.write_html("investment_chart.html", include_plotlyjs="cdn")

print("✅ Gráfico generado en investment_chart.html")
