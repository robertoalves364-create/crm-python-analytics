# crm-python-analytics
🚀 CRM Python Analytics
Este é um projeto de CRM (Customer Relationship Management) desenvolvido em Python, utilizando a biblioteca Streamlit para a interface web e Pandas para a inteligência de dados. O sistema permite o cadastro de clientes, segmentação automática baseada em comportamento de compra (RF) e visualização de indicadores de performance em tempo real.

🔗 (https://crm-python-analytics.streamlit.app/)

🛠️ Funcionalidades
📝 Cadastro de Clientes
Interface intuitiva para entrada de dados cadastrais.

Padronização de categorias (Varejo, Tecnologia, Saúde, etc.) para garantir a integridade da base de dados.

Persistência de dados em arquivo CSV.

⚡ Inteligência e Ações
Segmentação Automática: Cruzamento dinâmico entre a base de clientes e o histórico de vendas.

Classificação de Status:

💎 Fiel: Clientes com alta frequência de compra.

✅ Ativo: Clientes com compras recentes.

⚠️ Inativo: Clientes sem compras há mais de 90 dias (Churn).

🆕 Lead: Contatos cadastrados que ainda não realizaram compras.

Filtros Avançados: Segmentação por categoria, status e busca nominal para exportação de relatórios personalizados.

📊 Dashboards de Performance
Métricas de Faturamento Total e Ticket Médio.

Gráficos interativos (via Plotly) mostrando a saúde da carteira e o ranking dos principais clientes.

🧰 Tecnologias Utilizadas
Python 3.13

Streamlit: Framework para criação de web apps.

Pandas: Manipulação e análise de dados.

Plotly: Gráficos dinâmicos e interativos.

GitHub: Versionamento e Deploy.

🚀 Como executar o projeto localmente
Clone o repositório:

Bash
git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
Instale as dependências:

Bash
pip install -r requirements.txt
Execute o servidor do Streamlit:

Bash
streamlit run app.py
