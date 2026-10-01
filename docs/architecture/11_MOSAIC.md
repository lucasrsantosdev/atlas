# MOSAIC

## Versão

**Target:** v0.1  
**Projeto:** ATLAS.IA  
**Status:** Desenvolvimento Inicial

---

## Propósito

Mosaic é a engine de compreensão e preparação de contexto do Atlas.

Sua responsabilidade é entender o que o usuário está solicitando antes que um modelo de linguagem seja acionado.

O Mosaic deve ajudar o Atlas a reduzir chamadas desnecessárias aos modelos, reduzir o tamanho do contexto, selecionar informações relevantes e preservar a modularidade entre o Atlas Core e os modelos de linguagem.

O modelo de linguagem não é o Mosaic.

O Mosaic não é o Atlas.

O Mosaic é um componente do Atlas.

---

# Princípio Central

O fluxo básico deve ser:

```text
Usuário
  |
  v
Mosaic
  |
  |-- Intenção
  |-- Classificação da Tarefa
  |-- Entidades
  |-- Relevância
  |-- Contexto
  |
  v
MosaicResult
  |
  v
Atlas Core
  |
  v
Model Router
  |
  v
Modelo Selecionado