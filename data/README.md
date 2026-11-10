# Dados

O pipeline usa `data/pasturages_anonymized.csv`, com 67 linhas e 77 colunas.
Cada linha representa o intervalo entre duas medições de altura no mesmo
piquete. O alvo é `end_grass_height_avg_cm`, em centímetros.
O [dicionário](data_dictionary.md) descreve tipos, unidades e uso das colunas.

## Formato

- UTF-8, separador `;` e vírgula decimal;
- cabeçalho na ordem definida em [`data/schema.py`](../src/farmnote_grass_height/data/schema.py);
- timestamps ISO 8601;
- booleanos `true`/`false` ou `1`/`0`, sem distinção de maiúsculas;
- ausentes como campos vazios.

O carregador valida cabeçalho, tipos, identificadores, unicidade dos eventos e
presença do alvo. As linhas são ordenadas por término, início e ID do evento.

## Pseudônimos e consentimento

| Coluna | Padrão |
|---|---|
| `id` | `row_NN` |
| `user_id` | `source_NN` |
| `paddock_id` | `paddock_NN` |
| `pasturage_event_id` | `event_NN` |

Os identificadores preservam as relações entre linhas sem distribuir a
correspondência com os registros operacionais. Datas, áreas e demais valores
analíticos são preservados. A publicação dos dados da propriedade é consentida
pelo proprietário, inclusive quando a origem puder ser reconhecida.
Pseudonimização não significa anonimato irreversível.

## Preparar outra versão

Use somente um dataset analítico cuja utilização esteja autorizada. Mantenha
a origem privada fora deste repositório:

```bash
python scripts/anonymize_dataset.py /caminho/privado/training_dataset.csv --output /caminho/publico/dataset.csv
```

O script substitui os quatro identificadores, preserva os demais valores e não
salva o mapa de correspondência. Para substituir um destino existente, informe
`--force`. Ele informa hashes da origem e do resultado; não publique o hash da
origem privada sem necessidade.

Uma nova versão pode ser usada com `--dataset`. Treino, avaliação e SHAP devem
receber o mesmo CSV. Alterações em datas ou valores mudam os dados de entrada
e podem alterar os resultados.

## Licença

[CC BY 4.0](../LICENSE-DATA), quanto aos direitos disponíveis sobre o dataset.
Crédito: Oscar Borges Faleta Santana, FarmNote, lote `2026-06-01_20-44`.
Weather data provided by [OpenWeather](https://openweathermap.org/).

**A compatibilidade da redistribuição das colunas meteorológicas com CC BY 4.0
permanece em confirmação.** Consulte [licenças de terceiros](../docs/third_party_licenses.md).
O consentimento do proprietário não substitui os direitos do provedor.
