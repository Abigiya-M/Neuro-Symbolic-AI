"""
pipeline.py
Run this script to interactively ask questions and get answers from the neuro-symbolic pipeline.

Usage examples:
  python pipeline.py --question "Which genes are associated with breast_cancer?"
  python pipeline.py   # interactive mode
"""
import argparse
from prolog_kb import parse_genes_pl, available_traits, query_dsl
from llm_client import generate_queries, summarize_results
import json

def run_question(question: str, kb_file: str = 'neuro_symbolic_ai/genes.pl'):
    # ensure KB parsed
    parse_genes_pl(kb_file)
    traits = available_traits(kb_file)
    print(f"Known traits in KB: {', '.join(traits)}\n")

    # ask the 'LLM' for candidate DSL queries
    dsl_queries = generate_queries(question)
    print('Generated DSL queries:')
    print(json.dumps(dsl_queries, indent=2))

    # run each DSL query
    all_results = []
    for q in dsl_queries:
        res = query_dsl(q, prolog_file=kb_file)
        print(f"\nResults for query {q}:\n  -> {len(res)} matches")
        for r in res[:10]:
            print(f"    - {r['gene']} | trait={r['trait']} | score={r['score']}")
        all_results.extend(res)
    # dedupe results by gene+trait
    uniq = {}
    for r in all_results:
        key = (r['gene'], r['trait'])
        if key not in uniq or r['score'] > uniq[key]['score']:
            uniq[key] = r
    final_results = sorted(list(uniq.values()), key=lambda x: -x['score'])

    # produce a final summary (LLM assisted or template)
    summary = summarize_results(question, final_results)
    print('\nFINAL SUMMARY:\n')
    print(summary)
    return final_results, summary

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', type=str, help='Question to ask the pipeline', default=None)
    parser.add_argument('--kb', type=str, help='Path to Prolog KB file', default='neuro_symbolic_ai/genes.pl')
    args = parser.parse_args()
    if args.question:
        run_question(args.question, kb_file=args.kb)
    else:
        print('Interactive demo. Type a question and press enter (empty to quit).')
        while True:
            q = input('> ').strip()
            if not q:
                break
            run_question(q, kb_file=args.kb)