import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import re
import streamlit as st

# Função de suporte para garantir que as listas tenham o tamanho correto
def ajustar_lista(lista, tamanho=4):
    return (lista + [0.0] * tamanho)[:tamanho]

def extrair_dados_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
            
            # Captura porcentagens e volumes
            pct_matches = re.findall(r'(\d{1,2}[,.]\d)%', texto)
            pct_values = [float(x.replace(',', '.')) for x in pct_matches]
            vol_matches = re.findall(r'\b(\d{2,4})\b', texto)
            vol_values = [int(x) for x in vol_matches if 20 < int(x) < 5000]
            
            return {
                "otda": ajustar_lista([x for x in pct_values if x > 50]),
                "extravio": ajustar_lista([x for x in pct_values if 0 <= x < 2]),
                "devolucao": ajustar_lista([x for x in pct_values if 2 <= x < 15]),
                "envios": ajustar_lista(vol_values)
            }
    except Exception as e:
        st.error(f"Erro técnico na extração do PDF: {e}")
        return None

def main():
    st.set_page_config(page_title="Gerador de Performance CS", layout="wide")
    st.title("🚀 Automação CS: Dashboard de Performance")
    st.warning("⚠️ AVISO: Verifique se os dados extraídos abaixo conferem com o PDF.")

    col1, col2 = st.columns(2)
    with col1:
        excel_file = st.file_uploader("Suba o Relatório de Tickets (Excel)", type="xlsx")
    with col2:
        pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if excel_file and pdf_file:
        # Lendo o Excel
        df_tkt = pd.read_excel(excel_file, engine='openpyxl')
        
        # Localizando a linha SUM (coluna Ocorrência é a terceira - índice 2)
        row_sum = df_tkt[df_tkt.iloc[:, 2].astype(str).str.strip().str.upper() == 'SUM']
        
        if row_sum.empty:
            st.error("Linha 'SUM' não encontrada no Excel.")
            return

        # Captura de Tickets (Colunas F, I, L, O do seu modelo)
        tickets_mes = [row_sum.iloc[0, 5], row_sum.iloc[0, 8], row_sum.iloc[0, 11], row_sum.iloc[0, 14]]
        
        dados_pdf = extrair_dados_pdf(pdf_file)

        if dados_pdf:
            fig, ax1 = plt.subplots(figsize=(12, 7))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Gráfico de Barras (Envios)
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios', color='gray', fontweight='bold')
            for i, v in enumerate(dados_pdf['envios']):
                ax1.text(i, v + 2, str(v), ha='center', color='gray', fontsize=9)
            
            # Gráfico de Linhas (Percentuais)
            ax2 = ax1.twinx()
            ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            tkt_rate = ajustar_lista([(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, dados_pdf['envios'])])
            ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            # Adicionando os Rótulos de Porcentagem (%)
            for i in range(4):
                ax2.text(i, dados_pdf['otda'][i] + 4, f"{dados_pdf['otda'][i]}%", color='#1A237E', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
                ax2.text(i, tkt_rate[i] + 4, f"{tkt_rate[i]:.1f}%", color='#E65100', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
                ax2.text(i, dados_pdf['extravio'][i] - 10, f"{dados_pdf['extravio'][i]}%", color='#B71C1C', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
                ax2.text(i, dados_pdf['devolucao'][i] - 20, f"{dados_pdf['devolucao'][i]}%", color='#4A148C', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

            ax2.set_ylim(-25, 115)
            ax1.legend(loc='upper left', fontsize=9)
            ax2.legend(loc='upper right', fontsize=9)
            plt.title("Performance Logística Unificada", fontsize=14, fontweight='bold')
            
            st.pyplot(fig)
            st.success("Gráfico gerado com sucesso!")

if __name__ == "__main__":
    main()
