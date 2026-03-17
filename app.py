import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Sistema CRM Pro", layout="wide")
ARQUIVO_BANCO = "clientes_crm.csv"

# --- 1. BANCO DE DADOS DE VENDAS (Exemplo para cruzamento) ---
vendas_exemplo = {
    'Nome': ['Joao Silva', 'Maria Oliveira', 'Joao Silva', 'Carlos Souza', 'Ana Costa', 'Fernanda Lima'],
    'Data_Venda': ['2026-03-10', '2026-03-15', '2025-11-20', '2025-10-05', '2026-03-16', '2026-01-10'],
    'Valor': [150.0, 200.0, 80.0, 50.0, 350.0, 500.0]
}
df_vendas = pd.DataFrame(vendas_exemplo)
df_vendas['Data_Venda'] = pd.to_datetime(df_vendas['Data_Venda'])

# --- 2. FUNÇÕES DE SUPORTE ---
def carregar_dados():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            return pd.read_csv(ARQUIVO_BANCO, encoding='latin-1')
        except:
            return pd.read_csv(ARQUIVO_BANCO, encoding='utf-8')
    # Retorna DataFrame vazio se arquivo não existir
    return pd.DataFrame(columns=['Nome', 'Contato', 'Data de Nascimento', 'Categoria', 'Endereco'])

def processar_segmentacao(df_clientes, df_vendas):
    hoje = datetime.now()
    vendas_resumo = df_vendas.groupby('Nome').agg(
        Ultima_Compra=('Data_Venda', 'max'),
        Total_Gasto=('Valor', 'sum'),
        Qtd_Pedidos=('Data_Venda', 'count')
    ).reset_index()
    
    df_final = pd.merge(df_clientes, vendas_resumo, on='Nome', how='left')
    df_final['Qtd_Pedidos'] = df_final['Qtd_Pedidos'].fillna(0)
    df_final['Total_Gasto'] = df_final['Total_Gasto'].fillna(0)
    df_final['Dias_Inativo'] = (hoje - pd.to_datetime(df_final['Ultima_Compra'])).dt.days
    
    def definir_status(row):
        if row['Qtd_Pedidos'] == 0: return "🆕 Lead (Sem compras)"
        elif row['Dias_Inativo'] > 90: return "⚠️ Inativo (> 3 meses)"
        elif row['Qtd_Pedidos'] >= 3: return "💎 Fiel"
        else: return "✅ Ativo"
            
    df_final['Classificacao'] = df_final.apply(definir_status, axis=1)
    return df_final

# Inicialização do estado da sessão
if 'df_crm' not in st.session_state:
    st.session_state['df_crm'] = carregar_dados()

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("🚀 CRM Analytics")
    pagina = st.radio("Navegação", ["📝 Cadastro", "⚡ Ações", "📊 Dashboards"])
    st.divider()
    st.info(f"💾 Registros locais: {len(st.session_state['df_crm'])}")

# --- 4. LÓGICA DAS PÁGINAS ---

if pagina == "📝 Cadastro":
    st.title("Cadastro de Clientes")
    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input('Nome Completo')
            contato = st.text_input('WhatsApp/E-mail')
        with col2:
            data_nasc = st.date_input('Data de Nascimento',
            value=datetime(1990, 1, 1),
            min_value=datetime(1920, 1, 1),
            max_value=datetime.now()
            )
            categoria = st.selectbox('Categoria', ['Varejo', 'Tecnologia', 'Saúde', 'Educação', 'Indústria'])
        
        endereco = st.text_area('Endereço Completo')
        if st.form_submit_button("Salvar Cliente"):
            if nome and contato:
                novo_dado = pd.DataFrame([[nome, contato, data_nasc, categoria, endereco]], 
                                         columns=['Nome', 'Contato', 'Data de Nascimento', 'Categoria', 'Endereco'])
                
                # Atualiza sessão e arquivo
                st.session_state['df_crm'] = pd.concat([st.session_state['df_crm'], novo_dado], ignore_index=True)
                st.session_state['df_crm'].to_csv(ARQUIVO_BANCO, index=False, encoding='utf-8') # Salvando em UTF-8 para o Cloud
                
                st.success(f"Sucesso! {nome} foi adicionado.")
                st.rerun()
            else:
                st.error("Campos Nome e Contato são obrigatórios.")

elif pagina == "⚡ Ações":
    st.title("Relatório Personalizado")
    df = processar_segmentacao(st.session_state['df_crm'], df_vendas)
    
    if df.empty:
        st.warning("Base de dados vazia. Cadastre clientes primeiro.")
    else:
        col_a1, col_a3, col_a2 = st.columns(3)
        with col_a1:
            filtro_status = st.multiselect("Status", options=df['Classificacao'].unique(), default=df['Classificacao'].unique())
        with col_a3:
            filtro_categoria = st.multiselect("Categoria", options=df['Categoria'].unique(), default=df['Categoria'].unique())
        with col_a2:
            busca = st.text_input("Buscar Nome")

        # AJUSTE: Filtros cumulativos (E não ou)
        df_filtrado = df[
            (df['Classificacao'].isin(filtro_status)) & 
            (df['Categoria'].isin(filtro_categoria))
        ]

        if busca:
            df_filtrado = df_filtrado[df_filtrado['Nome'].str.contains(busca, case=False)]

        st.dataframe(df_filtrado[['Nome', 'Contato','Categoria', 'Classificacao', 'Total_Gasto']], use_container_width=True)
        
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar Lista Filtrada (CSV)", data=csv, file_name="relatorio_crm.csv", mime="text/csv")

elif pagina == "📊 Dashboards":
    st.title("Painel de Indicadores")
    df_dash = processar_segmentacao(st.session_state['df_crm'], df_vendas)
    
    if df_dash.empty:
        st.info("Sem dados para exibir gráficos.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Faturamento Total", f"R$ {df_dash['Total_Gasto'].sum():,.2f}")
        
        # Métrica de ticket médio apenas de quem comprou
        ticket_medio = df_dash[df_dash['Total_Gasto'] > 0]['Total_Gasto'].mean()
        m2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}" if not pd.isna(ticket_medio) else "R$ 0,00")
        
        taxa_inativo = (len(df_dash[df_dash['Classificacao'].str.contains('Inativo')]) / len(df_dash) * 100)
        m3.metric("Taxa de Inativos", f"{taxa_inativo:.1f}%")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎯 Clientes por Segmento")
            df_counts = df_dash['Classificacao'].value_counts().reset_index()
            df_counts.columns = ['Status', 'Quantidade']
            
            fig_seg = px.bar(df_counts, x='Status', y='Quantidade', color='Status',
                             color_discrete_map={"💎 Fiel": "#1E88E5", "✅ Ativo": "#4CAF50", 
                                               "⚠️ Inativo (> 3 meses)": "#E53935", "🆕 Lead (Sem compras)": "#FB8C00"},
                             text_auto=True)
            fig_seg.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_seg, use_container_width=True)
            
        with c2:
            st.subheader("💰 Top 10 Clientes")
            top_10 = df_dash.nlargest(10, 'Total_Gasto')[['Nome', 'Total_Gasto']]
            fig_top = px.bar(top_10, x='Total_Gasto', y='Nome', orientation='h',
                             text_auto='.2s', color='Total_Gasto', color_continuous_scale='Blues')
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_top, use_container_width=True)
