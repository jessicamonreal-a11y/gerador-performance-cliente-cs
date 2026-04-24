# ... (mantenha as funções ajustar_lista e extrair_dados_pdf como estão)

        if dados_pdf:
            fig, ax1 = plt.subplots(figsize=(12, 7))
            meses = ['Jan', 'Fev', 'Mar', 'Abr']
            
            # 1. Barras de Envios
            ax1.bar(meses, dados_pdf['envios'], color='#CFD8DC', alpha=0.5, label='Qtd Envios')
            ax1.set_ylabel('Volume de Envios', fontweight='bold', color='gray')
            for i, v in enumerate(dados_pdf['envios']):
                ax1.text(i, v + 2, str(v), ha='center', color='gray', fontsize=9)
            
            # 2. Eixo de Percentuais
            ax2 = ax1.twinx()
            ax2.set_ylabel('Performance / Qualidade (%)', fontweight='bold')
            
            # Plotagem das linhas
            l1, = ax2.plot(meses, dados_pdf['otda'], marker='o', color='#1A237E', label='OTDA (%)', linewidth=3)
            
            tkt_rate = ajustar_lista([(t / e) * 100 if e > 0 else 0 for t, e in zip(tickets_mes, dados_pdf['envios'])])
            l2, = ax2.plot(meses, tkt_rate, marker='s', color='#E65100', linestyle='--', label='% Tickets')
            
            l3, = ax2.plot(meses, dados_pdf['extravio'], marker='^', color='#B71C1C', label='% Extravio')
            l4, = ax2.plot(meses, dados_pdf['devolucao'], marker='v', color='#4A148C', label='% Devolução')
            
            # 3. Lógica para escrever as % no gráfico (Labels)
            for i in range(4):
                # OTDA (Sempre acima do ponto)
                ax2.text(i, dados_pdf['otda'][i] + 3, f"{dados_pdf['otda'][i]}%", 
                         color='#1A237E', fontweight='bold', ha='center',
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))
                
                # Tickets (Sempre acima do ponto)
                ax2.text(i, tkt_rate[i] + 3, f"{tkt_rate[i]:.1f}%", 
                         color='#E65100', fontweight='bold', ha='center',
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))
                
                # Extravio (Abaixo do ponto)
                ax2.text(i, dados_pdf['extravio'][i] - 7, f"{dados_pdf['extravio'][i]}%", 
                         color='#B71C1C', fontweight='bold', ha='center',
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))
                
                # Devolução (Mais abaixo ainda para não bater no extravio)
                ax2.text(i, dados_pdf['devolucao'][i] - 14, f"{dados_pdf['devolucao'][i]}%", 
                         color='#4A148C', fontweight='bold', ha='center',
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

            ax2.set_ylim(-20, 115)
            ax1.legend(loc='upper left', fontsize=9)
            ax2.legend(loc='upper right', fontsize=9)
            plt.title("Performance Logística Unificada - Q1 2026", fontsize=14, fontweight='bold')
            
            st.pyplot(fig)
