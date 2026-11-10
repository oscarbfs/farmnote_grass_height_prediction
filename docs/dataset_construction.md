# Entrada e preparação do dataset

A entrada do pipeline é o CSV analítico descrito em [data/README.md](../data/README.md).
A coleta e a construção científica do conjunto são apresentadas no artigo.

Cada linha agrega o intervalo entre duas medições consecutivas de altura no
mesmo piquete: altura inicial e final, área, clima e movimentação/ocupação.
O conjunto distribuído possui 67 eventos de cinco piquetes e 77 colunas.

O código público começa nesse CSV. Não reconstrói eventos a partir do banco
operacional, de planilhas brutas ou de uma API externa. Para preparar outro
arquivo analítico, use `scripts/anonymize_dataset.py` conforme as instruções
dos dados e preserve as unidades do [dicionário](../data/data_dictionary.md).

O carregador em [`loader.py`](../src/farmnote_grass_height/data/loader.py)
converte números e booleanos, valida timestamps, recusa identificadores fora
dos padrões públicos e exige um alvo preenchido. A seleção de variáveis em
[`features.py`](../src/farmnote_grass_height/data/features.py) remove o alvo,
os identificadores de linha, origem e evento e os proxies finais antes do
pré-processamento. `paddock_id` permanece como variável categórica.

As colunas meteorológicas e de movimentação representam observações do
intervalo completo. Para uso prospectivo, forneça informações disponíveis no
instante da previsão e avalie esse novo protocolo separadamente.
