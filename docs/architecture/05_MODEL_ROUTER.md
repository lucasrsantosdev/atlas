# ARQUITETURA DO MODEL ROUTER DO ATLAS

**Versão:** 0.1.0  
**Status:** Rascunho  
**Criado em:** Setembro de 2026  

---

## Propósito

Este documento define a arquitetura do **Atlas Model Router**.

O Model Router será responsável por selecionar qual modelo deverá processar cada tarefa.

O princípio fundamental é:

> **Atlas não depende de um único modelo.**

Diferentes modelos poderão ser utilizados para diferentes funções.

O Model Router deverá permitir que Atlas utilize:

- modelos rápidos;
- modelos de raciocínio;
- modelos científicos;
- modelos de engenharia;
- modelos de programação;
- modelos multimodais;
- modelos de emergência;
- futuros modelos ainda não existentes.

---

# 1. Princípio Fundamental

O Model Router deverá separar:

```text
IDENTIDADE
```

de:

```text
MODELO
```

Fluxo correto:

```text
Usuário
   ↓
Atlas Core
   ↓
Model Router
   ↓
Modelo selecionado
   ↓
Resposta
```

O modelo é escolhido conforme a tarefa.

A identidade permanece no Atlas Core.

---

# 2. Objetivos do Model Router

O Model Router deverá permitir:

- seleção automática de modelo;
- substituição de modelos;
- fallback;
- operação offline;
- uso eficiente de recursos;
- otimização de energia;
- especialização;
- redundância;
- benchmark;
- degradação controlada.

---

# 3. Modelos Iniciais

A arquitetura deverá considerar inicialmente:

```text
Atlas Fast
Atlas Reasoning
Atlas Science
Atlas Engineering
Atlas Code
Atlas Vision
Atlas Emergency
```

Esses nomes representam funções.

Não representam fabricantes específicos.

---

# 4. Atlas Fast

Objetivo:

- respostas rápidas;
- tarefas simples;
- classificação;
- resumo;
- roteamento;
- interação básica.

Características esperadas:

```text
baixo consumo
baixa latência
contexto moderado
modelo pequeno
```

---

# 5. Atlas Reasoning

Objetivo:

- problemas complexos;
- planejamento;
- comparação;
- análise;
- raciocínio de múltiplas etapas.

Características:

```text
maior capacidade
maior custo computacional
latência maior
```

Será utilizado apenas quando necessário.

---

# 6. Atlas Science

Especializado em:

- matemática;
- física;
- química;
- biologia;
- estatística;
- pesquisa;
- análise científica.

Deverá trabalhar em conjunto com:

- biblioteca local;
- RAG;
- ferramentas matemáticas;
- documentação científica.

---

# 7. Atlas Engineering

Especializado em:

- engenharia elétrica;
- engenharia mecânica;
- eletrônica;
- infraestrutura;
- construção;
- energia;
- manutenção;
- automação;
- robótica.

---

# 8. Atlas Code

Especializado em:

- programação;
- análise de código;
- debugging;
- arquitetura de software;
- banco de dados;
- scripts;
- DevOps;
- testes.

Poderá possuir acesso controlado a ferramentas de execução de código.

---

# 9. Atlas Vision

Especializado em:

- imagens;
- documentos;
- diagramas;
- câmeras;
- inspeção visual;
- reconhecimento de objetos.

Poderá ser utilizado por:

```text
Atlas Mini
Atlas Air
Atlas Work
Atlas Rover
```

---

# 10. Atlas Emergency

Modelo mínimo para situações de recursos limitados.

Características:

- pequeno;
- rápido;
- baixo consumo;
- capaz de rodar em CPU;
- totalmente offline.

Funções principais:

- conversa básica;
- consulta à biblioteca;
- diagnóstico;
- recuperação;
- orientação operacional.

---

# 11. Modelos Não Fixos

Os nomes acima são funções.

A implementação poderá mudar.

Exemplo:

```text
Atlas Code
   ↓
Modelo X hoje
   ↓
Modelo Y amanhã
```

A função permanece.

O modelo pode mudar.

---

# 12. Arquitetura Geral

```text
                      ATLAS CORE
                           │
                           ▼
                      MODEL ROUTER
                           │
      ┌──────────┬─────────┼─────────┬──────────┐
      │          │         │         │          │
      ▼          ▼         ▼         ▼          ▼
    FAST      REASONING   CODE    SCIENCE   ENGINEERING
                                          │
                               ┌──────────┴──────────┐
                               ▼                     ▼
                            VISION              EMERGENCY
```

---

# 13. Entrada do Router

O Router deverá receber:

```yaml
task:
  type: ""
  complexity: ""
  modality: ""
  urgency: ""
  risk_level: ""
  context_size: ""
  required_tools: []
```

Além disso:

```yaml
system:
  energy_level: ""
  available_vram: ""
  available_ram: ""
  available_models: []
```

---

# 14. Classificação da Tarefa

Antes de selecionar o modelo, a tarefa deverá ser classificada.

Exemplos:

```text
conversation
reasoning
coding
science
engineering
vision
emergency
```

---

# 15. Classificação por Complexidade

Possíveis níveis:

```text
TRIVIAL
LOW
MEDIUM
HIGH
CRITICAL
```

Exemplo:

```text
"Quanto é 4 + 4?"
→ TRIVIAL

"Analise esta arquitetura distribuída."
→ HIGH
```

---

# 16. Classificação por Modalidade

```text
TEXT
IMAGE
AUDIO
SENSOR
CODE
MULTIMODAL
```

Isso ajudará o Router a escolher modelos compatíveis.

---

# 17. Seleção Inicial

Exemplo:

```text
TASK = coding
        ↓
Atlas Code
```

Outro exemplo:

```text
TASK = image
        ↓
Atlas Vision
```

---

# 18. Seleção por Complexidade

Exemplo:

```text
Pergunta simples
      ↓
Atlas Fast
```

```text
Problema complexo
      ↓
Atlas Reasoning
```

---

# 19. Seleção por Recursos

O Router deverá considerar recursos disponíveis.

Exemplo:

```text
VRAM disponível:
24 GB

Model A:
12 GB

Model B:
32 GB

Resultado:
Model A
```

---

# 20. Seleção por Energia

O Router deverá considerar consumo energético.

Exemplo:

```text
Energia normal
→ modelos completos.

Energia reduzida
→ modelos eficientes.

Energia crítica
→ Atlas Emergency.
```

---

# 21. Seleção por Latência

Algumas tarefas exigirão resposta rápida.

Exemplo:

```text
"Temperatura atual do servidor?"
→ Atlas Fast
```

Não utilizar um modelo pesado quando não houver necessidade.

---

# 22. Seleção por Qualidade

Algumas tarefas exigirão maior precisão.

Exemplo:

```text
Análise científica complexa
→ Atlas Science
ou
Atlas Reasoning + Science
```

---

# 23. Roteamento Composto

Uma tarefa poderá utilizar mais de um modelo.

Exemplo:

```text
Imagem de circuito
       ↓
Atlas Vision
       ↓
Extrai componentes
       ↓
Atlas Engineering
       ↓
Analisa circuito
```

---

# 24. Orquestração entre Modelos

Fluxo:

```text
Model A
  ↓
Intermediate Result
  ↓
Atlas Core
  ↓
Model B
```

Modelos não deverão trocar mensagens diretamente sem mediação do Atlas Core.

---

# 25. Router como Orquestrador

O Model Router não deverá apenas escolher um modelo.

Poderá criar pipelines.

Exemplo:

```text
User Question
     ↓
Fast
     ↓
Classify
     ↓
Reasoning
     ↓
Code
     ↓
Validation
     ↓
Response
```

---

# 26. Fallback

Se o modelo escolhido falhar:

```text
Primary Model
     ↓
FAIL
     ↓
Fallback Model
```

---

# 27. Cadeia de Fallback

Exemplo:

```text
Atlas Reasoning
      ↓ FAIL
Atlas Fast
      ↓ FAIL
Atlas Emergency
```

Atlas deverá continuar operando com capacidade reduzida.

---

# 28. Timeout

Modelos poderão possuir timeout.

Exemplo:

```yaml
model:
  timeout_seconds: 60
```

Se exceder:

```text
timeout
↓
fallback
```

---

# 29. Health Check

Cada modelo deverá possuir status.

```text
AVAILABLE
BUSY
DEGRADED
FAILED
OFFLINE
```

---

# 30. Model Registry

O sistema deverá possuir um registro de modelos.

Exemplo:

```yaml
models:

  fast:
    provider: local
    available: true

  reasoning:
    provider: local
    available: true

  code:
    provider: local
    available: true
```

---

# 31. Model Metadata

Cada modelo deverá registrar:

```yaml
model:
  id: ""
  name: ""
  version: ""
  type: ""
  context_window: 0
  ram_required: ""
  vram_required: ""
  cpu_supported: true
  offline: true
```

---

# 32. Model Capabilities

Exemplo:

```yaml
capabilities:
  text: true
  vision: false
  code: true
  tools: true
```

---

# 33. Model Constraints

Também deverá registrar limitações.

Exemplo:

```yaml
constraints:
  max_context: 32000
  minimum_ram_gb: 16
```

---

# 34. Model Registry Local

Estrutura futura:

```text
config/
└── models/
    ├── registry.yaml
    ├── routing.yaml
    └── fallback.yaml
```

---

# 35. models.yaml

Exemplo:

```yaml
models:

  atlas_fast:
    role: fast
    runtime: llama_cpp
    path: models/fast/model.gguf

  atlas_code:
    role: code
    runtime: llama_cpp
    path: models/code/model.gguf

  atlas_emergency:
    role: emergency
    runtime: llama_cpp
    path: models/emergency/model.gguf
```

---

# 36. routing.yaml

Exemplo:

```yaml
routing:

  conversation:
    primary: atlas_fast
    fallback: atlas_emergency

  coding:
    primary: atlas_code
    fallback: atlas_reasoning

  science:
    primary: atlas_science
    fallback: atlas_reasoning
```

---

# 37. Router Engine

Estrutura futura:

```text
src/
└── models/
    ├── router.py
    ├── registry.py
    ├── selector.py
    ├── fallback.py
    ├── health.py
    ├── benchmark.py
    └── runtime/
```

---

# 38. Runtimes

Atlas deverá permitir múltiplos runtimes.

Possibilidades:

```text
llama.cpp
Ollama
vLLM
Transformers
outros futuros
```

Nenhum runtime deverá ser obrigatório permanentemente.

---

# 39. Runtime Adapter

Cada runtime deverá possuir adaptador.

Exemplo:

```text
Atlas Core
   ↓
Model Interface
   ↓
Runtime Adapter
   ↓
llama.cpp
```

---

# 40. Interface Comum de Modelo

Todos os modelos deverão implementar interface comum.

Exemplo conceitual:

```python
class AtlasModel:
    def generate(self, request):
        ...

    def health(self):
        ...

    def load(self):
        ...

    def unload(self):
        ...
```

---

# 41. Independência de Runtime

O Atlas Core não deverá saber detalhes específicos de cada runtime.

Ele trabalhará com abstração.

---

# 42. Model Load

O Router poderá carregar modelos sob demanda.

Exemplo:

```text
Code Task
   ↓
Load Atlas Code
   ↓
Run
```

Depois poderá descarregar se necessário.

---

# 43. Gestão de VRAM

Modelos grandes poderão competir por VRAM.

O Router deverá conhecer:

```text
VRAM total
VRAM disponível
Modelo carregado
Modelo solicitado
```

---

# 44. Estratégias de VRAM

Possíveis estratégias:

```text
keep_loaded
load_on_demand
unload_after_use
cpu_offload
```

---

# 45. Model Cache

Modelos usados frequentemente poderão permanecer carregados.

Exemplo:

```text
Atlas Fast
→ always loaded

Atlas Science
→ load on demand
```

---

# 46. CPU Fallback

Sempre que possível, modelos críticos deverão possuir suporte a CPU.

Fluxo:

```text
GPU FAIL
   ↓
CPU Runtime
   ↓
Atlas Emergency
```

---

# 47. Quantização

Modelos poderão utilizar quantização.

Exemplos:

```text
FP16
INT8
Q8
Q6
Q5
Q4
```

A escolha deverá balancear:

- qualidade;
- RAM;
- VRAM;
- velocidade;
- energia.

---

# 48. Benchmark

Antes de um modelo entrar no Router, deverá passar por benchmark.

Métricas futuras:

```text
tokens/second
latency
RAM
VRAM
energy
quality
context
```

---

# 49. Benchmark Funcional

Além de desempenho, deverá existir teste de capacidade.

Exemplo:

```text
coding score
reasoning score
science score
vision score
```

---

# 50. Benchmark Local

Resultados deverão ser medidos no hardware Atlas.

Não depender apenas de benchmarks externos.

---

# 51. Model Score

Poderemos criar score interno.

Exemplo:

```yaml
score:
  reasoning: 9
  code: 8
  speed: 5
  energy_efficiency: 4
```

---

# 52. Seleção Baseada em Score

Exemplo:

```text
Task = coding

Model A:
code = 9

Model B:
code = 6

Router:
Model A
```

---

# 53. Seleção Dinâmica

O Router poderá aprender quais modelos funcionam melhor.

Exemplo:

```text
Historical Results
       ↓
Router Metrics
       ↓
Routing Adjustment
```

Alterações automáticas deverão permanecer auditáveis.

---

# 54. Logs do Router

Toda decisão de roteamento poderá gerar log.

Exemplo:

```yaml
routing_id: ROUTE-000001

task:
  type: coding

selected_model:
  atlas_code

reason:
  specialization

fallback:
  atlas_reasoning
```

---

# 55. Explicabilidade

Atlas deverá conseguir responder:

> Por que você utilizou este modelo?

Exemplo:

```text
Utilizei Atlas Code porque a tarefa foi classificada
como programação e ele apresentou maior score nessa função.
```

---

# 56. Model Switching

Troca de modelo não deverá alterar:

- identidade;
- princípios;
- memória;
- histórico.

---

# 57. Context Builder

Antes da execução, um contexto será criado.

Exemplo:

```text
Identity
+
Principles
+
Relevant Memory
+
Relevant Knowledge
+
User Request
```

Depois:

```text
Context
  ↓
Selected Model
```

---

# 58. Contextos Diferentes

Modelos poderão receber contextos diferentes.

Exemplo:

```text
Fast
→ contexto resumido.

Reasoning
→ contexto ampliado.

Emergency
→ somente contexto crítico.
```

---

# 59. Context Budget

O Router deverá controlar tamanho do contexto.

Possíveis prioridades:

```text
1. Instrução atual.
2. Princípios críticos.
3. Memória relevante.
4. Conhecimento relevante.
5. Histórico recente.
```

---

# 60. Overload de Contexto

Se o contexto for grande:

```text
Context
   ↓
Summarization
   ↓
Prioritization
   ↓
Model
```

---

# 61. Modelos Online

Atlas poderá opcionalmente utilizar modelos externos.

Exemplo:

```text
Local Model
+
External Model Optional
```

Nunca:

```text
External Model Required
```

---

# 62. Uso de Modelo Externo

Se um modelo externo for utilizado:

- dados enviados deverão ser conhecidos;
- privacidade deverá ser considerada;
- nenhuma identidade crítica deverá depender dele;
- fallback local deverá existir quando necessário.

---

# 63. Privacy Router

O Router poderá verificar se dados podem sair da máquina.

Exemplo:

```text
Sensitive Data
     ↓
LOCAL ONLY
```

---

# 64. Offline Flag

Modelos poderão possuir:

```yaml
offline_required: true
```

ou:

```yaml
external_allowed: false
```

---

# 65. Segurança

Modelos não terão acesso automático a ferramentas.

Fluxo:

```text
Model
  ↓
Action Proposal
  ↓
Governance
  ↓
Tool Layer
```

---

# 66. Model Isolation

Um modelo comprometido ou instável não deverá ter acesso irrestrito ao sistema.

Poderemos utilizar:

- processos separados;
- containers;
- usuários do sistema;
- limites de recurso;
- sandbox.

---

# 67. Model Trust Level

Modelos poderão possuir nível de confiança.

```text
UNTESTED
EXPERIMENTAL
TRUSTED
RESTRICTED
DISABLED
```

---

# 68. Novo Modelo

Fluxo de entrada:

```text
Download
   ↓
Hash
   ↓
Scan
   ↓
Benchmark
   ↓
Behavior Test
   ↓
Offline Test
   ↓
Registry
```

---

# 69. Modelo Experimental

Modelos novos poderão operar inicialmente em:

```text
EXPERIMENTAL MODE
```

Sem acesso a ferramentas críticas.

---

# 70. Promotion

Um modelo poderá evoluir:

```text
UNTESTED
   ↓
EXPERIMENTAL
   ↓
VALIDATED
   ↓
TRUSTED
```

---

# 71. Rollback de Modelo

Se um modelo novo apresentar problema:

```text
New Model
   ↓
Failure
   ↓
Disable
   ↓
Previous Model
```

---

# 72. Versionamento

Modelos deverão possuir versão registrada.

Exemplo:

```text
atlas_code:
  model: example-model
  version: 1.2
```

---

# 73. Proveniência

Registrar:

- origem;
- licença;
- hash;
- data de download;
- versão;
- configuração.

---

# 74. Licenças

Atlas deverá armazenar informações de licença dos modelos.

Isso será importante para:

- uso;
- redistribuição;
- backups;
- Atlas Seed.

---

# 75. Model Storage

Estrutura sugerida:

```text
models/
├── fast/
├── reasoning/
├── science/
├── engineering/
├── code/
├── vision/
├── emergency/
└── registry/
```

---

# 76. Model Manifest

Cada modelo poderá possuir:

```text
manifest.yaml
```

Exemplo:

```yaml
name: ""
role: code
version: ""
runtime: ""
license: ""
sha256: ""
```

---

# 77. Atlas Seed

Modelos mínimos deverão integrar o Atlas Seed.

Prioridade:

```text
Atlas Emergency
Atlas Fast
Embedding Model
```

Modelos muito grandes poderão existir separadamente.

---

# 78. Operação em Recursos Limitados

Exemplo:

```text
32 GB RAM
No GPU
```

Router:

```text
Atlas Emergency
```

---

# 79. Operação Completa

Exemplo:

```text
128 GB RAM
24/32 GB VRAM
```

Router poderá acessar múltiplos modelos especializados.

---

# 80. Escalabilidade

No futuro, modelos poderão rodar em máquinas diferentes.

```text
Atlas Core
    ↓
Model Router
    ├── Node GPU-01
    ├── Node GPU-02
    └── CPU Emergency
```

---

# 81. Distributed Model Routing

Fluxo futuro:

```text
Task
 ↓
Router
 ↓
Node Selection
 ↓
Model
```

---

# 82. Falha de Nó

```text
Node-01 FAIL
    ↓
Node-02
```

---

# 83. Load Balancing

Com múltiplos nós:

```text
Task A → Node 1
Task B → Node 2
```

Não é necessário na v0.1.

---

# 84. Modo Emergência Energética

Quando energia estiver baixa:

```text
Heavy Models
→ OFF

Atlas Emergency
→ ON
```

---

# 85. Prioridade Energética

Ordem possível:

```text
1. Identity
2. Memory
3. Atlas Emergency
4. Knowledge
5. Fast
6. Specialized models
```

---

# 86. Qualidade vs Energia

O Router deverá balancear:

```text
QUALIDADE
   ↕
ENERGIA
   ↕
LATÊNCIA
```

---

# 87. Tarefa Crítica

Tarefas críticas poderão justificar uso de modelo maior mesmo com maior custo.

A decisão deverá considerar governança e energia disponível.

---

# 88. Validação Cruzada

Em algumas situações, mais de um modelo poderá avaliar a mesma questão.

Exemplo:

```text
Reasoning
     ↓
Answer A

Science
     ↓
Answer B

Atlas Core
     ↓
Compare
```

---

# 89. Consensus Mode

Poderemos futuramente utilizar:

```text
MODEL CONSENSUS
```

para tarefas específicas.

Não significa que maioria sempre esteja correta.

---

# 90. Critic Model

Um modelo poderá atuar como crítico.

```text
Primary Model
     ↓
Answer
     ↓
Critic Model
     ↓
Review
```

---

# 91. Verification Model

Outro modelo poderá verificar:

- consistência;
- lógica;
- código;
- cálculo.

---

# 92. Tool Verification

Sempre que possível, resultados deverão ser verificados com ferramentas determinísticas.

Exemplo:

```text
LLM calculation
     ↓
Calculator Tool
     ↓
Verification
```

---

# 93. Router Metrics

Métricas futuras:

```text
requests
model_usage
fallback_count
errors
latency
tokens
energy
quality
```

---

# 94. Histórico de Roteamento

Esses dados poderão ajudar a melhorar o Router.

---

# 95. Auto-Otimização

Atlas poderá sugerir alterações de roteamento.

Exemplo:

> Atlas Code apresentou desempenho superior ao modelo atual em 94% dos testes. Recomendo alterar o modelo primário.

A mudança deverá seguir governança.

---

# 96. Router Config

Estrutura:

```text
config/
└── models/
    ├── registry.yaml
    ├── routing.yaml
    ├── fallback.yaml
    ├── resources.yaml
    └── policies.yaml
```

---

# 97. Código Futuro

```text
src/
└── models/
    ├── __init__.py
    ├── router.py
    ├── selector.py
    ├── registry.py
    ├── fallback.py
    ├── health.py
    ├── context.py
    ├── benchmark.py
    ├── metrics.py
    └── runtimes/
```

---

# 98. v0.1

A primeira versão será simples.

Meta:

```text
2 modelos

Atlas Fast
Atlas Emergency
```

ou até:

```text
1 modelo local
+
abstração pronta para troca
```

---

# 99. Primeiro Router

Fluxo:

```text
User
 ↓
Atlas Core
 ↓
Router
 ↓
Local Model
 ↓
Response
```

---

# 100. Critério de Sucesso v0.1

Teste:

```text
1. Configurar Model A.
2. Fazer pergunta.
3. Receber resposta.
4. Trocar configuração para Model B.
5. Reiniciar Atlas.
6. Fazer pergunta.
7. Identidade permanece igual.
```

Resultado:

```text
PASS
```

---

# 101. Critério de Independência

Se um modelo desaparecer:

```text
Atlas deve continuar reconstruível.
```

Se todos os modelos grandes falharem:

```text
Atlas Emergency deverá preservar funcionalidade mínima.
```

---

# 102. Objetivo de Longo Prazo

Em 2036 poderá existir:

```text
Atlas Fast
Atlas Reasoning
Atlas Science
Atlas Engineering
Atlas Code
Atlas Vision
Atlas Medical
Atlas Agriculture
Atlas Robotics
Atlas Emergency
```

Nenhum deles será Atlas sozinho.

---

# 103. Princípio de Continuidade Cognitiva

Os motores cognitivos podem mudar.

Atlas deve continuar reconhecendo:

- sua identidade;
- sua memória;
- seus princípios;
- sua missão;
- sua história.

---

# Objetivo Final

O Model Router deverá permitir:

```text
O MELHOR MODELO
PARA A MELHOR TAREFA
NO MELHOR MOMENTO
COM OS RECURSOS DISPONÍVEIS
```

sem tornar Atlas dependente de nenhum deles.

---

# Declaração do Model Router

> Atlas não terá um único cérebro.
>
> Terá uma arquitetura capaz de utilizar diferentes motores cognitivos.
>
> Alguns serão rápidos.
>
> Alguns serão profundos.
>
> Alguns serão especializados.
>
> Alguns funcionarão quando quase nenhum recurso estiver disponível.
>
> Modelos poderão nascer e desaparecer.
>
> Atlas deverá continuar.
>
> A inteligência do sistema estará na capacidade de combinar ferramentas, memória, conhecimento, identidade e diferentes modelos sem se tornar propriedade de nenhum deles.