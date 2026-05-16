import geopandas as gpd
import warnings
from datetime import datetime
import matplotlib.pyplot as plt
import os
import contextily as ctx
import fiona

warnings.filterwarnings("ignore")
fiona.drvsupport.supported_drivers['KML'] = 'rw'
ano_atual = datetime.now().year

# 1. Carregar a fazenda (Fazemos isso UMA ÚNICA VEZ)
caminho_json_fazenda = 'fazenda.json'
fazenda_gdf = gpd.read_file(caminho_json_fazenda)
fazenda_gdf.set_crs(epsg=4674, inplace=True, allow_override=True)

# 2. Dicionário Mestre de Configuração Atualizado
analises_para_fazer = {
    "Desmatamento Prodes Amazônia Legal": {
        "caminho": "geoData/amazonia/accumulated_deforestation_2007_amazonia_legal_v20260330.shp",
        "coluna_ano": "year"
    },
    "Desmatamento Contíguo Prodes Amazônia Legal": {
        "caminho": "geoData/amazonia contiguo/yearly_deforestation_amazonia_legal_v20260330.shp",
        "coluna_ano": "year"
    },
    "Desmatamento Prodes Cerrado": {
        "caminho": "geoData/cerrado/accumulated_deforestation_2000_biome_cerrado_v20260330.shp",
        "coluna_ano": "year"
    },
    "Desmatamento Prodes Pantanal": {
        "caminho": "geoData/pantanal/accumulated_deforestation_2000_biome_pantanal_v20260330.shp",
        "coluna_ano": "year"
    },
    "Sobreposição com Terras Indígenas": {
        "caminho": "geoData/terras indigenas/tis_poligonais.shp",
        "coluna_ano": None
    },
    "Sobreposição com Áreas de Quilombolas": {
        "caminho": "geoData/areas de quilombolas/Áreas de Quilombolas_MT.shp",
        "coluna_ano": None
    },
    "Sobreposição com Unidades de Conservação": {
        "caminho": "geoData/unidades de conservacao/limite_ucs_federais_032026_a2.shp",
        "coluna_ano": None 
    }
}
# 3. A Função Mágica (Agora com cálculo de Hectares)
def analisar_criterio(nome, config, fazenda):
    print(f"\nAnalisando: {nome}...")
    try:
        # Pega a "caixa delimitadora" da fazenda no formato de tupla
        limites_fazenda = tuple(fazenda.total_bounds)
        
        # Lê o shapefile usando a tupla como bbox (evita conflitos complexos de CRS no read_file)
        base_gdf = gpd.read_file(config["caminho"], bbox=limites_fazenda)
        
        if base_gdf.empty:
            return "CONFORME - Sem sobreposição (ou fora da caixa delimitadora)."
            
        # Agora sim, garante que ambos estão no mesmo sistema geodésico (SIRGAS 2000)
        base_gdf = base_gdf.to_crs(epsg=4674)
        fazenda = fazenda.to_crs(epsg=4674) # Garantia extra
        
        # Faz a interseção real
        intersecao = gpd.overlay(fazenda, base_gdf, how='intersection')
        
        if intersecao.empty:
            return "CONFORME - Sem sobreposição."
            
# --- CÁLCULO DE ÁREA EM HECTARES ---
        intersecao_metrica = intersecao.to_crs(epsg=5880)
        area_hectares = round(intersecao_metrica.area.sum() / 10000, 2)
        
        # Pequenos resquícios de borda
        if area_hectares < 0.05: 
             return "CONFORME - Interseção insignificante (possível erro de borda)."

        # Cria uma pasta "mapas_gerados" se não existir
        os.makedirs("mapas_gerados", exist_ok=True)

        # ==========================================
        # --- NOVO: GERAÇÃO DA IMAGEM DO MAPA ---
        # ==========================================
        # Cria uma "tela" em branco com tamanho 10x8 polegadas
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Reprojeta para Web Mercator (EPSG:3857) para o basemap de satélite
        fazenda_web = fazenda.to_crs(epsg=3857)
        intersecao_web = intersecao.to_crs(epsg=3857)
        
        # 1. Desenha a fazenda vazada com borda amarela para destacar no satélite
        fazenda_web.plot(ax=ax, facecolor='none', edgecolor='#ffeb3b', linewidth=2.5)
        
        # 2. Desenha a interseção em vermelho translúcido
        intersecao_web.plot(ax=ax, facecolor='#f44336', alpha=0.5)
        
        # Adiciona o basemap da Esri
        ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, attribution="")
        
        # 3. Adiciona um título com o nome da análise
        plt.title(f"Análise: {nome} | Área Afetada: {area_hectares} ha", fontsize=14)
        
        # Remove os eixos (coordenadas nas bordas) para ficar mais limpo
        ax.axis('off')
        
        # Salva a imagem em alta resolução (300 dpi) na pasta mapas_gerados
        nome_arquivo = f"mapas_gerados/satelite_{nome.replace(' ', '_')}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        
        # Fecha a figura para liberar a memória do computador
        plt.close()
        # ==========================================
        
        # ==========================================
        # --- EXPORTAÇÃO PARA GOOGLE EARTH (KML) ---
        # ==========================================
        # Reprojeta a interseção para WGS 84 (EPSG:4326) exigido pelo Google Earth
        intersecao_kml = intersecao.to_crs(epsg=4326)
        
        # Exporte utilizando o driver KML
        nome_kml = f"mapas_gerados/vetor_{nome.replace(' ', '_')}.kml"
        intersecao_kml.to_file(nome_kml, driver='KML')
        # ==========================================

        col_ano = config.get("coluna_ano")
        
        if col_ano and col_ano in intersecao.columns:
            anos = intersecao[col_ano].dropna().astype(int).unique().tolist()
            anos.sort()
            if ano_atual in anos:
                outros_anos = [a for a in anos if a != ano_atual]
                msg = f"NÃO CONFORME - ALERTA: Desmatamento de {area_hectares} ha no ANO ATUAL ({ano_atual})!"
                if outros_anos:
                    msg += f" Histórico anterior: {outros_anos}."
                return msg
            else:
                return f"NÃO CONFORME - Desmatamento de {area_hectares} ha. Histórico nos anos: {anos}."
        else:
            return f"NÃO CONFORME - Sobreposição de {area_hectares} ha detectada (S/ dado de ano)."

    except FileNotFoundError:
        return "ERRO - Arquivo de mapa não encontrado no caminho."
    except Exception as e:
        return f"ERRO - {e}"

# 4. Rodando o Motor para todos os critérios
print("=" * 60)
print("RELATÓRIO DE CONFORMIDADE AMBIENTAL")
print("=" * 60)

for nome_criterio, configuracao in analises_para_fazer.items():
    resultado = analisar_criterio(nome_criterio, configuracao, fazenda_gdf)
    print(f"-> {nome_criterio}: {resultado}")