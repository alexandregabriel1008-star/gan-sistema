# =====================================================
# DATABASE - SUPABASE (PROFISSIONAL)
# =====================================================

from supabase import create_client
from datetime import datetime
import os

# =====================================================
# CONFIG
# =====================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Variáveis SUPABASE não configuradas")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================================
# INIT
# =====================================================
def init_db():
    # Supabase já gerencia isso
    pass


# =====================================================
# SALVAR DOCUMENTO
# =====================================================
def salvar_documento(
    usuario_id,
    tipo,
    cliente,
    caminho=None,
    status="REVISAO",
    setor=None
):
    try:
        res = supabase.table("documentos").insert({
            "usuario_id": usuario_id,
            "tipo": tipo,
            "cliente": cliente,
            "caminho": caminho,
            "status": status,
            "setor": setor,
            "criado_em": datetime.utcnow().isoformat()
        }).execute()

        return {"ok": True, "data": res.data}

    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================================================
# HISTÓRICO (COMPATÍVEL COM APP)
# =====================================================
def salvar_historico(dados: dict):
    return salvar_documento(
        usuario_id=dados.get("usuario"),
        tipo="CONTRATO",
        cliente=dados.get("cliente"),
        caminho=dados.get("arquivo"),
        status=dados.get("status", "REVISAO"),
        setor=dados.get("setor")
    )


# =====================================================
# LISTAR DOCUMENTOS
# =====================================================
def listar_documentos(usuario_id=None):
    try:
        query = supabase.table("documentos").select("*")

        if usuario_id:
            query = query.eq("usuario_id", usuario_id)

        res = query.order("criado_em", desc=True).execute()

        return res.data if res.data else []

    except Exception:
        return []


def listar_historico(usuario=None):
    return listar_documentos(usuario)


# =====================================================
# DASHBOARD
# =====================================================
def listar_dashboard(usuario_id=None):
    dados = listar_documentos(usuario_id)

    dashboard = {
        "REVISAO": 0,
        "ASSINADO": 0,
        "CONCLUIDO": 0,
        "TOTAL": 0
    }

    for d in dados:
        dashboard["TOTAL"] += 1
        status = d.get("status")

        if status in dashboard:
            dashboard[status] += 1

    return dashboard