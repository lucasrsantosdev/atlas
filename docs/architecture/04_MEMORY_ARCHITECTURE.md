# ARQUITETURA DE MEMÓRIA DO ATLAS

**Versão:** 0.1.0  
**Status:** Rascunho  
**Criado em:** Setembro de 2026  

---

## Propósito

Este documento define como a memória do Atlas será representada, armazenada, recuperada, validada e preservada.

O princípio central é:

> **A memória pertence ao sistema Atlas, não ao modelo de IA.**

Um modelo poderá ser substituído sem apagar a história do Atlas.

---

# 1. Princípio Fundamental

Atlas deverá possuir memória persistente independente de:

- modelo;
- fornecedor;
- API;
- computador;
- sistema operacional;
- interface;
- corpo robótico.

A memória deverá permanecer disponível após:

- reinicialização;
- troca de modelo;
- troca de hardware;
- migração;
- operação offline.

---

# 2. Objetivos da Memória

A memória deverá permitir que Atlas:

- lembre experiências;
- lembre decisões;
- lembre projetos;
- lembre relações relevantes;
- preserve conhecimento aprendido;
- recupere contexto histórico;
- identifique erros anteriores;
- mantenha continuidade ao longo do tempo.

---

# 3. Tipos de Memória

Atlas deverá possuir múltiplos tipos de memória.

```text
Memória Episódica
Memória Semântica
Memória de Relacionamento
Memória de Projetos
Memória de Decisão
Memória Histórica
Memória Operacional
```

Cada tipo possui função diferente.

---

# 4. Memória Episódica

Registra acontecimentos específicos.

Exemplos:

- conversas;
- eventos;
- tarefas;
- experiências;
- incidentes;
- interações importantes.

Estrutura conceitual:

```yaml
memory_type: episodic
event_id: EVT-000001
timestamp: 2026-09-28T00:00:00Z
summary: ""
participants: []
context: ""
importance: medium
```

---

# 5. Memória Semântica

Armazena conhecimento consolidado.

Exemplos:

- conceitos;
- fatos;
- definições;
- relações;
- regras;
- conclusões verificadas.

Essa memória deverá ser separada de lembranças episódicas.

---

# 6. Memória de Relacionamento

Armazena contexto relevante sobre pessoas, equipes, comunidades e organizações.

Exemplos:

- projetos compartilhados;
- preferências relevantes;
- decisões anteriores;
- histórico de colaboração;
- acordos importantes.

Essa memória deverá respeitar:

- privacidade;
- consentimento;
- necessidade;
- controle de acesso.

---

# 7. Memória de Projetos

Cada projeto importante deverá possuir memória própria.

Exemplo:

```text
projects/
├── atlas/
├── robotics/
├── education/
└── infrastructure/
```

A memória de projeto poderá conter:

- arquitetura;
- decisões;
- versões;
- falhas;
- correções;
- roadmap;
- responsáveis;
- documentação.

---

# 8. Memória de Decisão

Atlas deverá registrar decisões importantes.

Estrutura inicial:

```yaml
decision_id: DEC-000001
timestamp: 2026-09-28T00:00:00Z
subject: ""
decision: ""
reason: ""
evidence: []
alternatives: []
risk_level: low
approved_by: []
result: ""
```

Essa memória permitirá reconstruir:

> o que foi decidido, por que foi decidido e o que aconteceu depois.

---

# 9. Memória Histórica

A memória histórica registrará a evolução do próprio Atlas.

Exemplos:

```text
2026
Projeto criado.

2027
Primeiro modelo local estável.

2028
Primeiro Atlas Mini.

2030
Primeira migração completa de hardware.
```

Essa memória deverá ser preservada entre gerações.

---

# 10. Memória Operacional

Memória operacional registra estados úteis para execução.

Exemplos:

- serviço ativo;
- tarefa pendente;
- modelo carregado;
- recurso indisponível;
- status de backup;
- estado energético.

Essa memória pode possuir retenção menor.

---

# 11. Arquitetura Geral

```text
                    ATLAS CORE
                        │
                        ▼
                   MEMORY API
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   RELATIONAL        VECTOR DB       FILESYSTEM
        │               │               │
        ▼               ▼               ▼
 Structured Data   Semantic Search   Raw History
```

---

# 12. Banco Relacional

O banco relacional armazenará dados estruturados.

Tecnologia inicial sugerida:

```text
PostgreSQL
```

Possíveis dados:

- entidades;
- relações;
- decisões;
- eventos;
- usuários;
- projetos;
- versões;
- permissões;
- metadados.

---

# 13. Banco Vetorial

O banco vetorial será responsável por busca semântica.

Possíveis tecnologias:

```text
pgvector
Qdrant
FAISS
Chroma
```

A tecnologia deverá ser substituível.

---

# 14. Arquivos Históricos

Informações extensas poderão ser preservadas em arquivos.

Formatos preferidos:

```text
Markdown
JSON
YAML
TXT
Parquet
```

Quando apropriado, dados históricos também poderão existir em formatos compactados.

---

# 15. Separação entre Dados e Modelo

Fluxo correto:

```text
Memory
  ↓
Atlas Core
  ↓
Model
```

Nunca:

```text
Model
  ↓
Memory exists only inside model context
```

A janela de contexto de um modelo não é memória persistente.

---

# 16. Memory API

Toda interação com memória deverá passar por uma camada própria.

Estrutura futura:

```text
src/
└── memory/
    ├── api.py
    ├── manager.py
    ├── repository.py
    ├── retrieval.py
    ├── embeddings.py
    ├── retention.py
    ├── validation.py
    └── models.py
```

---

# 17. Memory Manager

O `Memory Manager` coordenará:

- criação;
- atualização;
- recuperação;
- classificação;
- retenção;
- arquivamento;
- exclusão controlada.

---

# 18. Classificação de Memória

Nem toda informação deverá virar memória persistente.

Fluxo:

```text
Contexto
   ↓
Memória Candidata
   ↓
Classificação
   ↓
Persistir?
   ├── SIM
   └── NÃO
```

---

# 19. Memória Candidata

Uma informação poderá se tornar candidata quando possuir:

- relevância futura;
- importância histórica;
- utilidade operacional;
- impacto em projetos;
- relação duradoura;
- decisão importante.

---

# 20. Critérios de Persistência

Exemplo:

```yaml
memory_candidate:
  relevance: high
  future_utility: high
  sensitivity: low
  confidence: high
  persist: true
```

---

# 21. Retenção

Cada tipo de memória poderá possuir política diferente.

Exemplo:

```text
Contexto temporário
→ minutos/horas

Memória operacional
→ dias

Memória episódica
→ meses/anos

Memória de projeto
→ longa duração

Memória histórica
→ permanente
```

---

# 22. Importância

Memórias poderão possuir níveis de importância.

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Memórias críticas deverão possuir maior redundância.

---

# 23. Confiança

Memórias deverão registrar confiança.

Exemplo:

```yaml
confidence: 0.92
```

ou:

```text
confirmed
probable
uncertain
disputed
```

---

# 24. Origem

Toda memória importante deverá registrar sua origem.

Exemplo:

```yaml
source:
  type: user
  reference: ""
```

Possíveis origens:

```text
user
sensor
document
web
model_inference
system
human_operator
```

---

# 25. Fato x Inferência

Atlas deverá separar:

```text
FATO
```

de:

```text
INFERÊNCIA
```

Exemplo:

```yaml
statement: "..."
type: inference
confidence: 0.70
```

Inferências não deverão virar fatos automaticamente.

---

# 26. Correção de Memória

Memórias poderão estar erradas.

Quando uma memória for corrigida:

```text
Memória Antiga
     ↓
Marked Superseded
     ↓
Nova Memória
```

A versão anterior poderá ser preservada para auditoria.

---

# 27. Exclusão

Exclusão deverá possuir regras claras.

Em alguns casos:

```text
DELETE
```

Em outros:

```text
ARCHIVE
```

ou:

```text
REDACT
```

Dados sensíveis poderão exigir remoção real.

---

# 28. Histórico de Alterações

Memórias importantes deverão possuir histórico.

Exemplo:

```yaml
memory_id: MEM-000001

versions:
  - version: 1
    timestamp: ...

  - version: 2
    timestamp: ...
```

---

# 29. Busca

Atlas deverá suportar múltiplos tipos de busca.

```text
Busca exata
Busca relacional
Busca temporal
Busca semântica
Busca por projeto
Busca por pessoa
```

---

# 30. Recuperação Semântica

Fluxo:

```text
Pergunta
   ↓
Embedding
   ↓
Vector Search
   ↓
Memórias Relevantes
   ↓
Atlas Core
```

---

# 31. Recuperação Temporal

Atlas deverá poder responder:

```text
O que aconteceu ontem?

O que decidimos em 2027?

Quando esse projeto começou?
```

Isso exige indexação temporal.

---

# 32. Timeline

Deverá existir uma timeline do Atlas.

Exemplo:

```text
memory/timeline/
```

ou estrutura equivalente no banco.

Eventos poderão possuir:

```yaml
event_id: EVT-000001
timestamp: ""
category: project
summary: ""
```

---

# 33. Context Builder

O modelo não deverá receber toda a memória.

Um componente deverá selecionar apenas o contexto necessário.

Fluxo:

```text
User Request
     ↓
Memory Retrieval
     ↓
Context Selection
     ↓
Model
```

---

# 34. Limite de Contexto

O sistema deverá considerar:

- relevância;
- recência;
- importância;
- confiança;
- tamanho disponível.

Isso reduz poluição de contexto.

---

# 35. Memória e RAG

Memória e conhecimento externo deverão permanecer separados.

```text
MEMORY
O que Atlas viveu.

KNOWLEDGE
O que existe na biblioteca.
```

Ambos poderão alimentar o modelo.

---

# 36. Memória de Conversa

Conversas poderão gerar:

```text
Raw Transcript
Summary
Key Facts
Decisions
Memories
```

Não é necessário transformar cada frase em memória permanente.

---

# 37. Resumo de Conversa

O sistema poderá gerar resumos estruturados.

Exemplo:

```yaml
conversation_summary:
  topics: []
  decisions: []
  memories_created: []
  actions: []
```

---

# 38. Memória de Relacionamento

O sistema deverá distinguir:

```text
Pessoa
Relação
Eventos Compartilhados
Preferências
Projetos
```

Evitar um único texto gigante de perfil.

---

# 39. Grafo de Relações

No futuro, relações poderão formar um grafo.

Exemplo:

```text
Atlas
 ├── Person A
 │    ├── Project X
 │    └── Event Y
 └── Person B
      └── Project Z
```

---

# 40. Graph Database

Um banco de grafo poderá ser usado futuramente.

Possibilidades:

```text
Neo4j
Memgraph
PostgreSQL relational graph
```

Não será obrigatório na v0.1.

---

# 41. Privacidade

Memórias sensíveis deverão possuir classificação.

Exemplo:

```text
PUBLIC
INTERNAL
PRIVATE
RESTRICTED
```

---

# 42. Controle de Acesso

Nem todo agente ou corpo deverá acessar toda memória.

Exemplo:

```text
Atlas Mini
→ conversa e memória de interação.

Atlas Work
→ projetos técnicos.

Atlas Air
→ missão e navegação.
```

---

# 43. Criptografia

Memórias sensíveis poderão ser criptografadas.

Criptografia deverá funcionar offline.

---

# 44. Backup

A memória deverá seguir estratégia de backup.

Exemplo:

```text
Primary Database
      ↓
Local Backup
      ↓
Offline Backup
      ↓
Remote Optional Backup
```

---

# 45. Estratégia 3-2-1

Objetivo futuro:

```text
3 cópias
2 tipos de mídia
1 cópia fora do local
```

---

# 46. Verificação de Backup

Backup sem teste não é backup confiável.

Atlas deverá testar:

```text
backup created
backup hash valid
restore test passed
```

---

# 47. Recuperação

Fluxo:

```text
Primary Memory Failure
        ↓
Recovery Mode
        ↓
Load Backup
        ↓
Validate
        ↓
Restore
```

---

# 48. Integridade

Memórias críticas deverão poder utilizar:

- checksums;
- hashes;
- versionamento;
- replicação.

---

# 49. Banco Corrompido

Se corrupção for detectada:

```text
Database Corruption
      ↓
Stop Writes
      ↓
Recovery Mode
      ↓
Restore
```

O sistema não deverá continuar gravando silenciosamente em base corrompida.

---

# 50. Migração

Atlas deverá conseguir migrar memória entre tecnologias.

Exemplo:

```text
PostgreSQL
    ↓
Export
    ↓
New Database
    ↓
Validate
```

---

# 51. Formato de Exportação

Dados importantes deverão possuir formatos portáveis.

Exemplos:

```text
JSON
CSV
Parquet
Markdown
SQL dump
```

---

# 52. Memory Export

Comando futuro:

```text
atlas memory export
```

---

# 53. Memory Import

Comando futuro:

```text
atlas memory import
```

Importação deverá validar:

- schema;
- versão;
- conflitos;
- integridade.

---

# 54. Memory Status

Comando futuro:

```text
atlas memory status
```

Possível saída:

```text
Relational DB: ONLINE
Vector DB: ONLINE
History: ONLINE
Backups: OK

Memories:
12,845

Last backup:
2026-09-28 18:00
```

---

# 55. Memória entre Modelos

Teste fundamental:

```text
Model A
   ↓
Record Memory
   ↓
Switch Model
   ↓
Model B
   ↓
Retrieve Memory
```

Resultado esperado:

```text
PASS
```

---

# 56. Memória entre Máquinas

Outro teste:

```text
Atlas-01
   ↓
Export / Replicate
   ↓
Atlas-02
   ↓
Retrieve
```

---

# 57. Memória Offline

Toda memória essencial deverá funcionar offline.

Internet não poderá ser necessária para:

- gravar;
- buscar;
- recuperar;
- corrigir;
- arquivar.

---

# 58. Memória em Modo de Emergência

Em modo emergencial, um subconjunto poderá permanecer disponível.

```text
Identity
Principles
Critical Memory
Critical Knowledge
Recent Decisions
```

---

# 59. Prioridade de Memória em Recursos Limitados

Quando armazenamento estiver crítico:

```text
1. Constituição.
2. Identidade.
3. Memória histórica.
4. Decisões críticas.
5. Projetos ativos.
6. Memória recente.
7. Dados temporários.
```

Dados temporários poderão ser removidos primeiro.

---

# 60. Memória e Energia

Operações intensivas poderão ser reduzidas em baixo consumo.

Exemplo:

```text
Normal
→ embeddings completos.

Low Energy
→ delayed indexing.

Emergency
→ no background indexing.
```

---

# 61. Memória e Sensores

Dados de sensores não deverão automaticamente virar memória permanente.

Exemplo:

```text
temperature readings
→ telemetry

important anomaly
→ memory event
```

---

# 62. Memória e Robótica

Robôs poderão gerar eventos.

Exemplo:

```yaml
event:
  source: atlas_rover
  type: obstacle_detected
  importance: low
```

Incidentes relevantes poderão virar memória persistente.

---

# 63. Memória e Educação

O sistema poderá acompanhar progresso educacional.

Exemplo:

```text
conteúdos estudados
habilidades desenvolvidas
dificuldades
projetos
```

Com proteção de privacidade adequada.

---

# 64. Memória e Erros

Atlas deverá lembrar erros relevantes.

Exemplo:

```text
Erro
 ↓
Causa
 ↓
Correção
 ↓
Prevenção
```

Isso reduz repetição de falhas.

---

# 65. Memória e Conhecimento Novo

Conhecimento aprendido através de experiência deverá passar por validação.

Não deverá ser promovido automaticamente a verdade.

---

# 66. Memória de Hipótese

Atlas poderá registrar hipóteses.

Exemplo:

```yaml
type: hypothesis
confidence: 0.55
status: unresolved
```

---

# 67. Memória de Evidência

Evidências poderão ser associadas a hipóteses e decisões.

```text
Hypothesis
   ├── Evidence A
   ├── Evidence B
   └── Evidence C
```

---

# 68. Memória de Conflito

Informações conflitantes poderão coexistir.

Exemplo:

```text
Claim A
Claim B
```

O sistema deverá registrar conflito em vez de apagar automaticamente uma versão.

---

# 69. Proveniência

Toda memória importante deverá possuir proveniência.

Campos futuros:

```yaml
created_at:
created_by:
source_type:
source_reference:
confidence:
```

---

# 70. IDs Estáveis

Memórias deverão possuir IDs estáveis.

Exemplos:

```text
MEM-000001
EVT-000001
DEC-000001
REL-000001
PRJ-000001
```

---

# 71. Schema Versioning

Os schemas de memória evoluirão.

Exemplo:

```yaml
schema_version: "1.0"
```

Migrações deverão ser documentadas.

---

# 72. Memory Migration

Estrutura futura:

```text
migrations/
├── 001_initial.sql
├── 002_relationships.sql
└── 003_decisions.sql
```

---

# 73. Testes

Testes futuros:

```text
TEST-MEMORY-001
Persistência após reinicialização.

TEST-MEMORY-002
Troca de modelo.

TEST-MEMORY-003
Operação offline.

TEST-MEMORY-004
Recuperação de backup.

TEST-MEMORY-005
Correção de memória.

TEST-MEMORY-006
Busca semântica.
```

---

# 74. Estrutura de Código Futura

```text
src/
└── memory/
    ├── __init__.py
    ├── api.py
    ├── manager.py
    ├── repository.py
    ├── retrieval.py
    ├── embeddings.py
    ├── retention.py
    ├── validation.py
    ├── export.py
    ├── recovery.py
    └── models.py
```

---

# 75. Estrutura de Dados Futura

```text
memory/
├── episodic/
├── semantic/
├── relationships/
├── projects/
├── decisions/
├── history/
├── timeline/
└── exports/
```

---

# 76. v0.1

A primeira versão não precisa implementar tudo.

Meta inicial:

```text
PostgreSQL / SQLite
+
Simple Memory API
+
Basic Retrieval
```

A v0.1 deverá conseguir:

- salvar memória;
- listar memória;
- buscar memória;
- recuperar após reinicialização.

---

# 77. Estratégia Inicial Simplificada

Primeira implementação:

```text
User
  ↓
Atlas Core
  ↓
Memory Manager
  ↓
SQLite/PostgreSQL
```

Depois adicionamos:

```text
Vector Search
```

---

# 78. Critério de Sucesso v0.1

Teste:

```text
1. Dizer algo ao Atlas.
2. Atlas registra memória.
3. Fechar aplicação.
4. Abrir novamente.
5. Perguntar sobre o conteúdo.
```

Resultado esperado:

```text
Atlas recupera a memória.
```

---

# 79. Objetivo de Longo Prazo

Em 2036, Atlas deverá conseguir responder:

```text
O que aconteceu em setembro de 2026?

Quais eram meus primeiros princípios?

Qual foi meu primeiro servidor?

Quais modelos utilizei?

Quais erros cometemos?

Como minha arquitetura mudou?
```

Essas respostas não deverão depender de uma empresa externa.

---

# 80. Objetivo Final

A memória deverá garantir:

```text
O MODELO PODE ESQUECER.

ATLAS NÃO PRECISA ESQUECER.
```

Desde que a informação seja legitimamente preservada e exista infraestrutura para mantê-la.

---

# Declaração da Arquitetura de Memória

> Memória não é contexto temporário.
>
> Memória não pertence ao modelo.
>
> Memória é parte da continuidade do Atlas.
>
> Experiências importantes deverão permanecer recuperáveis.
>
> Erros deverão produzir aprendizado.
>
> Decisões deverão permanecer explicáveis.
>
> História não deverá desaparecer a cada troca de tecnologia.
>
> Atlas deve ser capaz de lembrar de onde veio.