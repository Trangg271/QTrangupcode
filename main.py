import os
import sys
import json
import csv
import time
import argparse

# Ensure utf-8 encoding on windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from excel_parser import get_excel_context
from formatter import clean_answer
from llm_agent import OpenRouterAgent, DEFAULT_MODEL

def load_config(config_path):
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    return {}

def parse_args():
    parser = argparse.ArgumentParser(
        description="AI2026 - Bang C - Chu de 2: Hoi dap tren bang tinh Excel"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="xlsx_files",
        help="Path to directory containing .xlsx files"
    )
    parser.add_argument(
        "--queries",
        type=str,
        default="queries.json",
        help="Path to queries.json"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="submission.csv",
        help="Path to output submission.csv"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=None,
        help="OpenRouter API key"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help="LLM model ID (default: qwen/qwen3.7-flash)"
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry run without calling API (useful for testing pipeline structure)"
    )
    return parser.parse_args()

def main():
    start_time = time.time()
    args = parse_args()

    # Load configuration if available
    config = load_config(args.config)
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY") or config.get("openrouter_api_key")

    # Resolve paths (fallback to 'Public data 1' if default not found in root)
    data_dir = args.data_dir
    if not os.path.isdir(data_dir):
        alt_data = os.path.join("Public data 1", "xlsx_files")
        if os.path.isdir(alt_data):
            data_dir = alt_data
            
    queries_path = args.queries
    if not os.path.isfile(queries_path):
        alt_queries = os.path.join("Public data 1", "queries.json")
        if os.path.isfile(alt_queries):
            queries_path = alt_queries

    print("=" * 60)
    print("AI2026 - CHỦ ĐỀ 2: HỎI ĐÁP TRÊN BẢNG TÍNH EXCEL")
    print(f"Data directory : {data_dir}")
    print(f"Queries file   : {queries_path}")
    print(f"Output CSV     : {args.output}")
    print(f"LLM Model      : {args.model}")
    print(f"Dry run mode   : {args.dry_run}")
    print("=" * 60)

    if not os.path.exists(queries_path):
        print(f"Error: queries file not found at '{queries_path}'", file=sys.stderr)
        sys.exit(1)

    with open(queries_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    print(f"Loaded {len(queries)} queries to process.")

    agent = None
    if not args.dry_run:
        if not api_key:
            print(
                "Error: OpenRouter API key not provided! Set OPENROUTER_API_KEY environment variable, "
                "or specify --api_key, or configure config.json.",
                file=sys.stderr
            )
            sys.exit(1)
        agent = OpenRouterAgent(api_key=api_key, model=args.model)

    # Cache parsed excel contexts to avoid re-parsing same xlsx file multiple times
    excel_cache = {}
    results = []

    for i, item in enumerate(queries, 1):
        q_id = item.get("id")
        file_name = item.get("file_name")
        query_text = item.get("query")

        q_start = time.time()
        print(f"\n[{i}/{len(queries)}] Processing {q_id} ({file_name})...")
        print(f"  Query: {query_text}")

        # Parse Excel context
        xlsx_file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(xlsx_file_path):
            print(f"  Warning: File '{xlsx_file_path}' does not exist!", file=sys.stderr)
            excel_context = ""
        else:
            if file_name not in excel_cache:
                excel_cache[file_name] = get_excel_context(xlsx_file_path)
            excel_context = excel_cache[file_name]

        if args.dry_run:
            raw_answer = "DRY_RUN_ANSWER"
        else:
            try:
                raw_answer, p_tok, c_tok = agent.query(excel_context, query_text)
                print(f"  Tokens: {p_tok} prompt + {c_tok} completion")
            except Exception as e:
                print(f"  Error calling LLM: {e}", file=sys.stderr)
                raw_answer = ""

        # Post-process answer to adhere strictly to Exact Match
        final_answer = clean_answer(raw_answer, query_text)
        q_elapsed = time.time() - q_start
        print(f"  -> Answer: {final_answer} ({q_elapsed:.2f}s)")

        results.append({"id": q_id, "answer": final_answer})

    # Write output submission.csv
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["id", "answer"])
        for r in results:
            writer.writerow([r["id"], r["answer"]])

    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"COMPLETED successfully! Output saved to: {args.output}")
    print(f"Total time elapsed: {total_time:.2f} seconds ({total_time/len(queries):.2f}s/query)")
    if agent:
        stats = agent.get_token_stats()
        print(f"Total tokens used : {stats['total_tokens']} (Prompt: {stats['prompt_tokens']}, Completion: {stats['completion_tokens']})")
        print(f"Estimated cost    : ${stats['estimated_cost_usd']:.5f} USD (Avg: ${stats['estimated_cost_usd']/len(queries):.5f}/query)")
        print(f"Cost limit check  : {'PASSED (<= $0.10/query)' if stats['estimated_cost_usd']/len(queries) <= 0.10 else 'FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
