# Neuro-Symbolic Demo (Gene-Trait Association)

This small demo shows a clean, local, neuro-symbolic pipeline:
- A Prolog knowledge base (`genes.pl`) with `gene_assoc(Gene, Trait, Score)` facts and a couple rules.
- A lightweight Python interface `prolog_kb.py` that either uses `pyswip` + SWI-Prolog (if installed),
  or a safe fallback that parses `genes.pl` and answers a restricted set of queries in Python.
- `llm_client.py` — integration with OpenAI Chat API if you provide `OPENAI_API_KEY`; otherwise a heuristic fallback that uses known traits.
- `pipeline.py` — the orchestrator: it asks the LLM for DSL queries, runs them against the KB, and summarizes results.

## Quick start (Ubuntu / Debian)

1. Install SWI-Prolog (needed for full Prolog support; fallback works without it):
   ```bash
   sudo apt update
   sudo apt install swi-prolog
