# Licenças de terceiros

O código e a documentação deste repositório usam Apache 2.0. As dependências
instaladas por `requirements.txt` mantêm suas próprias licenças; seus códigos
e binários não são incorporados à árvore Git do projeto.

## Software

| Dependência principal | Versão | Licença principal |
|---|---|---|
| scikit-learn | 1.7.2 | [BSD-3-Clause](https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.7.2/COPYING) |
| LightGBM | 4.6.0 | [MIT](https://github.com/lightgbm-org/LightGBM/blob/v4.6.0/LICENSE) |
| SHAP | 0.48.0 | [MIT](https://raw.githubusercontent.com/shap/shap/v0.48.0/LICENSE) |
| Joblib | 1.5.1 | BSD-3-Clause |
| NumPy | 2.3.1 | BSD-3-Clause e avisos dos componentes incluídos |
| pandas | 2.3.1 | BSD-3-Clause |
| SciPy | 1.16.0 | BSD-3-Clause e avisos dos componentes incluídos |
| matplotlib | 3.10.9 | Licença própria baseada na PSF e avisos históricos |

Ao redistribuir dependências, preserve seus textos de licença, copyrights e
demais avisos aplicáveis, inclusive os componentes incorporados aos wheels.
Uma distribuição futura em contêiner ou executável precisa incluir os avisos
dos componentes efetivamente empacotados.

## Dados meteorológicos

Weather data provided by [OpenWeather](https://openweathermap.org/).
As colunas de temperatura, umidade e precipitação foram agregadas a partir
de dados obtidos pelo plano estudantil OpenWeather.

As [condições da iniciativa estudantil](https://docs.openweather.co.uk/our-initiatives/student-initiative)
descrevem uso acadêmico e restrições de uso comercial. O
[guia de licenciamento](https://openweathermap.org/guide) apresenta condições
para dados e bancos derivados. Esses termos não devem ser substituídos pela
licença escolhida para o restante do dataset.

**A compatibilidade da redistribuição das colunas meteorológicas com CC BY 4.0
aguarda resposta do OpenWeather à consulta enviada ao suporte.**
`LICENSE-DATA` não concede direitos que pertençam ao OpenWeather.
Antes de redistribuir o CSV sob essa licença,
confirme os termos aplicáveis à coleta e as obrigações de atribuição e
compartilhamento de dados derivados.
