# =====================================================
# PDF UTILS - PROFISSIONAL (RENDER + WINDOWS)
# =====================================================

import subprocess
import time
import os
from pathlib import Path
import platform

# =====================================================
# DETECTAR LIBREOFFICE
# =====================================================
def get_libreoffice():
    sistema = platform.system()

    if sistema == "Windows":
        caminho = r"C:\Program Files\LibreOffice\program\soffice.exe"
        if Path(caminho).exists():
            return caminho
        else:
            raise RuntimeError("LibreOffice não encontrado no Windows.")

    # Linux / Render
    return "soffice"


# =====================================================
# GERAR PDF
# =====================================================
def gerar_pdf(
    caminho_docx: str,
    pasta_destino: str | None = None,
    cliente: str | None = None,
    tipo: str | None = None
) -> str:

    caminho_docx = Path(caminho_docx)

    if not caminho_docx.exists():
        raise RuntimeError(f"DOCX não encontrado: {caminho_docx}")

    libreoffice = get_libreoffice()

    pasta_saida = Path(pasta_destino) if pasta_destino else caminho_docx.parent
    pasta_saida.mkdir(parents=True, exist_ok=True)

    pdf_esperado = pasta_saida / f"{caminho_docx.stem}.pdf"

    tentativas = 3
    ultimo_erro = None

    for tentativa in range(1, tentativas + 1):
        try:
            comando = [
                libreoffice,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to", "pdf",
                str(caminho_docx),
                "--outdir", str(pasta_saida)
            ]

            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120
            )

            if resultado.returncode != 0:
                raise RuntimeError(
                    resultado.stderr.decode("utf-8", errors="ignore")
                )

            time.sleep(2)

            if not pdf_esperado.exists():
                raise RuntimeError("PDF não foi gerado.")

            return str(pdf_esperado)

        except Exception as e:
            ultimo_erro = str(e)
            time.sleep(2)

    raise RuntimeError(
        f"Erro ao gerar PDF após {tentativas} tentativas: {ultimo_erro}"
    )