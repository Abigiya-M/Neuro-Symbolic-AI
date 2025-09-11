# llm_client.py
from dotenv import load_dotenv
import os, json
from typing import List, Dict

load_dotenv()

# Load API keys
openai_key = os.environ.get("OPENAI_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY")

# Try OpenAI
client = None
if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
    except ImportError:
        client = None

# Try Gemini (always try if key exists, regardless of OpenAI)
gemini_client = None
if gemini_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        gemini_client = genai.GenerativeModel("gemini-1.5-flash")
    except ImportError:
        gemini_client = None


def generate_queries(question: str, traits: List[str] = None, n: int = 3) -> List[Dict]:
    """
    Generate DSL queries from a natural language question.
    """
    prompt = f"""
    You are a neuro-symbolic AI assistant.
    Given a natural language question about gene-trait associations,
    return a JSON array of up to {n} structured queries in this DSL:

    DSL format:
    {{
      "query": "gene_assoc(Gene, Trait, Score)",
      "filters": [{{"field": "Trait", "equals": "breast_cancer"}}]
    }}

    Known traits: {traits}

    Question: {question}
    """

    # Try OpenAI first
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            text = response.choices[0].message.content.strip()
            return json.loads(text)
        except Exception as e:
            print(f"[OpenAI Error, trying Gemini] {e}")

    # Try Gemini next
    if gemini_client:
        try:
            response = gemini_client.generate_content(prompt)
            text = response.text.strip()

            # Clean Gemini output if wrapped in ```json ... ```
            if text.startswith("```"):
                text = text.strip("`").replace("json", "", 1).strip()

            return json.loads(text)
        except Exception as e:
            print(f"[Gemini Error, using fallback queries] {e}")


def summarize_results(question: str, results: List[Dict]) -> str:
    """
    Summarize query results into natural language.
    """
    prompt = f"""
    Summarize the following results for the question: "{question}"

    Results: {results}
    """

    # Try OpenAI first
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[OpenAI Error, trying Gemini] {e}")

    # Try Gemini next
    if gemini_client:
        try:
            response = gemini_client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini Error, using fallback summary] {e}")

    # --- Fallback summarizer ---
    if not results:
        return "No results found."

    parts = []
    for r in results[:5]:
        gene = r.get("Gene") or r.get("gene") or "UnknownGene"
        trait = r.get("Trait") or r.get("trait") or "UnknownTrait"
        score = r.get("Score") or r.get("score") or "?"
        parts.append(f"{gene} (trait={trait}, score={score})")

    summary = f"Found {len(results)} results. " + ", ".join(parts)
    if len(results) > 5:
        summary += f", and {len(results) - 5} more..."
    return summary


def rule_based_queries(question: str, traits: List[str], n: int) -> List[Dict]:
    """
    Very simple keyword-based query generator as fallback.
    """
    q = question.lower()
    matches = []
    for t in traits or []:
        if t.lower().replace("_", " ") in q or t.lower() in q:
            matches.append({
                "query": "gene_assoc(Gene, Trait, Score)",
                "filters": [{"field": "Trait", "equals": t}]
            })
    if not matches:
        matches.append({"query": "gene_assoc(Gene, Trait, Score)", "filters": []})
    return matches[:n]
