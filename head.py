import geopandas as gpd

# Especifique o caminho do seu arquivo .shp
caminho_arquivo = "caminho/para/seu_arquivo.shp"

# Leia o arquivo
gdf = gpd.read_file(caminho_arquivo)

# Imprima todas as colunas disponíveis
print("Colunas do shapefile:")
print(gdf.columns.tolist())

# Veja as primeiras 5 linhas para entender o formato dos dados
print("\nPrimeiras linhas:")
print(gdf.head())