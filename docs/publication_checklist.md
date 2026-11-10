# Checklist de publicação

Verificações concluídas em 10 de novembro de 2026. Antes de publicar novas
alterações, repita as verificações relacionadas aos arquivos modificados.

## Licenças e dados

- [x] Código e documentação identificados como Apache 2.0, com `LICENSE` e `NOTICE`.
- [x] Dataset e métricas identificados com CC BY 4.0 para os direitos disponíveis sobre esses materiais.
- [ ] Confirmar com OpenWeather a licença e as condições de redistribuição das colunas meteorológicas obtidas pelo plano estudantil. Consulta enviada ao suporte; aguardando resposta. Ver [licenças de terceiros](third_party_licenses.md).
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

O consentimento sobre os dados da propriedade não substitui as condições
do provedor meteorológico. A confirmação dessas condições é a pendência
de licenciamento para a redistribuição do CSV sob CC BY 4.0.
