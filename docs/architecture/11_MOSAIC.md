# MOSAIC

## Version

**Target:** v0.1  
**Project:** ATLAS.IA  
**Status:** Initial Development

---

## Purpose

Mosaic is the context comprehension and preparation engine of Atlas.

Its responsibility is to understand what the user is asking before a language model is invoked.

Mosaic should help Atlas reduce unnecessary model calls, reduce context size, select relevant information and preserve modularity between the Atlas Core and language models.

The language model is not Mosaic.

Mosaic is not Atlas.

Mosaic is a component of Atlas.

---

# Core Principle

The basic flow should be:

```text
User
  |
  v
Mosaic
  |
  |-- Intent
  |-- Task Classification
  |-- Entities
  |-- Relevance
  |-- Context
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
Selected Model