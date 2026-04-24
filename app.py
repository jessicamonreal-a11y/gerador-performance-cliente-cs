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
            
            # Captura OTDA e Qualidade baseada em faixas de valores
            pct_matches = re.findall(r'(\d{1,2}[,.]\d)%', texto)
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
    st.set_page_config(page_title="Gerador de Performance CS", layout="wide")
    st.title("🚀 Automação CS: Relatório Excel + PDF")
    
    st.info("Suba o arquivo .xlsx original (sem converter para CSV) e o PDF operacional.")

    col1, col2 = st.columns(2)
    with col1:
        excel_file = st.file_uploader("Suba o Relatório de Tickets (Excel)", type="xlsx")
    with col2:
        pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if excel_file and pdf_file:
        # Lendo o Excel (engine openpyxl é necessária)
        df_tkt = pd.read_excel(excel_file)
        
        # Localiza a linha 'SUM' (Totais)
        # No seu arquivo, a coluna 'Ocorrência' é a terceira (índice 2)
        row_sum = df_tkt[df_tkt.iloc[:, 2].astype(str).str.strip().str.upper() == 'SUM']
        
        if row_sum.empty:
            st.error("Não encontrei a linha 'SUM' na coluna de Ocorrências. Verifique o arquivo Excel.")
            return

        # Mapeamento fixo das colunas de 'Tickets' baseados no seu modelo
        try:
            tickets_mes = [
                row_sum.iloc[0, 5],  # Janeiro Tickets (Coluna F)
                row_sum.iloc[0, 8],  # Fevereiro Tickets (Coluna I)
                row_sum.iloc[0, 11], # Março Tickets (Coluna L)
                row_sum.iloc[0, 14]  # Abril Tickets (Coluna O)
            ]
        except Exception as e:
            st.error(f"Erro ao ler as colunas de tickets: {e}")
            return

        dados_pdf = extrair_dados_pdf(pdf_file)

        if dados_pdf and len(dados_pdf['envios']) >= 4:
            fig, ax1 = plt.subplots(figsize=(12, 7))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Plotagem Barras
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios', fontweight='bold')
            
            # Plotagem Linhas
            ax2 = ax1.twinx()
            ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            # Taxa de Tickets
            tkt_rate = [(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, dados_pdf['envios'])]
            ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets/Envios')
            
            ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            ax2.set_ylim(-15, 115)
            
            # Rótulos de dados (Data Labels)
            for i in range(4):
                ax2.text(i, dados_pdf['otda'][i] + 3, f"{dados_pdf['otda'][i]}%", ha='center', fontweight='bold', color='#1A237E')
                ax2.text(i, tkt_rate[i] + 3, f"{tkt_rate[i]:.1f}%", ha='center', fontweight='bold', color='#E65100')
                ax2.text(i, dados_pdf['extravio'][i] - 8, f"{dados_pdf['extravio'][i]}%", ha='center', color='#B71C1C')
                ax2.text(i, dados_pdf['devolucao'][i] - 15, f"{dados_pdf['devolucao'][i]}%", ha='center', color='#4A148C')

            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.title(f"Performance Consolidada", fontsize=14, fontweight='bold')
            
            st.pyplot(fig)
            st.success("Dashboard gerado com sucesso!")
        else:
            st.error("Erro ao extrair dados do PDF. Verifique se os gráficos estão legíveis no arquivo.")

if __name__ == "__main__":
    main()
