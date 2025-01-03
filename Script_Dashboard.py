import pandas as pd
import requests
import streamlit as st

# Configurar título do aplicativo
st.title("Dashboard de SKUs Não Vendidos por Vendedor")

# Função para carregar o arquivo do Google Drive
def carregar_google_drive(link_drive):
    try:
        st.info("Carregando arquivo do Google Drive...")
        response = requests.get(link_drive)
        response.raise_for_status()  # Verificar erros na requisição

        with open("arquivo_temp_google.xlsx", "wb") as f:
            f.write(response.content)

        return pd.read_excel("arquivo_temp_google.xlsx")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo do Google Drive: {e}")
        return None

# Função para carregar o arquivo do GitHub
def carregar_github(link_github):
    try:
        st.info("Carregando arquivo do GitHub...")
        response = requests.get(link_github)
        response.raise_for_status()  # Verificar erros na requisição

        return pd.read_excel(response.content)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo do GitHub: {e}")
        return None

# Função para carregar arquivo via upload manual
def carregar_upload_manual():
    uploaded_file = st.file_uploader(r"c:\Users\lucca.peixoto\Downloads\Qlik Sense - DB ROTAS POR SKULL - 2 de janeiro de 2025.xlsx", type=["xlsx"])
    if uploaded_file:
        try:
            return pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao processar o arquivo enviado: {e}")
    return None

# Seleção de método de carregamento
st.sidebar.title("Método de Carregamento de Dados")
metodo = st.sidebar.radio("Escolha como carregar o arquivo:", ["Google Drive", "GitHub", "Upload Manual"])

# Carregar a base de dados com base no método selecionado
base_skull = None

if metodo == "Google Drive":
    # Link de exemplo (substitua pelo seu link de download direto do Google Drive)
    link_drive = "https://docs.google.com/spreadsheets/d/1f6MLnCLyJ85v3_2mqnOsAm7GU-Naqijw/edit?usp=drive_link&ouid=118021272873758968461&rtpof=true&sd=true"
    base_skull = carregar_google_drive(link_drive)

elif metodo == "GitHub":
    # Link de exemplo (substitua pelo seu link raw do GitHub)
    link_github = "https://raw.githubusercontent.com/carnaubarosario/Dashboard-SKU/830cef041b5894e2b0ec90d32b30f19826aa702c/Qlik%20Sense%20-%20DB%20ROTAS%20POR%20SKULL%20-%202%20de%20janeiro%20de%202025.xlsx"
    base_skull = carregar_github(link_github)

elif metodo == "Upload Manual":
    base_skull = carregar_upload_manual()

# Verificar se a base foi carregada
if base_skull is None:
    st.warning("Nenhum arquivo foi carregado. Por favor, carregue um arquivo válido.")
    st.stop()

# **Tratamento de dados**

# Substituir valores "PT7L" para "PT - 7L" e ajustar "CX"
base_skull["PRODUTO"] = base_skull["PRODUTO"].replace("PT7L", "PT - 7L")
base_skull["PRODUTO"] = base_skull["PRODUTO"].str.replace(r"^CX", "CX - ", regex=True)

# Filtrar por ano e mês
base_skull = base_skull[(base_skull["ANO"] == 2024) & (base_skull["MÊS"].str.lower() == "dez")]

# Lista de vendedores filtrados
vendedores_filtrados = [
    "ADRIANO MENDONCA DE MEDEIROS", "CICERO PETRONILO", "DEIVISON RODRIGUES", "EDVAN GUILHERME",
    "EUCILANIO SANTOS", "ITALO ANGELO", "JEAN FABIO", "JOSE CARLOS", "JOSE FERNANDO", "JOSE UILSON",
    "JOSE WILLIAMS", "JULIO CESAR", "MARTA VIEIRA", "MICHEL JOSÉ", "MOISES FERREIRA BARROS",
    "NATAN FIRMINO", "WELLINGTON SILVA"
]
base_skull = base_skull[base_skull["FUNCIONÁRIO"].isin(vendedores_filtrados)]

# Identificar SKUs únicos
todos_skus = set(base_skull["PRODUTO"].unique())

# Agrupar por vendedor e listar SKUs vendidos
vendedores_skus = base_skull.groupby("FUNCIONÁRIO")["PRODUTO"].apply(set)

# Resumo por vendedor
resumo_vendedores = []

for vendedor, skus_vendidos in vendedores_skus.items():
    skus_nao_vendidos = todos_skus - skus_vendidos

    # Mesclar CATEGORIA e PRODUTO
    skus_nao_vendidos_completa = base_skull[base_skull["PRODUTO"].isin(skus_nao_vendidos)][["CATEGORIA", "PRODUTO"]]
    skus_nao_vendidos_lista = skus_nao_vendidos_completa.drop_duplicates().sort_values(by=["CATEGORIA", "PRODUTO"])

    resumo_vendedores.append({
        "FUNCIONÁRIO": vendedor,
        "SKUs Não Vendidos (Quantidade)": len(skus_nao_vendidos),
        "SKUs Não Vendidos (Lista)": skus_nao_vendidos_lista
    })

# Converter resumo para DataFrame
resumo_vendedores_df = pd.DataFrame(resumo_vendedores)

# Ordenar
resumo_vendedores_df = resumo_vendedores_df.sort_values(by="SKUs Não Vendidos (Quantidade)", ascending=False)

# **Exibição no Streamlit**
st.subheader("Resumo de SKUs Não Vendidos")
st.dataframe(resumo_vendedores_df[["FUNCIONÁRIO", "SKUs Não Vendidos (Quantidade)"]], use_container_width=True)

# Detalhes por vendedor
st.subheader("Detalhes por Vendedor")
vendedor_selecionado = st.selectbox("Selecione um Vendedor:", resumo_vendedores_df["FUNCIONÁRIO"])

if vendedor_selecionado:
    vendedor_info = resumo_vendedores_df[resumo_vendedores_df["FUNCIONÁRIO"] == vendedor_selecionado]
    st.write(f"**Quantidade de SKUs Não Vendidos:** {vendedor_info['SKUs Não Vendidos (Quantidade)'].values[0]}")

    # Mostrar lista como tabela
    st.write("**Lista de SKUs Não Vendidos:**")
    st.table(vendedor_info["SKUs Não Vendidos (Lista)"].values[0])
