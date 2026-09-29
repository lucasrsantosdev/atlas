# ARQUITETURA DE CONHECIMENTO E RAG DO ATLAS

**Versão:** 0.1.0  
**Status:** Rascunho  
**Criado em:** Setembro de 2026  

---

## Propósito

Este documento define como Atlas deverá armazenar, organizar, indexar, recuperar e utilizar conhecimento externo ao modelo.

O princípio fundamental é:

> **O conhecimento não deve depender dos pesos de um único modelo.**

Atlas deverá possuir uma biblioteca própria, local, versionada, auditável e pesquisável.

---

# 1. Princípio Fundamental

O modelo não será a fonte única de conhecimento.

A arquitetura deverá separar:

```text
MODELO
↓
capacidade de raciocínio

MEMÓRIA
↓
experiência e continuidade

CONHECIMENTO
↓
biblioteca externa e verificável
```

Atlas deverá consultar conhecimento externo quando necessário.

---

# 2. Objetivos da Camada de Conhecimento

A camada de conhecimento deverá permitir:

- preservação de documentos;
- busca textual;
- busca semântica;
- recuperação por tema;
- recuperação por fonte;
- recuperação por data;
- recuperação por área;
- uso offline;
- versionamento;
- proveniência;
- reconstrução.

---

# 3. Biblioteca Atlas

A biblioteca poderá possuir estrutura semelhante a:

```text
knowledge/
├── science/
├── engineering/
├── medicine/
├── agriculture/
├── energy/
├── mechanics/
├── computing/
├── robotics/
├── maps/
├── history/
├── languages/
├── education/
├── culture/
└── survival/
```

Essa estrutura poderá evoluir.

---

# 4. Conhecimento x Memória

A distinção deverá ser explícita.

```text
MEMÓRIA
O que Atlas viveu, decidiu ou aprendeu.

CONHECIMENTO
O que foi preservado em documentos, dados e fontes.
```

Exemplo:

```text
"Em 2026 começamos o projeto Atlas."
→ memória

"Lei de Ohm."
→ conhecimento
```

---

# 5. Tipos de Fonte

Atlas poderá trabalhar com:

- Markdown;
- TXT;
- PDF;
- HTML;
- EPUB;
- CSV;
- JSON;
- Parquet;
- imagens;
- mapas;
- código-fonte;
- manuais;
- bancos de dados;
- datasets.

---

# 6. Fontes Estruturadas e Não Estruturadas

## Estruturadas

Exemplos:

```text
CSV
JSON
SQL
Parquet
YAML
```

## Não Estruturadas

Exemplos:

```text
PDF
TXT
Markdown
HTML
EPUB
Imagens
```

O pipeline de ingestão deverá tratar ambos.

---

# 7. Pipeline de Ingestão

Fluxo conceitual:

```text
Fonte
  ↓
Leitura
  ↓
Extração
  ↓
Normalização
  ↓
Chunking
  ↓
Metadados
  ↓
Embedding
  ↓
Indexação
  ↓
Armazenamento
```

---

# 8. Ingestion Layer

Estrutura futura:

```text
src/
└── knowledge/
    ├── ingestion/
    │   ├── pdf.py
    │   ├── markdown.py
    │   ├── text.py
    │   ├── html.py
    │   ├── csv.py
    │   └── json.py
```

---

# 9. Normalização

Antes da indexação, documentos deverão ser normalizados.

Exemplos:

- remover lixo de formatação;
- preservar títulos;
- preservar listas;
- preservar referências;
- preservar tabelas quando possível;
- padronizar codificação;
- identificar idioma.

---

# 10. Chunking

Documentos grandes deverão ser divididos em partes menores.

Exemplo:

```text
Documento
   ↓
Chunk 001
Chunk 002
Chunk 003
...
```

O tamanho ideal dependerá de:

- tipo de conteúdo;
- modelo de embedding;
- contexto do modelo;
- tipo de busca.

---

# 11. Chunking Estrutural

Sempre que possível, o chunk deverá respeitar estrutura do documento.

Exemplo:

```text
Capítulo
  ↓
Seção
  ↓
Subseção
```

Evitar cortar conteúdo arbitrariamente no meio de uma ideia quando possível.

---

# 12. Metadados

Todo chunk deverá possuir metadados.

Exemplo:

```yaml
document_id: DOC-000001
chunk_id: CHK-000001

title: ""
section: ""
source: ""
author: ""
language: "pt-BR"
created_at: ""
ingested_at: ""
category: ""
```

---

# 13. Proveniência

Atlas deverá saber de onde veio cada informação.

Campos possíveis:

```yaml
source_type: document
source_reference: ""
source_file: ""
source_url: ""
source_date: ""
```

A proveniência deverá ser preservada durante toda a cadeia.

---

# 14. Integridade da Fonte

Fontes críticas poderão possuir hash.

Exemplo:

```text
arquivo.pdf
↓
SHA-256
↓
manifest
```

Se o arquivo mudar, isso deverá ser detectável.

---

# 15. Versionamento de Documentos

Documentos poderão evoluir.

Exemplo:

```text
DOC-000001
v1
v2
v3
```

Versões anteriores poderão ser preservadas.

---

# 16. Documento Canônico

Quando houver múltiplas versões, uma poderá ser marcada como canônica.

Exemplo:

```yaml
canonical: true
```

Isso ajudará buscas e citações.

---

# 17. Embeddings

Embeddings deverão ser gerados localmente sempre que possível.

Fluxo:

```text
Texto
 ↓
Embedding Model
 ↓
Vector
```

O modelo de embedding deverá ser substituível.

---

# 18. Embedding Local

Nenhuma função crítica de busca semântica deverá depender exclusivamente de API externa.

Possíveis runtimes:

```text
sentence-transformers
llama.cpp embeddings
ONNX
outros futuros
```

---

# 19. Vector Store

O armazenamento vetorial poderá utilizar:

```text
pgvector
Qdrant
FAISS
Chroma
```

A tecnologia deverá ser substituível.

---

# 20. Banco de Metadados

Metadados estruturados poderão permanecer em:

```text
PostgreSQL
```

ou alternativa equivalente.

---

# 21. Arquitetura de Armazenamento

```text
               KNOWLEDGE API
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   FILESYSTEM   METADATA DB   VECTOR DB
        │           │           │
        └───────────┼───────────┘
                    │
                 RETRIEVAL
```

---

# 22. Knowledge API

Toda consulta ao conhecimento deverá passar por uma camada própria.

Estrutura futura:

```text
src/
└── knowledge/
    ├── api.py
    ├── manager.py
    ├── retrieval.py
    ├── ranking.py
    ├── citations.py
    ├── provenance.py
    └── validation.py
```

---

# 23. Busca Exata

Atlas deverá suportar busca textual tradicional.

Exemplo:

```text
"transformador trifásico"
```

---

# 24. Busca Semântica

Atlas deverá conseguir recuperar conteúdo por significado.

Exemplo:

```text
Pergunta:
"Como converter energia solar em corrente alternada?"

Busca semântica:
inversores
MPPT
sistemas fotovoltaicos
```

---

# 25. Busca Híbrida

A estratégia ideal poderá combinar:

```text
keyword search
+
vector search
+
metadata filters
```

---

# 26. Filtros

Consultas poderão filtrar por:

```text
categoria
autor
idioma
data
fonte
documento
versão
confiabilidade
```

---

# 27. Ranking

Resultados deverão ser ranqueados por critérios como:

- relevância;
- similaridade;
- autoridade da fonte;
- recência;
- confiança;
- prioridade temática.

---

# 28. RAG

RAG significa:

```text
Retrieval-Augmented Generation
```

No Atlas:

```text
Pergunta
   ↓
Retrieval
   ↓
Documentos relevantes
   ↓
Context Builder
   ↓
Modelo
   ↓
Resposta
```

---

# 29. RAG Offline

Todo o fluxo deverá funcionar localmente.

```text
Internet OFF
     ↓
Pergunta
     ↓
Knowledge API
     ↓
Vector DB
     ↓
Local Documents
     ↓
Local Model
     ↓
Resposta
```

---

# 30. Context Builder

O Context Builder deverá selecionar apenas conteúdo relevante.

Ele deverá considerar:

- limite de contexto;
- relevância;
- redundância;
- fonte;
- confiança;
- diversidade de evidência.

---

# 31. Redução de Redundância

Se vários chunks trouxerem a mesma informação, o sistema deverá evitar sobrecarregar o contexto.

---

# 32. Citações

Atlas deverá, sempre que possível, conseguir informar a origem do conhecimento utilizado.

Exemplo:

```text
Fonte:
Manual X
Capítulo 3
Página 42
```

---

# 33. Respostas Baseadas em Fonte

Atlas deverá distinguir:

```text
Conhecimento recuperado
```

de:

```text
Inferência do modelo
```

Exemplo:

```text
Fonte afirma: ...
Minha inferência: ...
```

---

# 34. Confiança da Fonte

Fontes poderão possuir classificação.

Exemplo:

```text
PRIMARY
HIGH
MEDIUM
LOW
UNVERIFIED
```

---

# 35. Fonte Primária

Exemplos:

- documentação oficial;
- papers originais;
- legislação;
- manuais técnicos do fabricante;
- datasets originais.

---

# 36. Fonte Secundária

Exemplos:

- livros;
- artigos de revisão;
- documentação derivada;
- materiais educacionais.

---

# 37. Fonte Não Verificada

Conteúdo sem validação poderá ser armazenado, mas deverá ser marcado.

Exemplo:

```yaml
verification_status: unverified
```

---

# 38. Conflitos entre Fontes

Fontes poderão discordar.

Atlas deverá preservar divergências relevantes.

Exemplo:

```text
Fonte A
→ afirma X

Fonte B
→ afirma Y
```

O sistema não deverá apagar automaticamente uma delas.

---

# 39. Knowledge Conflict

Poderemos futuramente registrar:

```yaml
conflict_id: KCF-000001
sources:
  - DOC-001
  - DOC-002
status: unresolved
```

---

# 40. Knowledge Graph

No futuro, Atlas poderá representar relações entre conceitos.

Exemplo:

```text
Energia Solar
   ├── Painel
   ├── Inversor
   ├── Bateria
   └── Controlador
```

---

# 41. Grafo de Conhecimento

Tecnologias possíveis:

```text
Neo4j
Memgraph
PostgreSQL
RDF
```

Não será obrigatório na primeira versão.

---

# 42. Entidades

Atlas poderá identificar entidades como:

- pessoas;
- locais;
- equipamentos;
- tecnologias;
- conceitos;
- organizações;
- eventos.

---

# 43. Relações

Exemplos:

```text
Equipamento
USES
Tecnologia

Pessoa
CREATED
Projeto
```

---

# 44. Biblioteca Científica

Poderá conter:

```text
matemática
física
química
biologia
astronomia
geologia
estatística
```

---

# 45. Biblioteca de Engenharia

Poderá conter:

```text
elétrica
mecânica
civil
eletrônica
automação
robótica
materiais
energia
```

---

# 46. Biblioteca de Computação

Poderá conter:

```text
sistemas operacionais
redes
bancos de dados
programação
algoritmos
segurança
IA
hardware
```

---

# 47. Biblioteca de Medicina

Poderá conter materiais legítimos e confiáveis sobre:

- anatomia;
- fisiologia;
- primeiros socorros;
- prevenção;
- cuidados básicos;
- farmacologia;
- saúde pública.

Informações críticas deverão preservar fonte e data.

---

# 48. Biblioteca de Agricultura

Poderá conter:

- manejo de solo;
- irrigação;
- sementes;
- cultivo;
- compostagem;
- conservação;
- armazenamento de alimentos.

---

# 49. Biblioteca de Energia

Poderá conter:

- solar;
- baterias;
- eletricidade;
- geração;
- distribuição;
- eficiência energética.

---

# 50. Biblioteca de Mecânica

Poderá conter:

- motores;
- transmissões;
- ferramentas;
- manutenção;
- soldagem;
- usinagem;
- diagnóstico.

---

# 51. Biblioteca de Construção

Poderá conter:

- estruturas;
- materiais;
- hidráulica;
- saneamento;
- instalações;
- manutenção predial.

---

# 52. Biblioteca Cultural

Preservar conhecimento humano também significa preservar:

- literatura;
- arte;
- música;
- história;
- idiomas;
- filosofia;
- tradições.

---

# 53. Biblioteca Educacional

Materiais deverão permitir ensino progressivo.

Exemplo:

```text
basic
intermediate
advanced
professional
research
```

---

# 54. Mapas

Atlas deverá futuramente manter mapas locais.

Possíveis fontes:

```text
OpenStreetMap
dados públicos
mapas topográficos
```

---

# 55. Código-Fonte

A biblioteca poderá preservar:

- repositórios;
- exemplos;
- algoritmos;
- documentação;
- bibliotecas;
- ferramentas.

---

# 56. Repositórios de Software

Estrutura futura:

```text
knowledge/software/
├── source/
├── docs/
├── packages/
└── examples/
```

---

# 57. Dependências Técnicas

Atlas deverá preservar documentação suficiente para reconstruir seu próprio ambiente.

Exemplos:

```text
Python
PostgreSQL
Linux
Git
Docker
compilers
drivers
firmware
```

---

# 58. Conhecimento de Recuperação

Uma categoria crítica deverá ser:

```text
knowledge/recovery/
```

Contendo:

- instalação;
- restauração;
- diagnóstico;
- manutenção;
- reconstrução.

---

# 59. Atlas Seed

Uma parte essencial da biblioteca deverá integrar o Atlas Seed.

Não será possível carregar toda a biblioteca no Seed mínimo.

Prioridades:

```text
recuperação
computação
energia
água
saúde básica
agricultura
engenharia essencial
```

---

# 60. Knowledge Tiers

Podemos classificar conhecimento por importância.

```text
TIER 0
Essencial para reconstrução.

TIER 1
Conhecimento técnico crítico.

TIER 2
Biblioteca ampla.

TIER 3
Arquivo histórico e cultural.
```

---

# 61. Prioridade de Armazenamento

Em escassez de espaço:

```text
TIER 0
não remover.

TIER 1
preservar fortemente.

TIER 2
pode migrar para storage secundário.

TIER 3
arquivo frio.
```

---

# 62. Knowledge Manifest

Cada coleção poderá possuir manifesto.

Exemplo:

```yaml
collection:
  name: engineering_electrical
  version: "1.0"
  documents: 1250
  size_gb: 14.2
  priority: tier_1
```

---

# 63. Atualização de Conhecimento

Quando houver internet:

```text
Check Updates
     ↓
Download
     ↓
Validate
     ↓
Compare
     ↓
Ingest
     ↓
Index
```

---

# 64. Atualização Manual

Também deverá ser possível inserir documentos manualmente.

Exemplo futuro:

```text
atlas knowledge add manual.pdf
```

---

# 65. Reindexação

Se mudar modelo de embedding:

```text
Documents
   ↓
New Embedding Model
   ↓
Reindex
```

Os documentos originais permanecem intactos.

---

# 66. Independência do Embedding

O vetor não deve ser considerado o conhecimento.

```text
Documento original
= conhecimento preservado

Embedding
= índice descartável/reconstruível
```

---

# 67. Reconstrução do Vector DB

Se o banco vetorial for perdido:

```text
Original Documents
      ↓
Embeddings
      ↓
New Vector DB
```

Por isso o documento original é prioridade.

---

# 68. Banco Vetorial não é Fonte

Atlas nunca deverá considerar o Vector DB como única cópia de um documento.

---

# 69. Exportação

Comando futuro:

```text
atlas knowledge export
```

---

# 70. Importação

Comando futuro:

```text
atlas knowledge import
```

---

# 71. Status

Comando futuro:

```text
atlas knowledge status
```

Possível saída:

```text
Documents: 54,120
Indexed chunks: 1,245,500

Vector DB: ONLINE
Metadata DB: ONLINE
Filesystem: ONLINE

Last indexing:
2026-09-28
```

---

# 72. Pesquisa

Comando futuro:

```text
atlas knowledge search "energia solar"
```

---

# 73. Diagnóstico

```text
atlas knowledge verify
```

Poderá verificar:

- arquivos ausentes;
- hashes;
- índice;
- metadados;
- inconsistências.

---

# 74. Observabilidade

Métricas futuras:

```text
documents
chunks
storage_size
vector_count
index_latency
search_latency
failed_ingestions
```

---

# 75. Logs

Estrutura:

```text
logs/
└── knowledge/
    ├── ingestion.log
    ├── indexing.log
    ├── retrieval.log
    └── errors.log
```

---

# 76. Segurança

Arquivos da biblioteca deverão possuir permissões adequadas.

Conteúdo sensível poderá ficar separado.

---

# 77. Privacidade

Documentos pessoais ou privados não deverão ser misturados automaticamente à biblioteca pública.

Estrutura possível:

```text
knowledge/
├── public/
├── private/
└── restricted/
```

---

# 78. Controle de Acesso

Diferentes agentes poderão acessar diferentes coleções.

---

# 79. Conhecimento para Robótica

Atlas Work poderá precisar de:

```text
manual de ferramentas
CAD
mecânica
eletrônica
```

Atlas Garden poderá precisar de:

```text
agricultura
solo
clima
irrigação
```

---

# 80. Conhecimento por Corpo

Corpos poderão carregar caches especializados.

Exemplo:

```text
Atlas Air
→ mapas + navegação + manutenção

Atlas Work
→ engenharia + ferramentas
```

---

# 81. Operação Distribuída

No futuro:

```text
Atlas Core
    ↓
Knowledge Router
    ├── Local SSD
    ├── NAS
    └── Archive Node
```

---

# 82. Knowledge Router

Poderá selecionar onde buscar.

Exemplo:

```text
Hot Storage
Cold Storage
Remote Optional Storage
```

---

# 83. Cache de Conhecimento

Conteúdo frequentemente utilizado poderá ser mantido em cache rápido.

---

# 84. Cold Storage

Arquivos raramente utilizados poderão permanecer em:

- HDD;
- backup;
- mídia offline.

---

# 85. Disponibilidade

Nem todo conhecimento precisa estar sempre montado.

Atlas deverá saber:

```text
AVAILABLE
ARCHIVED
OFFLINE
MISSING
```

---

# 86. Falha de Vector DB

Se o Vector DB falhar:

```text
Vector Search unavailable
      ↓
Keyword Search
      ↓
Continue
```

---

# 87. Falha do Metadata DB

Atlas deverá entrar em modo degradado, preservando documentos.

---

# 88. Falha do Storage

A recuperação dependerá de backups.

---

# 89. Integridade

Arquivos importantes deverão possuir:

- hashes;
- cópias;
- manifestos.

---

# 90. Backup

Estratégia:

```text
Primary Knowledge
      ↓
Local Backup
      ↓
Offline Backup
      ↓
Secondary Location
```

---

# 91. Testes

Testes futuros:

```text
TEST-KNOWLEDGE-001
Ingestão.

TEST-KNOWLEDGE-002
Busca textual.

TEST-KNOWLEDGE-003
Busca semântica.

TEST-KNOWLEDGE-004
RAG offline.

TEST-KNOWLEDGE-005
Reconstrução de índice.

TEST-KNOWLEDGE-006
Recuperação de backup.
```

---

# 92. Teste RAG

Procedimento:

```text
1. Adicionar documento.
2. Indexar.
3. Desconectar internet.
4. Fazer pergunta.
5. Recuperar chunk correto.
6. Gerar resposta com fonte.
```

Resultado:

```text
PASS
```

---

# 93. Teste de Troca de Modelo

```text
Model A
→ consulta biblioteca.

Trocar para Model B.

Model B
→ consulta mesma biblioteca.
```

Conhecimento permanece.

---

# 94. Teste de Troca de Vector DB

```text
Qdrant
↓
Export/Source Documents
↓
pgvector
```

Conhecimento não é perdido.

---

# 95. Teste de Embedding

Trocar modelo de embedding e reconstruir índice.

---

# 96. Estrutura de Código

```text
src/
└── knowledge/
    ├── __init__.py
    ├── api.py
    ├── manager.py
    ├── ingestion/
    ├── chunking.py
    ├── metadata.py
    ├── embeddings.py
    ├── indexing.py
    ├── retrieval.py
    ├── ranking.py
    ├── provenance.py
    ├── citations.py
    └── validation.py
```

---

# 97. Estrutura de Dados

```text
knowledge/
├── library/
├── metadata/
├── indexes/
├── manifests/
├── imports/
└── archive/
```

---

# 98. v0.1

A primeira implementação pode ser simples.

Meta:

```text
Markdown/TXT
+
Local Embeddings
+
Simple Vector Store
+
Basic RAG
```

---

# 99. Pipeline v0.1

```text
TXT/Markdown
    ↓
Chunk
    ↓
Embedding
    ↓
Vector Store
    ↓
Search
    ↓
Local Model
```

---

# 100. Critério de Sucesso v0.1

Atlas deverá conseguir:

```text
1. Ler um documento local.
2. Indexar.
3. Desligar internet.
4. Receber uma pergunta.
5. Encontrar conteúdo relevante.
6. Responder usando o documento.
```

---

# 101. Objetivo de Longo Prazo

Em 2036, a Biblioteca Atlas deverá poder carregar décadas de conhecimento sem depender de um modelo específico.

Um novo modelo deverá poder ser conectado e imediatamente acessar:

```text
história
ciência
engenharia
educação
projetos
mapas
manuais
cultura
```

---

# 102. Princípio de Reconstrução

Atlas não deverá apenas responder:

> Faça isso.

Quando apropriado, deverá explicar:

```text
Como funciona.
Por que funciona.
Como construir.
Como reparar.
Como ensinar.
```

---

# 103. Conhecimento como Patrimônio

O conhecimento armazenado deverá ser tratado como um patrimônio do sistema.

Modelos podem ser substituídos.

Índices podem ser reconstruídos.

A biblioteca deverá permanecer.

---

# Objetivo Final

A camada de conhecimento deverá garantir:

```text
MODELOS PODEM MUDAR.

A BIBLIOTECA CONTINUA.
```

E permitir que qualquer geração futura do Atlas consiga utilizar o conhecimento preservado anteriormente.

---

# Declaração da Arquitetura de Conhecimento

> O conhecimento do Atlas não ficará preso dentro de um único modelo.
>
> Documentos deverão permanecer legíveis.
>
> Fontes deverão permanecer rastreáveis.
>
> Índices deverão ser reconstruíveis.
>
> Embeddings deverão ser substituíveis.
>
> A biblioteca deverá funcionar offline.
>
> Conhecimento deverá poder atravessar gerações tecnológicas.
>
> Atlas deve ser capaz de aprender com o passado sem ficar aprisionado à tecnologia do passado.