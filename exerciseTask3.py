import pandas as pd
import streamlit as st

# --- Leitura do arquivo ---
file_path = "Base tarefa 3 - 2025.2.xlsx"
df = pd.read_excel(file_path, header=None)

# Como está a tendência de público atendido ao longo do tempo;

# --- Tratamento ---
# Inicia A partir da linha 2 temos os dados (linha 0 e 1 são cabeçalhos desorganizados) descartando essas linhas. Seleciona todos os dados a partir da terceira linha (índice 2), descartando os cabeçalhos inúteis.
# Limpa e reinicia o índice para 0, 1, 2, 3..., descartando os números de índice originais.
dados = df.iloc[2:].reset_index(drop=True)

# Renomear a primeira coluna para "Dia"
dados = dados.rename(columns={0: "Dia"})

# Ttransformar colunas em linhas
dados_long = dados.melt(id_vars=["Dia"], var_name="Semana", value_name="Publico")

# --- Tratamento Semanal ---
# A partir da linha 2 temos os dados (linha 0 e 1 são cabeçalhos desorganizados)
dados = df.iloc[2:].reset_index(drop=True)

# Renomear a primeira coluna para "Dia"
dados = dados.rename(columns={0: "Dia"})

# Remover valores nulos e converter para número
dados_long = dados_long.dropna(subset=["Publico"])
dados_long["Publico"] = pd.to_numeric(dados_long["Publico"], errors="coerce")

# Criar índice de tempo fictício (semana 1, 2, 3...)
dados_long["Semana"] = dados_long.groupby("Dia").cumcount() + 1

# Agregar por semana (soma do público atendido)
tendencia_semanal = dados_long.groupby("Semana")["Publico"].sum().reset_index()


# Tratando o Afrupamento por mês (4 semanas = 1 mês)

# Função para mapear a semana para o mês
def mapear_mes(semana):
    if 1 <= semana <= 4:
        return "Janeiro"
    elif 5 <= semana <= 8:
        return "Fevereiro"
    elif 9 <= semana <= 12:
        return "Março"
    elif 13 <= semana <= 16:
        return "Abril"
    return "Outro"

# Criar a coluna "Mês" no DataFrame semanal, aplicando a função mapear_mes
tendencia_semanal["Mês"] = tendencia_semanal["Semana"].apply(mapear_mes)

# Agrupar por Mês e somar o público
tendencia_mensal = tendencia_semanal.groupby("Mês")["Publico"].sum().reset_index()

# Ordenar os meses para a exibição correta (Janeiro, Fevereiro, Março, Abril)
ordem_meses = ["Janeiro", "Fevereiro", "Março", "Abril"]
tendencia_mensal["Mês"] = pd.Categorical(tendencia_mensal["Mês"], categories=ordem_meses, ordered=True)
tendencia_mensal = tendencia_mensal.sort_values("Mês").reset_index(drop=True)


# --- Streamlit ---
st.title("📊 Tendência de Público Atendido")

opcao = st.sidebar.selectbox(
    "Selecione Opção",
    ("1. Tendência de Público por Semana",
     "2. Tendência de Público por Semanas",
     "3. Tendência de Público por Mês (4 Semanas/Mês)",
     "4.Gráfico de Público Total por Mês",
     "5. Gráfico de Barras por Semana")
)


# --- VISUALIZAÇÃO SEMANAL ---
if opcao == "1. Tendência de Público por Semana":
    st.subheader("1. Tendência de Público por Semana")
    st.dataframe(tendencia_semanal[["Mês","Semana", "Publico"]])
# Gráfico de linha semanal
elif opcao == "2. Tendência de Público por Semanas":
    st.subheader("2. Tendência de Público por Semanas)")
    st.line_chart(tendencia_semanal.set_index("Semana")["Publico"])

# --- VISUALIZAÇÃO MENSAL ---
elif opcao == "3. Tendência de Público por Mês (4 Semanas/Mês)":
    st.subheader("3. Tendência de Público por Mês (4 Semanas/Mês)")
    st.dataframe(tendencia_mensal)

# Gráfico de barras mensal
elif opcao == "4.Gráfico de Público Total por Mês":
    st.subheader("4.Gráfico de Público Total por Mês")
    st.bar_chart(tendencia_mensal.set_index("Mês")["Publico"])

# Gráfico de barras semanal (opcional)
elif opcao == "5. Gráfico de Barras por Semana":
    st.subheader("5. Gráfico de Barras por Semana")
    st.bar_chart(tendencia_semanal.set_index("Semana")["Publico"])








