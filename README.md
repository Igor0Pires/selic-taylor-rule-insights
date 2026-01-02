# Taylor Rule Analysis for Brazilian Economy

Análise e estimação da Regra de Taylor para a economia brasileira, utilizando dados de inflação esperada, taxa SELIC, hiato do produto e taxa de câmbio.

## Visão Geral

Este projeto implementa um pipeline completo para:
- Coleta e processamento de dados econômicos brasileiros
- Estimação dos parâmetros da Regra de Taylor em diferentes períodos
- Análise estatística dos resultados
- Visualização das séries temporais e estimativas

A Regra de Taylor é um modelo utilizado para entender como bancos centrais definem suas taxas de juros com base em desvios de inflação e hiato do produto.

## Estrutura do Projeto

```
taylor-project/
├── main.py                    # Ponto de entrada principal
├── config/
│   ├── config.yaml           # Configurações do pipeline
│   └── copom.yaml            # Configurações específicas do COPOM
├── data/
│   ├── raw/                  # Dados brutos
│   ├── processed/            # Dados processados
│   └── plots/                # Estilos de gráficos
├── src/
│   ├── pipeline.py           # Orquestração do pipeline
│   ├── ingestion.py          # Coleta de dados
│   ├── processing.py         # Processamento de dados
│   ├── estimation.py         # Estimação da Regra de Taylor
│   ├── analytics.py          # Análises estatísticas
│   ├── vizualization.py      # Geração de gráficos
│   └── utils.py              # Funções utilitárias
├── notebooks/
│   └── plots.ipynb           # Notebooks para exploração
└── logs/                      # Logs de execução
```

## Dados Utilizados

### Fontes de Dados

O projeto utiliza os seguintes conjuntos de dados:

1. **Expectativas de Inflação (Focus)**
   - Dados mensais de expectativas de inflação do mercado
   - Período: 2002-2025

2. **Inflação do BCB (Atas)**
   - Histórico de inflação esperada segundo o Banco Central
   - Período: 2002-2025

3. **Taxa SELIC**
   - Meta de taxa SELIC mensal
   - Período: 1999-2025

4. **Taxa de Câmbio**
   - Variação nominal da taxa de câmbio
   - Período: 1999-2025

5. **Meta de Inflação**
   - Meta de inflação definida pelo BCB
   - Período: 1999-2025

6. **IPCA 12 meses**
   - Inflação acumulada em 12 meses
   - Período: 1980-2025

7. **PIM-PF**
   - Proxy para gap de produto (Produção Industrial de Máquinas)
   - Período: 2002-2025

## Componentes Principais

### Pipeline
Orquestra todo o fluxo de dados:
- Ingestão de dados
- Processamento e limpeza
- Merge de bases diferentes
- Estimação de parâmetros
- Análises
- Visualizações

### Estimação da Regra de Taylor

A classe `TaylorRuleEstimator` implementa três modelos:

1. **Modelo I**: Apenas desvio de inflação
   ```
   selic_target ~ selic_target_lag + inflação_desvio
   ```

2. **Modelo II**: Inflação + Gap de Produto
   ```
   selic_target ~ selic_target_lag + inflação_desvio + gap_produto
   ```

3. **Modelo III**: Inflação + Gap + Câmbio
   ```
   selic_target ~ selic_target_lag + inflação_desvio + gap_produto + var_câmbio
   ```

Os parâmetros são estimados para períodos específicos definidos na configuração.

### Processamento de Dados

- **Filtro Hodrick-Prescott**: Utilizado para suavizar séries e extrair tendências (λ = 129.600)
- **Interpolação**: Para dados faltantes em expectativas de inflação
- **Sincronização de Datas**: Alinhamento de séries com diferentes frequências

## Como Usar

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Igor0Pires/selic-taylor-rule-insights.git
cd selic-taylor-rule-insights
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Execução

Execute o pipeline completo:
```bash
python main.py
```

Isto irá:
1. Carregar as configurações
2. Ingerir e processar os dados
3. Estimar os parâmetros da Regra de Taylor
4. Realizar análises estatísticas
5. Gerar visualizações

## Configuração

### `config/config.yaml`

Arquivo de configuração principal com os seguintes parâmetros:

- **paths**: Caminhos para dados e saídas
- **files_patterns**: Padrões de nomes dos arquivos de dados
- **ingestion**: Endpoints e configurações de coleta
- **processing**: Parâmetros de processamento (λ do filtro HP)
- **estimation**: Períodos para estimação e lags
- **visualization**: Configurações de gráficos

### Períodos de Estimação

Os períodos são configuráveis em `estimation.year_ranges`:
- 2002-2003 (com dummy 10/2002-03/2003)
- 2005-2007
- 2008-2009 (com dummy 09/2008-01/2009)
- 2011-2016 (com dummy 01/2015-12/2015)
- 2020-2025 (com dummy 03/2020-12/2020)

## Outputs

O projeto gera:

1. **Dados Processados** em `data/processed/`:
   - Dataset final com todas as séries sincronizadas
   - Séries de desvio de inflação
   - Gap de produto (filtro HP)
   - Variação de câmbio

2. **Resultados de Estimação**:
   - Coeficientes dos modelos
   - Estatísticas de ajuste (R², p-valores)
   - Análises por período

3. **Visualizações**:
   - Séries temporais das variáveis
   - Taxa SELIC observada vs. prevista pela Regra de Taylor
   - Evolução dos coeficientes ao longo do tempo
   - Gráficos de diagnóstico dos modelos

## Tecnologias

- **Python 3.x**
- **pandas**: Manipulação de dados
- **statsmodels**: Estimação econométrica
- **numpy**: Operações numéricas
- **matplotlib/seaborn**: Visualizações
- **PyYAML**: Configurações
- **requests**: Requisições HTTP

## Metodologia

A Função reação estimada é:
$$ 
 i_t = \alpha_1 i_{t-1}  + (1-\alpha_1) (\alpha_0 + \alpha_2(E_t\pi_{t+j} - \pi^*_{t+j}) + \alpha_3 \mathbb{y}_{t-1} + \alpha_4 \Delta e_{t-1})
$$


Onde:
- $i_t$: Taxa de juros (SELIC)
- $i_{t-1}$: Taxa de juros defasada
- $π_{t+j}$: Inflação esperada
- $π^*_{t+j}$: Meta de inflação
- $y_{t-1}$: Hiato do produto defasado
- $\Delta e_{t-1}$: Variação da taxa de câmbio defasada

## Logs

Os logs de execução são salvos em `logs/` e mostram:
- Status de cada etapa do pipeline
- Avisos sobre dados faltantes
- Estatísticas dos modelos
- Erros e exceções


## Contato

Para dúvidas ou sugestões, abra uma issue no repositório.:rocket:

---

**Última atualização**: Janeiro de 2026 