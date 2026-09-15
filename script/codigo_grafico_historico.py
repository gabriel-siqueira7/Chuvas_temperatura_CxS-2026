### Projeto para visualização em gráfico do acumulado de chuvas X temperaturas de Caxias do Sul, comparando
### com a "Normal climatológica", padrão estipulado internacionalmente pela Organização Meteorológica Mundial/OMM (três décadas de dados climáticos)
### Média das três décadas retiradas do site do INMET: https://portal.inmet.gov.br/servicos/normais-climatológicas

### Os dados climáticos recentes (2026) utilizados neste projeto foram coletados pela estação meteorológica automática de **Criúva (B817)**. Para fins de análise comparativa, esses dados foram 
### cruzados com a **Normal Climatológica (1991-2020)** da estação convencional do **Aeroporto de Caxias do Sul (83942)**, visto que é a única série histórica centenária disponível no 
### município. Pequenas divergências milimétricas ou térmicas observadas nos gráficos são esperadas devido 
### às diferenças geográficas e de microclima entre o distrito rural e a zona urbana

# Dados públicos da Estação Meteorológica de Caxias do Sul - Criúva, retirados do site do INMET: https://portal.inmet.gov.br/servicos/bdmep-dados-históricos
# Desenvolvido por GABRIEL SIQUEIRA DOS SANTOS


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Configurações do arquivo
nome_arquivo = r'C:\Users\gasiq\Documents\DocumentosProjetos-Programacao-github\Chuvas_temperatura_CXS\cleaned\tabela.csv'

skip_rows = 0
with open(nome_arquivo, 'r', encoding='latin-1') as f:
    for i, linha in enumerate(f):
        if 'Data' in linha:
            skip_rows = i
            break

# 2. Carregar o arquivo CSV 
df = pd.read_csv(nome_arquivo, sep=';', skiprows=skip_rows, encoding='latin-1')
df.columns = df.columns.str.strip()

# 3. Extração dos nomes das colunas
col_data = df.columns[df.columns.str.contains('Data', case=False)][0]
col_max = df.columns[df.columns.str.contains('Temp.*Max', case=False)][0]
col_min = df.columns[df.columns.str.contains('Temp.*Min', case=False)][0]
col_chuva = df.columns[df.columns.str.contains('Chuva', case=False)][0]

# 4. Tratar datas e forçar conversão numérica
df[col_data] = pd.to_datetime(df[col_data], errors='coerce', dayfirst=True)

for col in [col_max, col_min, col_chuva]:
    df[col] = df[col].astype(str).str.replace(',', '.')
    df[col] = df[col].replace(['-9999', '-9999.0', 'nan', 'NaN', 'None'], np.nan)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Remover linhas inválidas e filtrar até a data atual para evitar o "futuro vazio"
df = df.dropna(subset=[col_data])
data_hoje = pd.to_datetime('today')
df = df[df[col_data] <= data_hoje]

# 5. Agrupamento Mensal
df['Ano_Mes'] = df[col_data].dt.to_period('M')
df['Numero_Mes'] = df[col_data].dt.month  # Extrai o número do mês (1 a 12)

df_mensal = df.groupby(['Ano_Mes', 'Numero_Mes']).agg({
    col_max: 'max',     
    col_min: 'min',     
    col_chuva: 'sum'    
}).reset_index()

df_mensal = df_mensal.sort_values('Ano_Mes')
df_mensal['Mes_Ano_Texto'] = df_mensal['Ano_Mes'].dt.strftime('%b/%y')

# =========================================================================
# MAPEAMENTO DA NORMAL CLIMATOLÓGICA HISTÓRICA (INMET 1991-2020)
# =========================================================================
medias_historicas = {
    1: {'Chuva_Med': 158.5, 'Temp_Max_Med': 27.2},  # Jan
    2: {'Chuva_Med': 154.9, 'Temp_Max_Med': 26.8},  # Fev
    3: {'Chuva_Med': 111.3, 'Temp_Max_Med': 25.4},  # Mar
    4: {'Chuva_Med': 120.4, 'Temp_Max_Med': 22.3},  # Abr
    5: {'Chuva_Med': 140.9, 'Temp_Max_Med': 18.5},  # Mai
    6: {'Chuva_Med': 156.0, 'Temp_Max_Med': 17.6},  # Jun
    7: {'Chuva_Med': 189.4, 'Temp_Max_Med': 16.9},  # Jul
    8: {'Chuva_Med': 134.0, 'Temp_Max_Med': 18.8},  # Ago
    9: {'Chuva_Med': 142.0, 'Temp_Max_Med': 19.8},  # Set
    10: {'Chuva_Med': 167.0, 'Temp_Max_Med': 22.2}, # Out
    11: {'Chuva_Med': 184.0, 'Temp_Max_Med': 24.6}, # Nov
    12: {'Chuva_Med': 200.0, 'Temp_Max_Med': 26.3}  # Dez
}

# Criando colunas de médias históricas com base no mês do dado
df_mensal['Chuva_Historica'] = df_mensal['Numero_Mes'].map(lambda x: medias_historicas[x]['Chuva_Med'])
df_mensal['Temp_Max_Historica'] = df_mensal['Numero_Mes'].map(lambda x: medias_historicas[x]['Temp_Max_Med'])

# 6. Configurar as posições no eixo X
indices = np.arange(len(df_mensal))  
largura_barra_chuva = 0.4  

# Criar a estrutura do gráfico com eixo duplo
fig, ax1 = plt.subplots(figsize=(13, 7)) 

# --- EIXO Y 1: Chuva (Barras e Linha de Média) ---
color_chuva = '#bce2e6'  
ax1.set_xlabel('Período (Mensal)', fontsize=12, fontweight='bold', labelpad=10)
ax1.set_ylabel('Chuva Acumulada no Mês (mm)', color='#4682B4', fontsize=11, fontweight='bold')

barras_chuva = ax1.bar(indices, df_mensal[col_chuva], 
                       width=largura_barra_chuva, color=color_chuva, alpha=0.7, label='Chuva Registrada (mm)')

# Linha de tendência/média da chuva histórica
linha_chuva_hist = ax1.plot(indices, df_mensal['Chuva_Historica'], color='#70a1a8', linewidth=2, 
                            linestyle='--', marker='x', label='Média Histórica Chuva (mm)')

ax1.tick_params(axis='y', labelcolor='#4682B4')
ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
ax1.set_ylim(0, max(df_mensal[col_chuva].max(), df_mensal['Chuva_Historica'].max()) * 1.35)

# --- EIXO Y 2: Temperaturas (Linhas e Linha de Média) ---
ax2 = ax1.twinx()  
ax2.set_ylabel('Temperatura Extrema no Mês (°C)', color='#cf4646', fontsize=11, fontweight='bold')

linha_max = ax2.plot(indices, df_mensal[col_max], color='#d9534f', linewidth=2.5, 
                     marker='o', markersize=6, label='Maior Temp. Máxima (°C)')

# NOVO: Linha de tendência/média da temperatura máxima histórica
linha_temp_hist = ax2.plot(indices, df_mensal['Temp_Max_Historica'], color='#f0ad4e', linewidth=1.8, 
                             linestyle=':', marker='^', label='Média Histórica Máxima (°C)')

linha_min = ax2.plot(indices, df_mensal[col_min], color='#337ab7', linewidth=2.5, 
                     marker='o', markersize=6, label='Menor Temp. Mínima (°C)')

ax2.tick_params(axis='y', labelcolor='#cf4646')
ax2.set_ylim(df_mensal[col_min].min() - 3, max(df_mensal[col_max].max(), df_mensal['Temp_Max_Historica'].max()) * 1.35)

# 7. Formatação do Eixo X
plt.xticks(indices, df_mensal['Mes_Ano_Texto'], fontweight='bold')

# 8. Legenda Única Atualizada
elementos_graficos = [barras_chuva] + linha_chuva_hist + linha_max + linha_temp_hist + linha_min
labels = [e.get_label() for e in elementos_graficos]
ax1.legend(elementos_graficos, labels, loc='upper right', frameon=True, facecolor='white', edgecolor='#ccc', shadow=True, fontsize=9)

# 9. Título e Créditos
plt.title('Resumo Climático Mensal (2026) vs. Normal Climatológica (1991-2020)\nAnálise de Anomalias em Caxias do Sul (RS)', fontsize=14, fontweight='bold', pad=20)

texto_fonte = 'Fonte: Dados 2026 da Estação Automática de Criúva (B817) | Média Histórica da Estação Convencional do Aeroporto (83942) - INMET'
fig.text(0.1, 0.02, texto_fonte, fontsize=8, style='italic', color='#555')
fig.text(0.9, 0.02, 'Autor: Gabriel Siqueira dos Santos', fontsize=10, fontweight='bold', color='#333', ha='right')

plt.tight_layout()
plt.subplots_adjust(bottom=0.15) 

# Salvar 
plt.savefig('grafico_clima.png', dpi=300)


# 10. Exibir o gráfico
plt.show()



### FIM DO SCRIPT