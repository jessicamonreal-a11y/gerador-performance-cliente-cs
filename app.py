import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import re
import streamlit as st

def ajustar_lista(lista, tamanho=4):
    return (lista + [0.0] * tamanho)[:tamanho]

def extrair_dados_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
            
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
        st.error(f"Erro na extração do PDF: {e}")
        return None

def main():
    st.set_page_config(page_title="Gerador de Performance CS", layout="wide")
    st.title("🚀 Automação CS: Dashboard de Performance")

    # Painel Lateral para Configurações
    st.sidebar.header("Configurações")
    
    col1, col2 = st.columns(2)
    with col1:
        excel_file = st.file_uploader("Suba o Relatório de Tickets (Excel)", type="xlsx")
    with col2:
        pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if excel_file and pdf_file:
        df_tkt = pd.read_excel(excel_file, engine='openpyxl')
        
        # Tenta extrair o nome do cliente da primeira coluna/primeira linha do Excel
        nome_sugerido = str(df_tkt.iloc[0, 0]) if not df_tkt.empty else "Cliente"
        nome_cliente = st.sidebar.text_input("Nome do Cliente no Título:", value=nome_sugerido)
        
        row_sum = df_tkt[df_tkt.iloc[:, 2].astype(str).str.strip().str.upper() == 'SUM']
        
        if row_sum.empty:
            st.error("Linha 'SUM' não encontrada.")
            return

        tickets_mes = [row_sum.iloc[0, 5], row_sum.iloc[0, 8], row_sum.iloc[0, 11], row_sum.iloc[0, 14]]
        dados_pdf = extrair_dados_pdf(pdf_file)

        if dados_pdf:
            fig, ax1 = plt.subplots(figsize=(12, 8))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Barras (Envios)
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios', color='gray', fontweight='bold')
            for i, v in enumerate(dados_pdf['envios']):
                ax1.text(i, v + 5, str(v), ha='center', color='gray', fontsize=9)
            
            # Linhas (Percentuais)
            ax2 = ax1.twinx()
            ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            tkt_rate = ajustar_lista([(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, dados_pdf['envios'])])
            ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            # Rótulos Anti-Sobreposição
            for i in range(4):
                ax2.text(i, dados_pdf['otda'][i] + 5, f"{dados_pdf['otda'][i]}%", color='#1A237E', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
                ax2.text(i, tkt_rate[i] + 5, f"{tkt_rate[i]:.1f}%", color='#E65100', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
                ax2.text(i, -10, f"Ext: {dados_pdf['extravio'][i]}%", color='#B71C1C', fontweight='bold', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.7, edgecolor='#B71C1C', pad=1))
                ax2.text(i, -18, f"Dev: {dados_pdf['devolucao'][i]}%", color='#4A148C', fontweight='bold', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.7, edgecolor='#4A148C', pad=1))

            ax2.set_ylim(-30, 120)
            ax1.legend(loc='upper left', fontsize=9)
            ax2.legend(loc='upper right', fontsize=9)
            
            # TÍTULO DINÂMICO COM NOME DO CLIENTE
            plt.title(f"Performance Logística Unificada: {nome_cliente.upper()}", fontsize=15, fontweight='bold', pad=20)
            
            st.pyplot(fig)
            st.success(f"Dashboard gerado para {nome_cliente}!")

if __name__ == "__main__":
    main()
