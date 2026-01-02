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
# 4️⃣ Generar gráfico tipo donut con colores personalizados
# ------------------------------
color_map = {
    "Bonds": "#bc8edc",
    "Gold": "#e6c165",
    "International stocks": "#69a0eb",
    "Domestic stocks": "#d8914f",
    "Remunerated account": "#7bbc8e",
    "Emerging markets": "#e06666"
}

fig = px.pie(
    summary,
    names='Category',
    values='Amount',
    hole=0.4,
    color='Category',
    color_discrete_map=color_map
)

# ------------------------------
# 5️⃣ Porcentajes fuera con línea guía
# ------------------------------
fig.update_traces(
    textinfo='percent',       # solo porcentaje
    textposition='outside',   # fuera del gráfico
    pull=[0]*len(summary),    # sin separación entre sectores
    marker=dict(line=dict(color='#191919', width=1)),  # bordes de los sectores finos
    showlegend=True
)

# ------------------------------
# 6️⃣ Fondo oscuro y leyenda limpia
# ------------------------------
fig.update_layout(
    paper_bgcolor="#191919",
    plot_bgcolor="#191919",
    font_color="white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
        # sin borde ni recuadro
    )
)

# ------------------------------
# 7️⃣ Guardar como HTML listo para Notion / GitHub Pages
# ------------------------------
fig.write_html("investment_chart.html", include_plotlyjs="cdn")

print("✅ Gráfico generado con porcentajes fuera, línea guía y leyenda limpia")