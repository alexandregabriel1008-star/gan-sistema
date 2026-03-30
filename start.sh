#!/bin/bash

echo "🚀 Iniciando setup do ambiente..."

# Atualiza pacotes
apt-get update

# Instala LibreOffice (necessário para PDF)
apt-get install -y libreoffice

echo "✅ LibreOffice instalado"

# Inicia aplicação
echo "🚀 Iniciando Streamlit..."

streamlit run app.py --server.port=$PORT --server.address=0.0.0.0