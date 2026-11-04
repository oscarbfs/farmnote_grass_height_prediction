# Dados

## O que este repositório espera

O pipeline público parte do **dataset analítico**, e não dos registros operacionais brutos. O arquivo esperado é:

```text
data/pasturages_anonymized.csv
```

Ele deve conter uma linha por evento de pastejo — o intervalo entre duas medições consecutivas de altura no mesmo piquete — e as 77 colunas, na ordem registrada em [`data_dictionary.md`](data_dictionary.md). Na execução descrita no manuscrito e nos artefatos privados auditados, o conjunto tinha 67 linhas.

O CSV usa:

- codificação UTF-8;
- `;` como separador;
- `,` como separador decimal;
- cabeçalho completo, com as 77 colunas;
- timestamps em formato ISO 8601;
- booleanos `true`/`false` ou `1`/`0`;
- valores ausentes como campos vazios.

## Por que os dados brutos não estão aqui

Os dados brutos foram coletados pelo aplicativo FarmNote e processados pela API operacional. Eles incluem estruturas e identificadores internos, registros de propriedades, bovinos, movimentações, pesagens, medições, geometria/localização e metadados que não são necessários para executar o experimento público. A aplicação Flutter, a API completa, o banco MongoDB, as configurações do serviço meteorológico e os arquivos de exportação originais não integram esta distribuição.

O construtor original também é fortemente acoplado às entidades e aos repositórios privados. A decisão de publicação, portanto, é disponibilizar diretamente o dataset analítico revisado e pseudonimizado. A lógica de construção identificada no código está documentada em [`../docs/dataset_construction.md`](../docs/dataset_construction.md).

## Estado de disponibilidade

A árvore de trabalho contém um **candidato** a dataset público em `pasturages_anonymized.csv`, obtido do dataset analítico — não dos dados brutos — pelo procedimento abaixo. Em 10 de agosto de 2026, verificações locais confirmaram 67 linhas, 77 colunas na ordem esperada, 67 pseudônimos de linha/evento únicos, uma origem pseudonimizada, cinco piquetes pseudonimizados e ausência de UUIDs remanescentes. O SHA-256 do candidato é `c68e057437c380e8f6ef29e053d33f139f8f95df4448c6563b3d9c89130cfeed`.

Essas verificações técnicas **não constituem autorização de publicação**. A pessoa responsável pelos dados ainda deve aprovar o risco de reidentificação descrito em [`../docs/publication_checklist.md`](../docs/publication_checklist.md). Se a aprovação não for concedida, remova o CSV da versão pública e mantenha somente a estrutura/documentação. O repositório não cria dados sintéticos como substituto.

## Pseudonimização prevista

O script `scripts/anonymize_dataset.py` substitui somente os quatro identificadores operacionais:

| Coluna | Forma pública | Relação preservada |
|---|---|---|
| `id` | `row_01`, `row_02`, … | unicidade da linha |
| `user_id` | `source_01`, `source_02`, … | mesma origem entre eventos |
| `paddock_id` | `paddock_01`, `paddock_02`, … | mesmo piquete entre eventos |
| `pasturage_event_id` | `event_01`, `event_02`, … | unicidade do evento |

Os pseudônimos são atribuídos de forma determinística a partir da ordenação dos valores existentes no arquivo de entrada. A tabela reversível não é gravada. Todos os demais valores, a ordem das linhas, os ausentes e a ordem das colunas são preservados textualmente.

Essa medida não garante anonimato por si só. Datas exatas, combinação de áreas, contagens, pesos e a descrição da área de estudo podem permitir reidentificação por quem já conhece a operação. A publicação depende de revisão humana desse risco.

## Preparação controlada do arquivo público

Execute o comando somente sobre uma cópia privada do dataset analítico já conferido. Nunca coloque a origem dentro deste repositório.

```bash
python scripts/anonymize_dataset.py /caminho/privado/training_dataset.csv
```

O destino padrão é `data/pasturages_anonymized.csv`. Para substituir um arquivo público previamente aprovado, é necessário informar explicitamente `--force`.

O script:

1. exige correspondência exata com as 77 colunas;
2. recusa origem vazia;
3. recusa identificadores ausentes;
4. não permite usar o mesmo caminho como origem e destino;
5. não grava o mapeamento entre IDs privados e públicos;
6. valida os padrões dos quatro pseudônimos;
7. escreve por arquivo temporário e substituição atômica;
8. informa hashes SHA-256 da origem e do arquivo público para a cadeia de custódia local.

Não inclua o hash da origem privada em uma publicação sem avaliar se essa impressão digital deve permanecer restrita.

## Validação antes do treinamento

O carregador público recusa o arquivo quando:

- o conjunto ou a ordem das colunas diverge do esquema;
- há token booleano, número ou data inválido;
- algum dos quatro identificadores não segue o padrão público;
- `id` ou `pasturage_event_id` não é único;
- o alvo `end_grass_height_avg_cm` está ausente.

O carregador ordena as linhas por `finished_at`, `started_at` e `pasturage_event_id`, reproduzindo a ordenação realizada antes do split histórico.

## O que não deve ser adicionado

Não publique neste diretório:

- planilhas XLSX exportadas pelo aplicativo;
- CSVs privados ou versões anteriores com UUIDs;
- dumps de banco, JSONs de modelos ou metadados com IDs internos;
- nomes de pessoas, propriedades ou animais;
- coordenadas, endereços ou geometrias;
- mapas de pseudonimização;
- credenciais, URLs privadas, tokens ou arquivos `.env`;
- dados brutos de clima, pesagem, movimentação ou altura.

Se a autorização para disponibilizar o dataset analítico não for concedida, mantenha apenas esta estrutura e registre a indisponibilidade como limitação de reprodutibilidade.
