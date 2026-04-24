import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import re
import streamlit as st

# --- AVISO DE EXTRAÇÃO ---
# Nota: A extração de PDFs depende da estrutura do arquivo. 
# Se os números não forem detectados, verifique se o PDF tem texto selecionável.

def extrair_dados_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
            
            # Buscando padrões de porcentagem (OTDA, Extravio, Devolução)
            # Adaptado para encontrar valores como 97.9%, 0.8% etc.
            pct_matches = re.findall(r'(\d{1,2}[,.]\d)%', texto)
            
            # Buscando números inteiros (Volume de Envios)
            # Filtra números grandes que costumam ser o volume de pacotes
            vol_matches = re.findall(r'\b(\d{2,4})\b', texto)
            
            return {
                "texto": texto,
                "otda": [float(x.replace(',', '.')) for x in pct_matches if float(x.replace(',', '.')) > 50][:4],
                "qualidade": [float(x.replace(',', '.')) for x in pct_matches if float(x.replace(',', '.')) < 15],
                "envios": [int(x) for x in vol_matches if 20 < int(x) < 5000][:4]
            }
    except Exception as e:
        st.error(f"Erro na leitura do PDF: {e}")
        return None

def main():
    st.title("🚀 Automação CS: Dashboard de Performance")
    st.warning("⚠️ AVISO: A extração de dados de PDF pode conter erros dependendo da formatação do arquivo bruto.")

    col1, col2 = st.columns(2)
    with col1:
        csv_file = st.file_uploader("Suba o CSV de Tickets", type="csv")
    with col2:
        pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if csv_file and pdf_file:
        # Processamento
        dados_pdf = extrair_dados_pdf(pdf_file)
        
        # Exemplo de lógica para gerar o gráfico unificado
        # [Aqui você insere a função de plotagem com Matplotlib que criamos anteriormente]
        
        st.success("Dados processados! Verifique se os valores batem com o PDF antes de exportar.")
        # st.pyplot(fig)

if __name__ == "__main__":
    main()
