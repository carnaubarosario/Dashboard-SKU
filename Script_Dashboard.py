import pandas as pd
import streamlit as st

# Título do Dashboard
st.title("Dashboard de SKUs Não Vendidos por Vendedor")

# URL do arquivo Excel (substitua pela URL real do arquivo)
url_arquivo = "https://github.com/carnaubarosario/Dashboard-SKU/blob/67f484d6e8505a38492f7dc907d602e153bf4670/Qlik%20Sense%20-%20DB%20ROTAS%20POR%20SKULL%20-%202%20de%20janeiro%20de%202025.xlsx"  # Insira a URL do seu arquivo


# Verificar se o arquivo foi carregado
if url_arquivo is not None:
    # Carregar a base de dados a partir do arquivo enviado
    base_skull = pd.read_excel(url_arquivo)
    st.success("Base de dados carregada com sucesso!")
else:
    # Caminho para um arquivo padrão no ambiente local (caso exista)
    caminho_padrao = r"c:\Users\lucca.peixoto\Downloads\Qlik Sense - DB ROTAS POR SKULL - 2 de janeiro de 2025.xlsx"
    
    try:
        base_skull = pd.read_excel(caminho_padrao)
        st.info("Nenhum arquivo foi carregado. Usando a base de dados padrão.")
    except FileNotFoundError:
        st.error("Nenhum arquivo foi carregado e o arquivo padrão não foi encontrado. Por favor, faça o upload de um arquivo válido.")
        st.stop()

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

# Substituir "PT7L" por "PT - 7L" e "CX" por "CX - "
base_skull["PRODUTO"] = base_skull["PRODUTO"].replace({"PT7L": "PT - 7L"})
base_skull["PRODUTO"] = base_skull["PRODUTO"].apply(lambda x: x.replace("CX", "CX - ") if isinstance(x, str) and x.startswith("CX") else x)

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
        "SKUs Não Vendidos (Lista)": skus_nao_vendidos_lista
    })

# Converter o resumo para um DataFrame
resumo_vendedores_df = pd.DataFrame(resumo_vendedores)

# Ordenar por quantidade de SKUs não vendidos
resumo_vendedores_df = resumo_vendedores_df.sort_values(by="SKUs Não Vendidos (Quantidade)", ascending=False).reset_index(drop=True)

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
    
    # Exibir SKUs não vendidos de forma organizada em uma tabela
    st.subheader("SKUs Não Vendidos Detalhados")
    skus_nao_vendidos_df = pd.DataFrame(skus_nao_vendidos_lista_unica, columns=["SKU Não Vendido"])
    st.dataframe(skus_nao_vendidos_df, use_container_width=True)

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
