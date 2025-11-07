import streamlit as st
import pandas as pd
import locale
from babel.numbers import format_currency
from datetime import datetime
from pathlib import Path
import base64
from calendar import monthrange
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
import hashlib
import json


st.set_page_config(layout="wide")

def connect_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive",
               "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file"]
    creds_dict = json.loads(st.secrets["creds_json"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    #creds = ServiceAccountCredentials.from_json_keyfile_name(GSHEET_CREDS_PATH, scope)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def get_sheet(sheet_name="MetaVendas", worksheet_name="SalvaDado"):
    client = connect_gsheets()
    sheet = client.open(sheet_name)
    return sheet.worksheet(worksheet_name) #abre a pagina pelo nome
# ---------------- Configuração ----------------
load_dotenv()
USER1_HASH = hashlib.sha256(os.getenv("PASS1").encode()).hexdigest()
USER2_HASH = hashlib.sha256(os.getenv("PASS2").encode()).hexdigest()

usuarios = {os.getenv("USER1"): USER1_HASH,
            os.getenv("USER2"): USER2_HASH}

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
GSHEET_CREDS_PATH = os.getenv("GSHEET_CREDS_PATH")
#print("EMAIL_USER:", os.getenv("EMAIL_USER"))
#print("EMAIL_PASS (len):", None if os.getenv("EMAIL_PASS") is None else len(os.getenv("EMAIL_PASS")))

def enviar_email_gmail(usuario):

    remetente = EMAIL_USER
    senha_de_app = EMAIL_PASS
    destinatario = EMAIL_USER

    msg = MIMEMultipart("alternative")
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = 'Recuperação de Senha'
    corpo_email = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f0f2f5; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
          <h2 style="color: #2E86C1;">Recuperação de Senha</h2>
          <p>O usuário <strong>{usuario}</strong> solicitou a recuperação de senha.</p>
          <p>Se você não reconhece esta solicitação, ignore este e-mail.</p>
          <hr>
          <p style="font-size: 12px; color: #999999;">Este é um e-mail automático. Não responda.</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(corpo_email, 'html'))  
    with smtplib.SMTP('smtp.gmail.com', 587) as server: 
        server.ehlo()
        server.starttls()
        server.login(remetente, senha_de_app)
        server.send_message(msg)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- Lógica de login ----------------
if not st.session_state.logged_in:
    img_path = Path(__file__).parent/"TrioCSE.jpg"

# Converte imagem em base64
    def get_base64_of_image(image_file):
        with open(image_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    img_base64 = get_base64_of_image(img_path)

# Aplica fundo no Streamlit
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            height:100vh
            overflow: hidden;
    }}
    .login-box {{
        position: fixed;
        bottom: 10%;
        right: 20px;
        width: 300px;
        padding: 20px;
        background-color: rgba(255,255,255,0.95);
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.25);
    }}
    </style>
    """,
    unsafe_allow_html=True)

    for _ in range(20):
        st.write("")
    col1, col2 = st.columns([4,4])
    with col2:
        st.subheader("LOGIN")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        
        if "senha_errada" not in st.session_state:
            st.session_state.senha_errada = False

        if st.button("Entrar"):
                
                hash_digitada = hashlib.sha256(senha.encode()).hexdigest()
                hash_armazenada = usuarios.get(usuario)

                if hash_armazenada and hash_digitada == hash_armazenada:
                    st.session_state.logged_in = True
                    st.session_state.senha_errada = False
                    st.success(f"✅ Bem-vindo, {usuario}!")
                
                else:
                    st.session_state.senha_errada = True
                    st.session_state.logged_in = False
                    st.error("❌ Usuário ou senha inválidos")
                
        if st.session_state.senha_errada: 
            if st.button("Esqueci a senha"):
                enviar_email_gmail(usuario)
                st.info("✅ Pedido enviado ao administrador!")
                st.session_state.senha_errada = False
        

    

# ---------------- Área protegida ----------------
else:
    st.set_page_config(layout="wide")
    img_path = Path(__file__).parent / "TrioCIDG.jpg"
# Converte imagem em base64
    def get_base64_of_image(image_file):
        with open(image_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    img_base64 = get_base64_of_image(img_path)

# Aplica fundo no Streamlit
    st.markdown(
        f"""
        <style>
        .stApp {{
             background-image: url("data:image/png;base64,{img_base64}");
             background-size: cover;
             background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
    }}
    .login-box {{
        position: fixed;
        bottom: 10%;
        right: 10%;
        width: 100%;
        max-width:300px;
        padding: 20px;
        background-color: rgba(255,255,255,0.95);
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.25);
    }}
    </style>
    """,
    unsafe_allow_html=True)
    #st.sidebar.header("Filtros")
    #periodo = st.sidebar.selectbox("Agrupar por:", ["Horário","Dia","Mês"])
    #mostrar_meta = st.sidebar.checkbox("Mostrar Meta", value=True)

    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"logged_in": False}))

    col1, col2 = st.columns([2, 4])
    with col1:
        if st.session_state.logged_in:
            st.markdown(
            """
        <style>
        /* Labels dos inputs */
        label[data-testid="stWidgetLabel"] > div {
        font-size: 20px !important;
        font-weight: bold;
        color: white;
        }

            /* Texto digitado nos inputs */
        input, select, textarea {
        font-size: 18px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
        )

            st.markdown(
        """
        <style>
        .fade-message {
        animation: fadeOut 4s forwards;
        }
        @keyframes fadeOut {
            0% {opacity: 1;}
            70% {opacity: 1;}
            100% {opacity: 0; display: none;}
        }
        </style>
        <div class="fade-message">
            <p style="color: green; font-size:18px; font-weight: bold;">
             ✅ Bem-vindo! Você está logado
            </p>
        </div>
        """,
            unsafe_allow_html=True
            )
            st.title("➕ Inserir Dados de Vendas")

            mes = st.selectbox("Selecione o mês:", ["Outubro", "Novembro", "Dezembro"])
            meta = st.number_input("Meta do mês", min_value=0, step=100)
            st.markdown(
            """
                <div style="text-align: center; font-size: 26px; font-weight:; color: white;">
                    📊 Insira a venda realizada
                </div>
            """,
                unsafe_allow_html=True
             )
            evento = st.text_input("Nome do evento")
            realizado = st.number_input("Valor vendido", min_value=0, step=100)
            vendedor = st.text_input("Nome do vendedor")
            venda = realizado

            if st.button("Salvar"):
                sheet = get_sheet("MetaVendas", "SalvaDado")
                registro = str(datetime.now())
                data = [mes, meta, venda, vendedor, evento, registro]
                sheet.append_row(data)
                st.success(
                    f"✅ Dados salvos: {mes} | Meta: {meta} | Realizado: {venda} "
                    f"| Vendedor: {vendedor} | Evento: {evento}"
                )
    with col2:

        sheet = get_sheet("MetaVendas", "SalvaDado")
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)

        if not df.empty:
        # converter colunas em numéricas
            df["meta"] = pd.to_numeric(df["meta"], errors="coerce")
            df["venda"] = pd.to_numeric(df["venda"], errors="coerce")
            df["registro"] = pd.to_datetime(df["registro"], errors="coerce")

        

       #agrupar por mês
            resumo = df.rename(columns={"registro": "dia"})
          
        #resumo = df.groupby(df["registro"].dt.date).agg({
            #}).reset_index()

            resumo.rename(columns={"registro": "dia"}, inplace=True)
            resumo["dia"]=pd.to_datetime(resumo["dia"], errors="coerce")
            resumo = resumo.sort_values(by="dia")

            fig = px.line(
            resumo, 
            x="dia", 
            y=["meta", "venda"], 
            #barmode = "group",
            labels={"value":"R$ (Reais)", "variable":"Legenda"},
            title="📈 Meta vs Realizado - Tendência Diária de Vendas"
    )
            fig.update_traces(mode="lines+markers", line=dict(width=4))
            #fig.update_traces(width=10.5)   
            fig.update_layout(
                height=635,
                title={
                    "x":0.5,
                    "xanchor":"center",
                    "font": dict(size=22, color ="#FFFFFF", family="Arial")
                },
                legend=dict(
                    title ="Meta",
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    
                    xanchor="center",
                    x=0.5,
                    font=dict(color="black", size=14)
                ),
                plot_bgcolor="#2C2A2A",
                paper_bgcolor="#0E0D0D",
                font=dict(color="white"),
                yaxis_tickprefix="R$ ",
                hovermode="x unified",
                margin=dict(l=40, r=40, t=80, b=80)   
            )
            st.markdown(
                "<div style='display: flex; justify-content: center;'>",unsafe_allow_html=True
            )
            st.plotly_chart(fig, use_container_width=True)  # False pra não expandir
            st.markdown("</div>", unsafe_allow_html=True)
                    
        else:
            st.info("Ainda não há dados no Google Sheets.")