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

load_dotenv()
SENHA_DASH = os.getenv("DASH_PASS")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.title("🔐 RESTRITO")
    senha_input = st.text_input("Digite a senha de acesso:", type="password")

    if st.button("Entrar"):
        if senha_input == SENHA_DASH:  # Substitua pela sua senha
            st.session_state["autenticado"] = True
            st.success("✅ Acesso liberado!")
            st.rerun()
    #if st.session_state["autenticado"]:
        #st.write("✅ Acesso liberado!")
        else:
            st.error("❌ Senha incorreta. Tente novamente.")
    st.stop()

titulo = st.empty()
col1, = st.columns(1)
with col1:
    titulo.markdown(
        f"""
        <div style="text-align: center; font-size: 100px;">
            <h1>📊Acompanhamento de Vendas Outubro</h1>
        </div>
        """,
        unsafe_allow_html=True
    )


count = st_autorefresh(interval=120*1000, key="meta_refresh")

img_path = Path("TrioCIDG.jpg")

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
creds = ServiceAccountCredentials.from_json_keyfile_name("metadevenda-9750bb128912.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = "MetaVendas"   # nome da planilha
sheet = client.open(SHEET_NAME).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")  # Linux/Mac
except:
    locale.setlocale(locale.LC_TIME, "portuguese")

#meses = df["mes"].tolist()
#mes_atual = st.sidebar.selectbox("Selecione o mês:", meses)

df['mes_normalizado'] = df['mes'].str.strip().str.capitalize()
meses = df['mes_normalizado'].dropna().unique()
meses.sort()  # opcional: ordem cronológica

mes_atual = st.sidebar.selectbox("Selecione o mês:", meses)
titulo.title(f"📊Acompanhamento de Vendas - {mes_atual}")


# Filtra usando o mês normalizado

df_mes = df[df["mes_normalizado"] == mes_atual]

if df_mes.empty:
    st.warning("❌ Nenhum dado encontrado para o mês selecionado.")
    st.stop()

meta_valor = float(df_mes["meta"].iloc[0])



realizado_valor = df_mes["venda"].astype(float).sum()


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
            <div style="text-align: center; font-size: 65px; font-weight: bold;
                    color: {'lightgreen' if progresso >= 1 else 'orange' if progresso >= 0.5 else 'red'};">
            {progresso*100:.2f}%
            </div>
             """,
        
            unsafe_allow_html=True
        )
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(    
            f"""
            <div style="text-align: center; font-size: 60px;">
                Realizado: {realizado_fmt} 
            </div>
             """,
        
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(    
            f"""
            <div style="text-align: center; font-size: 60px; color: lightblue;">
            Esperado: {valor_esperado_fmt}
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
        <div style="text-align: right;">
            <h2>Tempo decorrido</h2>
            <p style="font-size:50px; font-weight:; color:white;">
            {progresso_tempo*100:.1f}%     
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    with col3:
        st.markdown(
        f"""
        <div style="text-align: left;">
            <h2>Valor para atingir meta</h2>
            <p style="font-size:50px; font-weight:; color:white;">
                {format_currency(faltante, "BRL", locale="pt_BR")}
            </p>
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
        st.progress(progresso_vendas)

    
else:
    st.warning("Defina uma meta para começar 🚀")