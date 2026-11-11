# Checklist de publicação

Licenças e atribuição atualizadas em 11 de novembro de 2026. A validação integral
dos experimentos foi concluída em 10 de novembro de 2026. Antes de publicar
novas alterações, repita as verificações relacionadas aos arquivos modificados.

## Licenças e dados

- [x] Código e documentação identificados como Apache 2.0, com `LICENSE` e `NOTICE`.
- [x] Dataset identificado como base derivada sob ODbL 1.0 em `LICENSE-DATA` e `data/NOTICE`.
- [x] Métricas agregadas de referência mantidas sob CC BY 4.0 em `LICENSE-RESULTS`, com escopo separado do dataset.
- [x] Condições OpenWeather de atribuição e ODbL para dados e bases incorporadas à documentação; ver [licenças de terceiros](third_party_licenses.md).
- [x] Crédito OpenWeather, link e logo oficial visíveis no README principal e nos documentos de dados e resultados.
- [x] Script de geração de gráficos SHAP inclui crédito, link, logo e referência à ODbL nas novas imagens exportadas.
- [x] Avisos descrevem as agregações meteorológicas e orientam preservar atribuição, compartilhamento e acesso à base derivada.
- [x] Consentimento do proprietário para disponibilizar os dados da propriedade, inclusive quando a origem puder ser reconhecida.
- [x] Identificadores operacionais substituídos; mapa de correspondência e coordenadas não incluídos no CSV.
- [x] Formato, colunas, tipos, alvo e integridade do CSV conferidos.
- [x] Crédito, contato e citação disponíveis no README e em `CITATION.cff`.
- [x] Dependências identificadas como software de terceiros com licenças próprias.

## Funcionamento e segurança

- [x] Instalação em ambiente novo, fora do workspace da aplicação.
- [x] Dependências consistentes e oito testes aprovados.
- [x] Grids completos dos 15 modelos executados nos dois experimentos.
- [x] Modelos recarregados e métricas recalculadas pelo avaliador.
- [x] SHAP gerado para os cinco modelos selecionados de cada experimento.
- [x] Resultados de referência separados dos resultados de novas execuções.
- [x] Particularidades de métricas, split, disponibilidade temporal e seeds documentadas.
- [x] Verificador local de segurança sem achados; histórico Git alcançável também inspecionado.

Ao compartilhar o CSV, inclua `LICENSE-DATA`, `data/NOTICE` e os recursos de
atribuição OpenWeather. Na publicação de imagens, artigos ou outros produtos
externos, confira a presença da atribuição junto à apresentação dos dados e
resultados derivados. Saídas antigas precisam receber esses avisos antes da
divulgação; a atualização do repositório não modifica arquivos já exportados.
