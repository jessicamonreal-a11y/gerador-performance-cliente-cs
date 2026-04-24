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
    st.title("🚀 Automação CS: Dashboard de Performance")
    
    csv_file = st.file_uploader("Suba o CSV de Tickets", type="csv")
    pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if csv_file and pdf_file:
        df_tkt = pd.read_csv(csv_file)
        
        # FILTRO DE SEGURANÇA: Localiza a linha SUM ignorando maiúsculas/minúsculas
        row_sum = df_tkt[df_tkt.iloc[:, 2].str.strip().str.upper() == 'SUM']
        
        if row_sum.empty:
            st.error("Não encontrei a linha 'SUM' na terceira coluna do CSV. Verifique o arquivo.")
            return

        # BUSCA POR POSIÇÃO: Janeiro costuma ser a 6ª coluna (índice 5), 
        # Fevereiro a 9ª (índice 8), Março a 12ª (índice 11) e Abril a 15ª (índice 14)
        # conforme a estrutura do seu arquivo bruto.
        try:
            tickets_mes = [
                row_sum.iloc[0, 5],  # Janeiro Tickets
                row_sum.iloc[0, 8],  # Fevereiro Tickets
                row_sum.iloc[0, 11], # Março Tickets
                row_sum.iloc[0, 14]  # Abril Tickets
            ]
        except Exception as e:
            st.error(f"Erro ao mapear colunas do CSV: {e}. Verifique se o formato do relatório mudou.")
            return

        dados_pdf = extrair_dados_pdf(pdf_file)

        if dados_pdf and len(dados_pdf['envios']) == 4:
            fig, ax1 = plt.subplots(figsize=(12, 7))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # Eixo 1: Envios
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios')
            
            # Eixo 2: Percentuais
            ax2 = ax1.twinx()
            ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            # Cálculo da Taxa de Tickets baseado nos valores extraídos
            tkt_rate = [(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, dados_pdf['envios'])]
            ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            
            ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            ax2.set_ylim(-15, 115)
            
            # Adicionando rótulos para garantir que nada fique invisível
            for i in range(4):
                ax2.text(i, dados_pdf['otda'][i] + 3, f"{dados_pdf['otda'][i]}%", ha='center', color='#1A237E', fontweight='bold')
                ax2.text(i, tkt_rate[i] + 3, f"{tkt_rate[i]:.1f}%", ha='center', color='#E65100', fontweight='bold')
                ax2.text(i, dados_pdf['extravio'][i] - 7, f"{dados_pdf['extravio'][i]}%", ha='center', color='#B71C1C', fontweight='bold')
                ax2.text(i, dados_pdf['devolucao'][i] - 14, f"{dados_pdf['devolucao'][i]}%", ha='center', color='#4A148C', fontweight='bold')

            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.title("Performance Logística Unificada")
            
            st.pyplot(fig)
            st.success("Gráfico gerado com sucesso!")
        else:
            st.error("O PDF não contém dados suficientes ou o formato não foi reconhecido.")

if __name__ == "__main__":
    main()
