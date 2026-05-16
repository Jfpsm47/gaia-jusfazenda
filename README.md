# 🌍 Gaia Jusfazenda

O **Gaia Jusfazenda** é uma ferramenta automatizada de *Due Diligence* e conformidade socioambiental (Environmental Compliance) desenvolvida em Python. O sistema cruza os limites de propriedades rurais (polígonos do CAR) com bancos de dados espaciais oficiais brasileiros para identificar passivos ambientais e restrições territoriais.

## 🚀 Funcionalidades Principais

* **Validação de Sobreposição:** Cruzamento rápido do perímetro da fazenda com múltiplas bases de restrição (shapefiles).
* **Análise Temporal de Desmatamento:** Diferenciação inteligente entre áreas consolidadas (desmatamento histórico) e incremento anual recente, essencial para o marco temporal do Código Florestal de 2008.
* **Cálculo Automático de Área:** Conversão topológica para calcular a exata metragem afetada em hectares (ha), com tolerância configurável para pequenos erros de borda (< 0.05 ha).
* **Geração de Evidências Visuais:**
  * 🗺️ Criação automática de mapas em alta resolução (`.png`) com imagens de satélite reais de fundo (Esri World Imagery).
  * 📍 Exportação de polígonos de infração em formato `.kml` para visualização interativa no Google Earth.

## 🗂️ Bases de Dados Suportadas (Exemplos)

O motor é configurado por meio de um dicionário dinâmico, permitindo plugar facilmente bases como:
* **INPE (PRODES):** Desmatamento Amazônia, Cerrado e Pantanal (Contíguo e Acumulado).
* **FUNAI:** Terras Indígenas demarcadas ou em estudo.
* **INCRA:** Áreas e Comunidades Quilombolas.
* **ICMBio/MMA:** Unidades de Conservação (Federais e Estaduais).

## 🛠️ Tecnologias Utilizadas

O projeto é construído em cima de bibliotecas robustas de dados espaciais no ecossistema Python:
* `geopandas`: Motor principal de manipulação espacial e overlay de polígonos.
* `fiona`: Leitura de shapefiles e exportação de vetores (.kml).
* `matplotlib`: Renderização e plotagem das geometrias.
* `contextily`: Integração com basemaps de satélite via Web Mercator.

## ⚙️ Instalação e Configuração

1. Clone este repositório:
   ```bash
   git clone [https://github.com/Jfpsm47/gaia-jusfazenda.git](https://github.com/Jfpsm47/gaia-jusfazenda.git)

## 📂 Artefatos Gerados (Saídas)

Para cada análise com sobreposição confirmada (área > 0.05 ha), o sistema gera automaticamente na pasta `mapas_gerados/`:

1. **Mapas de Satélite (`satelite_<Nome_da_Analise>.png`)**:
   - Imagens em alta resolução (300 DPI) utilizando o basemap Esri World Imagery (EPSG:3857).
   - A fazenda é destacada com uma borda amarela vazada, e a área de infração/interseção em vermelho translúcido.

2. **Arquivos Google Earth (`vetor_<Nome_da_Analise>.kml`)**:
   - O polígono da área afetada convertido para WGS 84 (EPSG:4326), pronto para visualização tridimensional e interativa no Google Earth.

## 📝 Como Executar

1. Certifique-se de ter as dependências instaladas:
   ```bash
   pip install geopandas matplotlib contextily fiona
   ```

2. Execute o script principal. Ele processará todas as análises configuradas na ordem e salvará os mapas na pasta `mapas_gerados`:
   ```bash
   python environmental_compliance_analysis.py
   ```