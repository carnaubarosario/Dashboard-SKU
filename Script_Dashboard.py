import pandas as pd
import streamlit as st

# URL bruta do arquivo no GitHub
url_arquivo = 'https://raw.githubusercontent.com/carnaubarosario/Dashboard-SKU/830cef041b5894e2b0ec90d32b30f19826aa702c/Qlik%20Sense%20-%20DB%20ROTAS%20POR%20SKULL%20-%202%20de%20janeiro%20de%202025.xlsx'

# Carregar a base de dados do GitHub diretamente
@st.cache_data
def carregar_base_skull(url):
    base_skull = pd.read_excel(url, engine='openpyxl')
    return base_skull

# Carregar a base de dados
base_skull = carregar_base_skull(url_arquivo)

# Converter a coluna "MÊS" para letras minúsculas (evitar problemas de case)
base_skull["MÊS"] = base_skull["MÊS"].str.lower()

# Filtrar os dados para o ano de 2024
base_skull = base_skull[base_skull["ANO"] == 2024]

# Filtrar para o mês de dezembro
base_skull = base_skull[base_skull["MÊS"] == "dez"]

# Lista de vendedores a serem filtrados
vendedores_filtrados = [
    "ADRIANO MENDONCA DE MEDEIROS", "CICERO PETRONILO", "DEIVISON RODRIGUES", "EDVAN GUILHERME", 
    "EUCILANIO SANTOS", "ITALO ANGELO", "JEAN FABIO", "JOSE CARLOS", "JOSE FERNANDO", "JOSE UILSON", 
    "JOSE WILLIAMS", "JULIO CESAR", "MARTA VIEIRA", "MICHEL JOSÉ", "MOISES FERREIRA BARROS", 
    "NATAN FIRMINO", "WELLINGTON SILVA"
]

# Filtrar os dados para considerar apenas os vendedores da lista
base_skull = base_skull[base_skull["FUNCIONÁRIO"].isin(vendedores_filtrados)]

# Identificar todos os SKUs únicos disponíveis na base
todos_skus = set(base_skull["PRODUTO"].unique())

# Agrupar por vendedor e listar os SKUs vendidos por cada um
vendedores_skus = base_skull.groupby("FUNCIONÁRIO")["PRODUTO"].apply(set)

# Criar um DataFrame para armazenar os SKUs não vendidos por vendedor
resumo_vendedores = []

for vendedor, skus_vendidos in vendedores_skus.items():
    # SKUs que o vendedor deixou de vender
    skus_nao_vendidos = todos_skus - skus_vendidos
    
    # Mesclar "CATEGORIA" e "PRODUTO" para detalhar melhor e remover duplicatas
    skus_nao_vendidos_completa = base_skull[base_skull["PRODUTO"].isin(skus_nao_vendidos)][["CATEGORIA", "PRODUTO"]]
    
    # Remover duplicatas e criar lista única
    skus_nao_vendidos_lista = ", ".join(skus_nao_vendidos_completa.apply(lambda row: f"{row['CATEGORIA']} - {row['PRODUTO']}", axis=1).drop_duplicates())
    
    resumo_vendedores.append({
        "FUNCIONÁRIO": vendedor,
        "SKUs Não Vendidos (Quantidade)": len(skus_nao_vendidos),
        "SKUs Não Vendidos (Lista)": skus_nao_vendidos_lista,
        "SKUs Não Vendidos (Tabela)": skus_nao_vendidos_completa
    })

# Converter o resumo para um DataFrame
resumo_vendedores_df = pd.DataFrame(resumo_vendedores)

# Ordenar por quantidade de SKUs não vendidos
resumo_vendedores_df = resumo_vendedores_df.sort_values(by="SKUs Não Vendidos (Quantidade)", ascending=False).reset_index(drop=True)

# Streamlit Dashboard
st.title("Dashboard de SKUs Não Vendidos por Vendedor")

# Mostrar o DataFrame de resumo com rolagem
st.subheader("Resumo de SKUs Não Vendidos")
st.dataframe(resumo_vendedores_df, use_container_width=True)

# Seleção interativa por vendedor
st.subheader("Detalhes por Vendedor")
vendedor_selecionado = st.selectbox("Selecione um Vendedor:", resumo_vendedores_df["FUNCIONÁRIO"])

# Mostrar detalhes do vendedor selecionado
if vendedor_selecionado:
    vendedor_info = resumo_vendedores_df[resumo_vendedores_df["FUNCIONÁRIO"] == vendedor_selecionado]
    
    # Garantir que não haja duplicatas nos SKUs não vendidos ao exibir detalhes
    skus_nao_vendidos_lista_unica = vendedor_info['SKUs Não Vendidos (Lista)'].values[0].split(", ")
    skus_nao_vendidos_lista_unica = sorted(list(set(skus_nao_vendidos_lista_unica)))  # Remover duplicatas e ordenar
    
    st.write(f"**SKUs Não Vendidos (Quantidade):** {vendedor_info['SKUs Não Vendidos (Quantidade)'].values[0]}")
    
    # Exibir a tabela com SKUs não vendidos
    st.write("**SKUs Não Vendidos (Tabela):**")
    st.dataframe(vendedor_info['SKUs Não Vendidos (Tabela)'].values[0], use_container_width=True)

# Filtros adicionais para explorar os dados
st.sidebar.title("Filtros")
filtro_quantidade = st.sidebar.slider("Filtrar por Quantidade de SKUs Não Vendidos", 
                                       0, 
                                       resumo_vendedores_df["SKUs Não Vendidos (Quantidade)"].max(), 
                                       (0, resumo_vendedores_df["SKUs Não Vendidos (Quantidade)"].max()))

# Aplicar filtro
filtro_resumo = resumo_vendedores_df[(
    resumo_vendedores_df["SKUs Não Vendidos (Quantidade)"] >= filtro_quantidade[0]) & 
    (resumo_vendedores_df["SKUs Não Vendidos (Quantidade)"] <= filtro_quantidade[1])
]

st.sidebar.subheader("Tabela Filtrada")
st.sidebar.dataframe(filtro_resumo, use_container_width=True)
