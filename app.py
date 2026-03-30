# =====================================================
# GAN SISTEMA CONTÁBIL (WEB + SUPABASE AUTH)
# =====================================================

import streamlit as st

st.set_page_config(
    page_title="GAN Sistema Contábil",
    layout="wide"
)

import os
import pandas as pd
from datetime import datetime
from supabase import create_client

# =====================================================
# 🔗 SUPABASE
# =====================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================================
# PLOTLY
# =====================================================
try:
    import plotly.express as px
    PLOTLY_OK = True
except:
    PLOTLY_OK = False

# =====================================================
# IMPORTS DO SISTEMA
# =====================================================
from document_utils import gerar_documento
from pdf_utils import gerar_pdf
from database import salvar_historico, listar_historico, init_db

# =====================================================
# CONFIG
# =====================================================
BASE_DIR = os.getcwd()
BASE_OUTPUT = os.path.join(BASE_DIR, "output")
TEMPLATES_CONTRATOS = os.path.join(BASE_DIR, "templates", "CONTRATOS")

for p in [BASE_OUTPUT, TEMPLATES_CONTRATOS]:
    os.makedirs(p, exist_ok=True)

init_db()

# =====================================================
# FUNÇÕES
# =====================================================
def listar_templates(pasta):
    if not os.path.exists(pasta):
        return []
    return [f for f in os.listdir(pasta) if f.endswith(".docx")]

# =====================================================
# 🔐 LOGIN SUPABASE
# =====================================================
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🔐 Acesso ao Sistema")

    tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])

    # LOGIN
    with tab1:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": senha
                })

                st.session_state.user = res.user
                st.success("Login realizado 🚀")
                st.rerun()

            except:
                st.error("Email ou senha inválidos")

    # CADASTRO
    with tab2:
        email_c = st.text_input("Email novo")
        senha_c = st.text_input("Senha", type="password")
        senha_c2 = st.text_input("Confirmar Senha", type="password")

        if st.button("Criar Conta"):
            if senha_c != senha_c2:
                st.error("Senhas não conferem")
            else:
                try:
                    supabase.auth.sign_up({
                        "email": email_c,
                        "password": senha_c
                    })
                    st.success("Conta criada com sucesso 🚀")
                except:
                    st.error("Erro ao criar conta")

    st.stop()

# =====================================================
# USUÁRIO LOGADO
# =====================================================
USER = st.session_state.user
USUARIO_ID = USER.id
EMAIL = USER.email

# =====================================================
# MENU + LOGOUT
# =====================================================
st.sidebar.write(f"👤 {EMAIL}")

if st.sidebar.button("Sair"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.radio("Menu", [
    "📊 Dashboard",
    "📄 Gerar Contrato",
    "🏢 Clientes",
    "📚 Histórico",
    "⚙️ Configurações"
])

# =====================================================
# 📊 DASHBOARD
# =====================================================
if menu == "📊 Dashboard":
    st.subheader("Dashboard")

    df = pd.DataFrame(listar_historico())

    if df.empty:
        st.info("Sem dados")
        st.stop()

    df = df[df["usuario"] == USUARIO_ID].copy()
    df["criado_em"] = pd.to_datetime(df["criado_em"], errors="coerce")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total", len(df))
    c2.metric("Revisão", len(df[df["status"] == "REVISAO"]))
    c3.metric("Concluído", len(df[df["status"] == "CONCLUIDO"]))

    if PLOTLY_OK:
        fig = px.bar(
            df.groupby(df["criado_em"].dt.date)
            .size()
            .reset_index(name="q"),
            x="criado_em",
            y="q"
        )
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 📄 GERAR CONTRATO
# =====================================================
elif menu == "📄 Gerar Contrato":
    st.subheader("Gerar Contrato")

    templates = listar_templates(TEMPLATES_CONTRATOS)

    if not templates:
        st.warning("Envie um template DOCX")
        st.stop()

    template = st.selectbox("Template", templates)
    nome_cliente = st.text_input("Nome do Cliente")

    if st.button("Gerar"):
        if not nome_cliente:
            st.warning("Informe o cliente")
            st.stop()

        with st.spinner("Gerando contrato..."):
            pasta = os.path.join(BASE_OUTPUT, USUARIO_ID, nome_cliente)
            os.makedirs(pasta, exist_ok=True)

            caminho_template = os.path.join(TEMPLATES_CONTRATOS, template)
            caminho_saida = os.path.join(pasta, f"{nome_cliente}.docx")

            gerar_documento(caminho_template, caminho_saida, {})
            gerar_pdf(caminho_saida)

            salvar_historico({
                "usuario": USUARIO_ID,
                "cliente": nome_cliente,
                "status": "CONCLUIDO",
                "criado_em": datetime.now().isoformat()
            })

        st.success("Contrato gerado com sucesso 🚀")

# =====================================================
# 🏢 CLIENTES
# =====================================================
elif menu == "🏢 Clientes":
    st.subheader("Cadastro de Clientes")

    nome = st.text_input("Nome")
    cpf = st.text_input("CPF/CNPJ")
    telefone = st.text_input("Telefone")
    email = st.text_input("Email")

    if st.button("Salvar Cliente"):
        if not nome or not cpf:
            st.warning("Nome e CPF/CNPJ são obrigatórios")
            st.stop()

        data = {
            "usuario_id": USUARIO_ID,
            "nome": nome,
            "cpf_cnpj": cpf,
            "telefone": telefone,
            "email": email
        }

        with st.spinner("Salvando..."):
            res = supabase.table("clientes").insert(data).execute()

        if res.data:
            st.success("Cliente salvo com sucesso 🚀")
        else:
            st.error("Erro ao salvar cliente")

    st.divider()
    st.subheader("Clientes cadastrados")

    lista = supabase.table("clientes")\
        .select("*")\
        .eq("usuario_id", USUARIO_ID)\
        .execute()

    if lista.data:
        for c in lista.data:
            st.write(f"👤 {c['nome']} - {c['cpf_cnpj']}")
    else:
        st.info("Nenhum cliente cadastrado")

# =====================================================
# 📚 HISTÓRICO
# =====================================================
elif menu == "📚 Histórico":
    st.subheader("Histórico")

    base_user = os.path.join(BASE_OUTPUT, USUARIO_ID)

    if not os.path.exists(base_user):
        st.info("Sem histórico")
        st.stop()

    for pasta in os.listdir(base_user):
        st.write(pasta)

# =====================================================
# ⚙️ CONFIG
# =====================================================
elif menu == "⚙️ Configurações":
    st.subheader("Templates")

    arq = st.file_uploader("Upload DOCX", type=["docx"])

    if arq:
        with open(os.path.join(TEMPLATES_CONTRATOS, arq.name), "wb") as f:
            f.write(arq.read())

        st.success("Template enviado com sucesso")