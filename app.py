import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import re
import streamlit as st

def ajustar_lista(lista, tamanho=4):
    """Garante que a lista tenha o tamanho exato, cortando ou preenchendo com 0.0"""
    return (lista + [0.0] * tamanho)[:tamanho]

def extrair_dados_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
            
            # Captura todas as porcentagens do texto
            pct_matches = re.findall(r'(\d{1,2}[,.]\d)%', texto)
            pct_values = [float(x.replace(',', '.')) for x in pct_matches]
            
            # Captura volumes (números de 3 a 4 dígitos)
            vol_matches = re.findall(r'\b(\d{2,4})\b', texto)
            vol_values = [int(x) for x in vol_matches if 20 < int(x) < 5000]
            
            # Distribui os dados filtrando por faixas lógicas
            dados = {
                "otda": ajustar_lista([x for x in pct_values if x > 50]),
                "extravio": ajustar_lista([x for x in pct_values if 0 <= x < 2]),
                "devolucao": ajustar_lista([x for x in pct_values if 2 <= x < 15]),
                "envios": ajustar_lista(vol_values)
            }
            return dados
    except Exception as e:
        st.error(f"Erro técnico na extração do PDF: {e}")
        return None

def main():
    st.set_page_config(page_title="Gerador de Performance CS", layout="wide")
    st.title("🚀 Automação CS: Dashboard de Performance")
    
    excel_file = st.file_uploader("Suba o Relatório de Tickets (Excel)", type="xlsx")
    pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if excel_file and pdf_file:
        df_tkt = pd.read_excel(excel_file, engine='openpyxl')
        row_sum = df_tkt[df_tkt.iloc[:, 2].astype(str).str.strip().str.upper() == 'SUM']
        
        if row_sum.empty:
            st.error("Linha 'SUM' não encontrada.")
            return

        # Captura tickets (Coluna F, I, L, O)
        tickets_mes = [row_sum.iloc[0, 5], row_sum.iloc[0, 8], row_sum.iloc[0, 11], row_sum.iloc[0, 14]]
        
        dados_pdf = extrair_dados_pdf(pdf_file)

        if dados_pdf:
            fig, ax1 = plt.subplots(figsize=(12, 7))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Plotagem Segura (Garantindo que x e y tenham o mesmo tamanho)
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            
            ax2 = ax1.twinx()
            ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            # Cálculo de taxa evitando divisão por zero
            tkt_rate = ajustar_lista([(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, dados_pdf['envios'])])
            
            ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            ax2.set_ylim(-15, 115)
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
            st.pyplot(fig)
            st.success("Gráfico gerado! Note: Se os dados no PDF não foram lidos, os valores aparecem como 0.0.")

if __name__ == "__main__":
    main()
