# Licenças de terceiros

O código e a documentação próprios deste repositório usam Apache 2.0. As dependências
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

<a href="https://openweathermap.org/"><img src="../assets/openweather/openweather-logo.png" alt="OpenWeather" width="180"></a>

**Weather data provided by [OpenWeather](https://openweathermap.org/).**
As colunas de temperatura, umidade e precipitação foram agregadas a partir
de dados obtidos pelo plano estudantil OpenWeather.

O dataset analítico é distribuído como base derivada sob
[ODbL 1.0](../LICENSE-DATA), com o [aviso de atribuição](../data/NOTICE).
O [guia OpenWeather](https://openweathermap.org/guide) distingue a apresentação
de resultados da redistribuição de uma base que combina ou transforma dados
meteorológicos. A agregação em intervalos não elimina a origem dos dados.

Ao redistribuir o CSV, mantenha a licença e os avisos e descreva alterações.
Bases derivadas utilizadas publicamente devem cumprir o compartilhamento
pela mesma licença e as obrigações de acesso da ODbL, inclusive disponibilizar
a base ou as alterações em formato legível por máquina conforme a seção 4.6.
A ODbL permite uso comercial e não comercial sob suas condições; não rege o
código utilizado para operar a base nem substitui direitos dos conteúdos
individuais ou de marcas.

O OpenWeather também indica [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
para mapas, APIs e outros produtos, conforme o material e os termos aplicáveis.
Isso não altera a licença Apache 2.0 do código próprio do FarmNote. As métricas
agregadas em `results/reference/` conservam [CC BY 4.0](../LICENSE-RESULTS)
quanto aos direitos disponíveis; a base de origem continua sob ODbL.

## Atribuição visível

Use a frase **Weather data provided by OpenWeather**, com link para
`https://openweathermap.org/` e o logo oficial. O crédito deve estar visível
na apresentação dos dados ou da funcionalidade derivada, não apenas em páginas
de termos, privacidade ou licenças. O README principal e os documentos dos
dados e resultados incluem esse crédito. Novos gráficos SHAP também o incluem.
Gráficos exportados anteriormente precisam receber a atribuição antes de serem
divulgados. O logo original e sua origem estão em
[assets/openweather/](../assets/openweather/).

Ao compartilhar resultados, inclua também a referência à base meteorológica
e à ODbL, conforme a seção 4.3 da licença. A licença de uma imagem ou de um texto
resultante não substitui essas obrigações nem relicencia a base original.

Referências: [FAQ de atribuição OpenWeather](https://openweathermap.org/faq),
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) e
[termos de venda](https://openweather.co.uk/api/files/file/OpenWeather_T%26C_of_sale.pdf).
