"""
prolog_kb.py
Lightweight Prolog KB interface. Works two ways:
1) If pyswip and SWI-Prolog are installed, it will use pyswip to run real Prolog queries.
2) Fallback: it parses `genes.pl` and runs a small in-Python query engine for the simple DSL used here.

DSL (Python dict) format expected by query_dsl():
  {
    "type": "find_genes",
    "trait": "breast_cancer",     # optional
    "min_score": 0.8,             # optional, default 0.0
    "max_results": 10             # optional
  }
"""
import re
from pathlib import Path
from typing import List, Dict

KB_FACTS: List[Dict] = []  # list of dicts: {"gene":..., "trait":..., "score":...}

def parse_genes_pl(path: str):
    """Parse gene_assoc facts from a Prolog file (simple regex-based parser)."""
    global KB_FACTS
    KB_FACTS = []
    text = Path(path).read_text(encoding='utf-8')
    # regex to capture facts like gene_assoc('BRCA1', 'breast_cancer', 0.98).
    pat = re.compile(r"gene_assoc\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([0-9]*\.?[0-9]+)\s*\)\s*\.")
    for m in pat.finditer(text):
        gene, trait, score = m.group(1), m.group(2), float(m.group(3))
        KB_FACTS.append({'gene': gene, 'trait': trait, 'score': score})
    # dedupe / sort
    KB_FACTS = sorted(KB_FACTS, key=lambda x: (x['trait'], -x['score']))
    return KB_FACTS

# Try to import pyswip if available
try:
    from pyswip import Prolog  # type: ignore
    PYSWIP_AVAILABLE = True
except Exception:
    PYSWIP_AVAILABLE = False

def query_with_pyswip_find_genes(trait: str = None, min_score: float = 0.0, max_results: int = 50, prolog_file: str = 'genes.pl'):
    """Use pyswip to consult the prolog file and return matching facts as dicts."""
    prolog = Prolog()
    prolog.consult(prolog_file)
    results = []
    # Build query; we always query gene_assoc(Gene, Trait, Score)
    if trait:
        q = f"gene_assoc(Gene,'{trait}',Score)"
    else:
        q = "gene_assoc(Gene,Trait,Score)"
    for r in prolog.query(q):
        gene = str(r.get('Gene'))
        trait_r = str(r.get('Trait'))
        score = float(r.get('Score'))
        if score >= min_score:
            results.append({'gene': gene, 'trait': trait_r, 'score': score})
    results.sort(key=lambda x: -x['score'])
    return results[:max_results]

def query_dsl(query: Dict, prolog_file: str = 'genes.pl') -> List[Dict]:
    """Execute a DSL query. Uses pyswip if available; otherwise fallbacks to the parsed KB."""
    qtype = query.get('type', 'find_genes')
    if qtype != 'find_genes':
        raise ValueError('Only find_genes queries are supported in this demo.')
    trait = query.get('trait', None)
    min_score = float(query.get('min_score', 0.0))
    max_results = int(query.get('max_results', 50))

    if PYSWIP_AVAILABLE:
        return query_with_pyswip_find_genes(trait=trait, min_score=min_score, max_results=max_results, prolog_file=prolog_file)

    # fallback: parse the prolog file into KB_FACTS and query in python
    if not KB_FACTS:
        parse_genes_pl(prolog_file)
    out = []
    for fact in KB_FACTS:
        if trait and fact['trait'] != trait:
            continue
        if fact['score'] < min_score:
            continue
        out.append(fact)
    out = sorted(out, key=lambda x: -x['score'])
    if max_results:
        out = out[:max_results]
    return out

def available_traits(prolog_file: str = 'genes.pl'):
    if not KB_FACTS:
        parse_genes_pl(prolog_file)
    return sorted({f['trait'] for f in KB_FACTS})

if __name__ == '__main__':
    print('Parsed facts:')
    parse_genes_pl('genes.pl')
    from pprint import pprint
    pprint(KB_FACTS)