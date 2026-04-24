import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import re
import streamlit as st

def extrair_dados_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
            
            # Busca OTDA (valores altos) e Qualidade (valores baixos)
            pct_matches = re.findall(r'(\d{1,2}[,.]\d)%', texto)
            # Busca Volumes (números de 3 a 4 dígitos)
            vol_matches = re.findall(r'\b(\d{3,4})\b', texto)
            
            return {
                "otda": [float(x.replace(',', '.')) for x in pct_matches if float(x.replace(',', '.')) > 50][:4],
                "extravio": [float(x.replace(',', '.')) for x in pct_matches if 0 <= float(x.replace(',', '.')) < 2][:4],
                "devolucao": [float(x.replace(',', '.')) for x in pct_matches if 2 <= float(x.replace(',', '.')) < 15][:4],
                "envios": [int(x) for x in vol_matches][:4]
            }
    except Exception as e:
        st.error(f"Erro na leitura do PDF: {e}")
        return None

def main():
    st.title("🚀 Automação CS: Dashboard de Performance")
    st.warning("⚠️ AVISO: Verifique se os dados extraídos abaixo conferem com o PDF.")

    csv_file = st.file_uploader("Suba o CSV de Tickets", type="csv")
    pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if csv_file and pdf_file:
        dados_pdf = extrair_dados_pdf(pdf_file)
        
        # Processar CSV de Tickets
        df_tkt = pd.read_csv(csv_file)
        df_tkt.columns = [col.replace('\n', ' ') for col in df_tkt.columns]
        row_sum = df_tkt[df_tkt['Ocorrência'].str.strip() == 'SUM'].iloc[0]
        tickets_mes = [row_sum['Janeiro Tickets'], row_sum['Fevereiro Tickets'], 
                       row_sum['Março Tickets'], row_sum['Abril Tickets']]

        if dados_pdf:
            # LÓGICA DE PLOTAGEM (O que faz o gráfico aparecer)
            fig, ax1 = plt.subplots(figsize=(12, 7))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Barras (Envios)
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios')
            
            # Linhas (Performance)
            ax2 = ax1.twinx()
            ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            # Cálculo % Tickets
            tkt_rate = [(t / e) * 100 for t, e in zip(tickets_mes, dados_pdf['envios'])]
            ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            
            ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            ax2.set_ylim(-15, 110)
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
            # O COMANDO MÁGICO DO STREAMLIT:
            st.pyplot(fig) 
            
            st.success("Gráfico gerado com sucesso!")

if __name__ == "__main__":
    main()
