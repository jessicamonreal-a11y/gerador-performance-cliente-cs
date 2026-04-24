import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import re
import streamlit as st

# Função para garantir que as listas tenham sempre 4 meses
def ajustar_lista(lista, tamanho=4):
    return (lista + [0.0] * tamanho)[:tamanho]

def extrair_dados_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
            
            # Busca todas as porcentagens
            pct_matches = re.findall(r'(\d{1,2}[,.]\d)%', texto)
            pct_values = [float(x.replace(',', '.')) for x in pct_matches]
            
            # Busca volumes (3 a 4 dígitos)
            vol_matches = re.findall(r'\b(\d{3,4})\b', texto)
            vol_values = [int(x) for x in vol_matches if 20 < int(x) < 5000]
            
            # Filtros por faixa para tentar organizar automaticamente
            return {
                "otda": [x for x in pct_values if x > 50][:4],
                "extravio": [x for x in pct_values if 0 <= x < 2][:4],
                "devolucao": [x for x in pct_values if 2 <= x < 15][:4],
                "envios": vol_values[:4]
            }
    except Exception as e:
        st.error(f"Erro na extração do PDF: {e}")
        return None

def main():
    st.set_page_config(page_title="Gerador de Performance CS", layout="wide")
    st.title("🚀 Automação CS: Dashboard de Performance")

    # Upload dos arquivos
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        excel_file = st.file_uploader("Suba o Relatório de Tickets (Excel)", type="xlsx")
    with col_up2:
        pdf_file = st.file_uploader("Suba o PDF Operacional", type="pdf")

    if excel_file and pdf_file:
        # 1. PROCESSAR EXCEL
        df_tkt = pd.read_excel(excel_file, engine='openpyxl')
        nome_sugerido = str(df_tkt.iloc[0, 0]) if not df_tkt.empty else "Cliente"
        row_sum = df_tkt[df_tkt.iloc[:, 2].astype(str).str.strip().str.upper() == 'SUM']
        
        if row_sum.empty:
            st.error("Linha 'SUM' não encontrada no Excel.")
            return
        
        tickets_mes = [row_sum.iloc[0, 5], row_sum.iloc[0, 8], row_sum.iloc[0, 11], row_sum.iloc[0, 14]]

        # 2. EXTRAÇÃO AUTOMÁTICA DO PDF
        dados_auto = extrair_dados_pdf(pdf_file)

        # 3. ÁREA DE AJUSTE MANUAL NA LATERAL
        st.sidebar.header("📝 Conferência de Dados")
        st.sidebar.write("Os valores abaixo foram lidos do PDF. Ajuste se estiverem errados:")
        
        cliente = st.sidebar.text_input("Nome do Cliente", value=nome_sugerido)
        
        # Inputs manuais pré-preenchidos com a extração automática
        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr']
        envios = []
        otda = []
        extravio = []
        devolucao = []

        for i, mes in enumerate(meses_labels):
            st.sidebar.subheader(f"Dados de {mes}")
            e = st.sidebar.number_input(f"Envios {mes}", value=int(dados_auto['envios'][i]) if i < len(dados_auto['envios']) else 0)
            o = st.sidebar.number_input(f"OTDA % {mes}", value=float(dados_auto['otda'][i]) if i < len(dados_auto['otda']) else 0.0, step=0.1)
            ext = st.sidebar.number_input(f"Extravio % {mes}", value=float(dados_auto['extravio'][i]) if i < len(dados_auto['extravio']) else 0.0, step=0.01)
            dev = st.sidebar.number_input(f"Devolução % {mes}", value=float(dados_auto['devolucao'][i]) if i < len(dados_auto['devolucao']) else 0.0, step=0.1)
            envios.append(e)
            otda.append(o)
            extravio.append(ext)
            devolucao.append(dev)

        # 4. GERAÇÃO DO GRÁFICO (Usando os dados da sidebar)
        if st.button("Gerar Gráfico Final"):
            fig, ax1 = plt.subplots(figsize=(12, 8))
            
            # Barras
            ax1.bar(meses_labels, envios, color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios', color='gray', fontweight='bold')
            for i, v in enumerate(envios):
                ax1.text(i, v + 5, str(v), ha='center', color='gray')

            # Linhas
            ax2 = ax1.twinx()
            ax2.plot(meses_labels, otda, marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            tkt_rate = [(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, envios)]
            ax2.plot(meses_labels, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            ax2.plot(meses_labels, extravio, marker='^', color='#B71C1C', label='% Extravio')
            ax2.plot(meses_labels, devolucao, marker='v', color='#4A148C', label='% Devolução')

            # Rótulos de dados inteligentes
            for i in range(4):
                ax2.text(i, otda[i] + 4, f"{otda[i]}%", color='#1A237E', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
                ax2.text(i, tkt_rate[i] + 4, f"{tkt_rate[i]:.1f}%", color='#E65100', fontweight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
                # Extravio e Devolução no "rodapé" do gráfico para evitar bagunça
                ax2.text(i, -12, f"Ext: {extravio[i]}%", color='#B71C1C', fontweight='bold', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8, edgecolor='#B71C1C', pad=1))
                ax2.text(i, -20, f"Dev: {devolucao[i]}%", color='#4A148C', fontweight='bold', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8, edgecolor='#4A148C', pad=1))

            ax2.set_ylim(-30, 120)
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.title(f"Performance Logística: {cliente.upper()}", fontsize=15, fontweight='bold', pad=20)
            
            st.pyplot(fig)
            st.success("Gráfico gerado com sucesso!")

if __name__ == "__main__":
    main()
