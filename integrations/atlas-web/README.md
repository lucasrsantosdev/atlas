# ATLAS Web

Interface oficial do ATLAS.IA.

## Arquitetura

O frontend pode aproveitar componentes e conceitos
desenvolvidos pelo Mosaic, mas o Atlas Core continua
sendo a autoridade do sistema.

Fluxo principal:

Usuario
↓
Atlas Web
↓
Atlas API
↓
Atlas Core
├─ Identity
├─ Security
├─ Memory
├─ Knowledge
├─ Model Router
└─ Tool Registry

Mosaic atua como camada auxiliar de compreensao e contexto.

As ferramentas, MCP e integracoes passam pelas politicas
de seguranca do Atlas.

## Regra

A interface nunca deve chamar diretamente recursos
privilegiados ignorando o Atlas Core.

## Primeira aplicacao

Atlas Educacional.
