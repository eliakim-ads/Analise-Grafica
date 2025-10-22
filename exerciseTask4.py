import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# CONFIGURAÇÕES
# r é indicação de string bruta e evita dar problema com as barras.
caminho_completo = r"Base tarefa 3 - 2025.2.xlsx"
dias_uteis_semana = 5
atendimentos_por_dia = 10  # cada médico faz 10 atendimentos por dia útil

# Carga e prepração
df = pd.read_excel(caminho_completo, header=2)
df = df.rename(columns={'Unnamed: 0': 'Dia_Semana'})

# melt: cada linha representará um dia da semana para uma determinada "sem X"
df_long = pd.melt(df, id_vars=['Dia_Semana'], var_name='Semana', value_name='Consultas')
df_long['Semana_Num'] = df_long['Semana'].str.replace('sem ', '').astype(int)

# Calcular totais semanais reais (1..16) para a tendência
df_tendencia = df_long.groupby('Semana_Num')['Consultas'].sum().reset_index()

# regressão linear usando os dados reais (1..16)
slope, intercept, r_value, p_value, std_err = linregress(df_tendencia['Semana_Num'], df_tendencia['Consultas'])

# preparar projeção para semanas 17..32 (NOVO)
semana_proj = np.arange(17, 33)
consultas_proj = slope * semana_proj + intercept
df_proj = pd.DataFrame({'Semana_Num': semana_proj, 'Consultas': consultas_proj})

# unir REAL (1..16) + PROJEÇÃO (17..32) para análise combinada (Novo)
df_total = pd.concat([df_tendencia[['Semana_Num', 'Consultas']], df_proj], ignore_index=True)
df_total = df_total.sort_values('Semana_Num').reset_index(drop=True)

# função número de médicos por semana (política de contratação)(Novo)
def medicos_por_semana(sem):
    if sem < 17:
        return 3
    elif 17 <= sem < 19:
        return 4
    else:
        return 5

# aplicar médicos e capacidade semanal para gráficos comparativos)(novo)
df_total['Medicos'] = df_total['Semana_Num'].apply(medicos_por_semana)
df_total['Capacidade_Semanal'] = df_total['Medicos'] * dias_uteis_semana * atendimentos_por_dia

"""
Calcular Consultas_Extras: comparar por dia, depois agregar por semana
pra isso precisamos da capacidade diária vigente na semana (medicos * atendimentos_por_dia)
usamos df_long (dados por dia) e juntamos a lógica de medicos_por_semana

"""
df_long['Medicos'] = df_long['Semana_Num'].apply(medicos_por_semana)
df_long['Capacidade_Diaria'] = df_long['Medicos'] * atendimentos_por_dia

# extras por linha (por dia): se Consultas > Capacidade_Diaria então diferença, (novo)
df_long['Consultas_Extra_Dia'] = np.where(df_long['Consultas'] > df_long['Capacidade_Diaria'],
                                          df_long['Consultas'] - df_long['Capacidade_Diaria'],
                                          0)

# agregar por semana (soma das diferenças diárias) -> isso gera os mesmos números do gráfico (Novo)
df_extras_semanais = df_long.groupby('Semana_Num')['Consultas_Extra_Dia'].sum().reset_index()
df_extras_semanais = df_extras_semanais.rename(columns={'Consultas_Extra_Dia': 'Consultas_Extras'})

"""
Juntar os extras ao df_total: para semanas projetadas (17-32) não temos dia-a-dia real; vamos estimar extras usando a demanda projetada
assumindo mesma distribuição diária média: comparar demanda semanal projetada com capacidade semanal.

"""
df_total = df_total.merge(df_extras_semanais, on='Semana_Num', how='left')

# preencher NaN nas semanas projetadas (17..32) calculando por diferença semanal (Novo)
mask_proj = df_total['Consultas_Extras'].isna()
df_total.loc[mask_proj, 'Consultas_Extras'] = np.where(
    df_total.loc[mask_proj, 'Consultas'] > df_total.loc[mask_proj, 'Capacidade_Semanal'],
    df_total.loc[mask_proj, 'Consultas'] - df_total.loc[mask_proj, 'Capacidade_Semanal'],
    0)

# para segurança arredondar/convertar pra inteiro (NOVO)
df_total['Consultas_Extras'] = df_total['Consultas_Extras'].round(0).astype(int)


# elaboração dos Graficos

# Tendência (reais 1-16) + projeção (17-32) — mantendo a tendência desde a semana 1 (NOVO)
plt.figure(figsize=(10, 6))
# pontos reais 1..16
plt.plot(df_total[df_total['Semana_Num'] <= 16]['Semana_Num'],
         df_total[df_total['Semana_Num'] <= 16]['Consultas'],
         'o-', label='Consultas Reais (Semanas 1–16)')
# projeção 17..32
plt.plot(df_total[df_total['Semana_Num'] >= 17]['Semana_Num'],
         df_total[df_total['Semana_Num'] >= 17]['Consultas'],
         '--', label='Projeção (Semanas 17–32)')

# opcional: mostrar linha de regressão estendida (continua desde a semana 1 até 32)
semana_range_full = np.arange(df_total['Semana_Num'].min(), 33)
plt.plot(semana_range_full, slope * semana_range_full + intercept, ':', label='Linha de Tendência (regressão estendida)')
plt.title('Tendência de Público Atendido (Consultas Semanais) — Reais + Projeção até Semana 32')
plt.xlabel('Número da Semana')
plt.ylabel('Total de Consultas (semana)')
plt.legend()
plt.grid(True)
plt.show()

# 5.2 Demanda vs Capacidade (Capacidade mostrada como total semanal de atendimentos)
plt.figure(figsize=(10, 6))
plt.plot(df_total['Semana_Num'], df_total['Consultas'], marker='o', label='Demanda (Real + Proj)')
plt.plot(df_total['Semana_Num'], df_total['Capacidade_Semanal'], linestyle='--', marker='s', label='Capacidade Semanal (Medicos x dias x 10)')
plt.axvline(17, color='orange', linestyle=':', label='Entrada 4º Médico (semana 17)')
plt.axvline(19, color='red', linestyle=':', label='Entrada 5º Médico (semana 19)')
plt.title('Demanda x Capacidade (Semanas 1–32)')
plt.xlabel('Semana')
plt.ylabel('Consultas / Capacidade semanal')
plt.legend()
plt.grid(True)
plt.show()

# Consultas Extras (calculadas por excesso diário e agregadas por semana)
plt.figure(figsize=(10, 6))
plt.bar(df_total['Semana_Num'], df_total['Consultas_Extras'])
plt.title('Consultas Extras (Excesso Diário Agregado por Semana) — Semanas 1–32')
plt.xlabel('Número da Semana')
plt.ylabel('Consultas Extras (soma dos excessos diários)')
plt.xticks(df_total['Semana_Num'])
plt.grid(axis='y', linestyle='--')
plt.show()

# Resumo
print("\n--- RESUMO (Semanas 1–32) ---")
print(df_total[['Semana_Num', 'Medicos', 'Capacidade_Semanal', 'Consultas', 'Consultas_Extras']])

total_extra_real = df_total[df_total['Semana_Num'] <= 16]['Consultas_Extras'].sum()
total_extra_proj = df_total[df_total['Semana_Num'] >= 17]['Consultas_Extras'].sum()
print(f"\nTotal Extras (1–16, reais, agregado diário): {total_extra_real}")
print(f"Total Extras (17–32, projetados, estimativa agregada): {total_extra_proj}")
print(f"Total Geral Extras (1–32): {total_extra_real + total_extra_proj}")

