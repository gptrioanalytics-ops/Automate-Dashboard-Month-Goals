import streamlit as st
import pandas as pd
import locale
from babel.numbers import format_currency
from datetime import datetime
from pathlib import Path
import base64
from calendar import monthrange
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import time
from dotenv import load_dotenv
import os
from streamlit_autorefresh import st_autorefresh
import json

st.set_page_config(layout="wide")

st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .main {
        zoom: 0.5;
    }
    .block-container {
        max-width: 100%;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)




count = st_autorefresh(interval=120*1000, key="meta_refresh")

img_path = Path(__file__).parent/"TrioCIDG.jpg"

# 5️⃣ Função para converter em base64
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_of_image(img_path)

#---------------------------------------------------
# 3️⃣ Aplica fundo no Streamlit
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        width: 100%;
        height: 100%;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)




#------conexão com Google Sheets----------------
scope = [ "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file"]
creds_dict = json.loads(st.secrets["creds_json"])
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SHEET_ID = st.secrets["SHEET_ID"]
SHEET_NAME = "SalvaDado"  
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)
print("Service Account:", creds_dict["client_email"])

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")  # Linux/Mac
except:
    locale.setlocale(locale.LC_TIME, "C")


#meses = df["mes"].tolist()
#mes_atual = st.sidebar.selectbox("Selecione o mês:", meses)

df['mes_normalizado'] = df['mes'].str.strip().str.capitalize()
meses = df['mes_normalizado'].dropna().unique()
meses.sort()  # opcional: ordem cronológica

mes_atual = st.sidebar.selectbox("Selecione o mês:", meses)

st.markdown(
    f"""
    <style>
    .fixed-title {{
        width: 100%;
        text-align: center;
        color: #FFFFFF;
        font-size: 60px;
        font-weight: ;
        padding: 20px 0 10px 0;
        margin-top: 10px;
    }}
    </style>

    <div class="fixed-title">
        📊 Acompanhamento de Vendas - {mes_atual}
    </div>
    """,
    unsafe_allow_html=True
)



# Filtra usando o mês normalizado

df_mes = df[df["mes_normalizado"] == mes_atual]

if df_mes.empty:
    st.warning("❌ Nenhum dado encontrado para o mês selecionado.")
    st.stop()

meta_valor = float(df_mes["meta"].iloc[0])



df_mes["venda"] = (
    df_mes["venda"]
    .astype(str)
    .str.replace(".", "", regex=False)        # tira separador de milhar
    .str.replace(",", ".", regex=False)        # troca vírgula por ponto
)

df_mes["venda"] = pd.to_numeric(df_mes["venda"], errors="coerce")

realizado_valor = df_mes["venda"].sum()


if meta_valor > 0:
    progresso = min(realizado_valor / meta_valor, 1.0)

    # Barra de progresso
    #st.progress(progresso)

    # Formatar valores em moeda
    meta_fmt = format_currency(meta_valor, "BRL", locale="pt_BR")
    realizado_fmt = format_currency(realizado_valor, "BRL", locale="pt_BR")
    hoje = datetime.now()
    ano, mes = hoje.year, hoje.month
    dias_no_mes = monthrange(ano, mes)[1]
    dia_atual = hoje.day

    progresso_tempo = dia_atual / dias_no_mes
    progresso_vendas = realizado_valor / meta_valor
    faltante = max(meta_valor - realizado_valor, 0)
    progresso_faltante =  faltante / meta_valor
    valor_esperado = (realizado_valor / progresso_tempo) if progresso_tempo > 0 else 0
    valor_esperado_fmt = format_currency(valor_esperado, "BRL", locale="pt_BR")

    #st.subheader(f"Meta: {meta_fmt} ")
    st.markdown(    
        f"""
        <div style="text-align: center; font-size: 60px; font-weight:; color: white;">
            Meta: {meta_fmt}
        </div>
        """,
        unsafe_allow_html=True
    )

    # KPI estilizado com HTML
    st.markdown(    
            f"""
            <div style="text-align: center; font-size: 75px; font-weight: bold;
                    color: {'lightgreen' if progresso >= 1 else 'orange' if progresso >= 0.5 else 'red'};">
             {progresso*100:.2f}% 
            </div>
             """,
        
            unsafe_allow_html=True
        )
    st.markdown(    
            f"""
            <div style="text-align: center; font-size: 70px;">
                Realizado: {realizado_fmt}
            </div>
             """,
        
            unsafe_allow_html=True
        )

  

    #st.subheader("Comparativo:")

    # KPIs lado a lado
    col1, col2, col3  = st.columns(3)
    with col1:
        st.markdown(
        f"""
        <div style="text-align: center;">
            <h2>Tempo decorrido</h2>
            <p style="font-size:50px; font-weight:; color:white;">
            {progresso_tempo*100:.1f}%     
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    with col2:
        st.markdown(
        f"""
        <div style="text-align: center;">
            <h2>Valor para atingir meta</h2>
            <p style="font-size:50px; text-align: center;font-weight:; color:white;">
                {format_currency(faltante, "BRL", locale="pt_BR")}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    df["registro"] = pd.to_datetime(df["registro"], errors="coerce")
    ultima_atualizacao = df["registro"].max()
    with col3:
    # Pegar a última atualização
        if pd.notnull(ultima_atualizacao):
            ultima_formatada = ultima_atualizacao.strftime("%d/%m/%Y %H:%M:%S")

            st.markdown(
                f"""
                    <div style="text-align: center; color: white;">
                        <h2>Última atualização</h2>
                    <p style="font-size:50px; text-align: center;font-weight:; color:white;">
                        {ultima_formatada}
                    </p>
                    </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                    <div style="text-align: center; color: white; font-size: 30px;">
                        Sem registros ainda
                    </div>
                """,
                unsafe_allow_html=True
            )



    # Barras de progresso
    #st.write("### Progresso")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <style = "font-size: 40px;">
        .stProgress > div > div > div > div {{
         background-color: white;
        }}
        </style>
        """, unsafe_allow_html=True)

    progresso_tempo_real = progresso_tempo
    progresso_vendas_real = progresso_vendas   

    with col2:
        #st.write("Tempo do mês")
        st.markdown(f"""
        <div style ="text-align: left; font-size: 40px;">
            <h2>Tempo do mês</h2>
        </div>
        """, unsafe_allow_html=True)

        st.progress(progresso_tempo)
        #st.write("Vendas realizadas")
        st.markdown(f"""
        <div style ="text-align: left; font-size: 40px;">
            <h2>Vendas Realizadas</h2>
        </div>
        """, unsafe_allow_html=True)

        st.progress(min(progresso_vendas, 1.0))
        st.write(f"{progresso_vendas_real * 100:.1f}% da meta")
    
else:
    st.warning("Defina uma meta para começar 🚀")