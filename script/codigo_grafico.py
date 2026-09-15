
### Projeto para visualização em gráfico do acumulado de chuvas X temperaturas de Caxias do Sul
# Dados públicos retirados do site do INMET: https://portal.inmet.gov.br/servicos/bdmep-dados-históricos
# Desenvolvido por Grabriel Siqueira dos Santos

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

# 3. Extraçao dos dados
col_data = [c for c in df.columns if 'Data' in c][0]
col_max = [c for c in df.columns if 'Temp. Max.' in c or 'Temp. Máx.' in c or 'Max' in c][0]
col_min = [c for c in df.columns if 'Temp. Min.' in c or 'Mín' in c or 'Min' in c][0]
col_chuva = [c for c in df.columns if 'Chuva' in c][0]

# 4. Tratar datas e forçar conversão numérica usando as chaves de string puras
df[col_data] = pd.to_datetime(df[col_data], errors='coerce', dayfirst=True)

for col in [col_max, col_min, col_chuva]:
    df[col] = df[col].astype(str).str.replace(',', '.')
    df[col] = df[col].replace(['-9999', '-9999.0', 'nan', 'NaN', 'None'], np.nan)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Remover linhas inválidas e filtrar até a data atual
df = df.dropna(subset=[col_data])
data_hoje = pd.to_datetime('today')
df = df[df[col_data] <= data_hoje]

# 5. Agrupamento Mensal
df['Ano_Mes'] = df[col_data].dt.to_period('M')

df_mensal = df.groupby('Ano_Mes').agg({
    col_max: 'max',     
    col_min: 'min',     
    col_chuva: 'sum'    
}).reset_index()

df_mensal = df_mensal.sort_values('Ano_Mes')
df_mensal['Mes_Ano_Texto'] = df_mensal['Ano_Mes'].dt.strftime('%b/%y')

# 6. Configurar as posições no eixo X
indices = np.arange(len(df_mensal))  
largura_barra_chuva = 0.4  # Barra centralizada e mais encorpada ao fundo

# Criar a estrutura do gráfico com eixo duplo
fig, ax1 = plt.subplots(figsize=(12, 6.5)) 

# --- EIXO Y 1: Chuva (Barras Azuis Claras ao Fundo) ---
color_chuva = '#bce2e6'  # Azul suave para o fundo
ax1.set_xlabel('Período (Mensal)', fontsize=12, fontweight='bold', labelpad=10)
ax1.set_ylabel('Chuva Acumulada no Mês (mm)', color='#4682B4', fontsize=11, fontweight='bold')

# Barra centralizada no mês para servir de plano de fundo
barras_chuva = ax1.bar(indices, df_mensal[col_chuva], 
                       width=largura_barra_chuva, color=color_chuva, alpha=0.7, label='Chuva Acumulada (mm)')
ax1.tick_params(axis='y', labelcolor='#4682B4')
ax1.grid(True, axis='y', linestyle='--', alpha=0.3)


ax1.set_ylim(0, df_mensal[col_chuva].max() * 1.30)

# --- EIXO Y 2: Temperaturas Máxima e Mínima em LINHAS DESTACADAS ---
ax2 = ax1.twinx()  
ax2.set_ylabel('Temperatura Extrema no Mês (°C)', color='#cf4646', fontsize=11, fontweight='bold')

# Linha da Temperatura Máxima (Vermelha)
linha_max = ax2.plot(indices, df_mensal[col_max], color='#d9534f', linewidth=2.5, 
                     marker='o', markersize=6, label='Maior Temp. Máxima (°C)')

# Linha da Temperatura Mínima (Azul Escura)
linha_min = ax2.plot(indices, df_mensal[col_min], color='#337ab7', linewidth=2.5, 
                     marker='o', markersize=6, label='Menor Temp. Mínima (°C)')
ax2.tick_params(axis='y', labelcolor='#cf4646')

# Ajuste do limite para afastar a legenda das linhas
ax2.set_ylim(df_mensal[col_min].min() - 3, df_mensal[col_max].max() * 1.30)

# 7. Formatação do Eixo X
plt.xticks(indices, df_mensal['Mes_Ano_Texto'], fontweight='bold')

# 8. Legenda Única Combinada (Lado superior direito no espaço livre)
elementos_graficos = [barras_chuva] + linha_max + linha_min
labels = [e.get_label() for e in elementos_graficos]
ax1.legend(elementos_graficos, labels, loc='upper right', frameon=True, facecolor='white', edgecolor='#ccc', shadow=True)

# 9. Título e Créditos
plt.title('Resumo Climático Mensal - Caxias do Sul (RS)\nAnálise de Tendências de Chuva e Temperatura', fontsize=14, fontweight='bold', pad=20)

fig.text(0.1, 0.02, 'Fonte dos dados: INMET (Instituto Nacional de Meteorologia)', fontsize=9, style='italic', color='#555')
fig.text(0.9, 0.02, 'Autor: Gabriel Siqueira dos Santos', fontsize=10, fontweight='bold', color='#333', ha='right')

plt.tight_layout()
plt.subplots_adjust(bottom=0.15) 

plt.savefig('grafico_clima.png', dpi=300)

# 10. Exibir o gráfico
plt.show()

###FIM DO SCRIPT