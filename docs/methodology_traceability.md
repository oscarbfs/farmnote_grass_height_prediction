# Mapa da implementação

| Etapa | Implementação |
|---|---|
| Schema e tipos | [`data/schema.py`](../src/farmnote_grass_height/data/schema.py) |
| Leitura e validação | [`data/loader.py`](../src/farmnote_grass_height/data/loader.py) |
| Seleção de variáveis e ablação | [`data/features.py`](../src/farmnote_grass_height/data/features.py) |
| Imputação, datas, escala e encoding | [`preprocessing/`](../src/farmnote_grass_height/preprocessing/) |
| Estimadores e grids | [`models/`](../src/farmnote_grass_height/models/) |
| Split e treinamento | [`training/`](../src/farmnote_grass_height/training/) |
| Métricas e ranking | [`evaluation/`](../src/farmnote_grass_height/evaluation/) |
| Importâncias SHAP | [`interpretation/`](../src/farmnote_grass_height/interpretation/) |

O treinamento divide as 67 linhas em 54 para treino e 13 para holdout,
com embaralhamento por `random.Random(42)`. Cada família usa busca em grade
com cinco dobras no treino. A ablação mantém o pipeline e remove as variáveis
de movimentação/ocupação, deixando 16 entradas em vez de 60.

Os comandos estão no [README](../README.md#executar).
O `manifest.json` registra as variáveis, partições, parâmetros, versões e hash
do CSV usado. A avaliação e o SHAP recusam um arquivo com hash diferente.
Consulte as [notas de execução](divergences.md) antes de interpretar resultados.
