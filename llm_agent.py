import os
import json
import time
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.7-flash"

SYSTEM_PROMPT = """You are an elite data analyst participating in the AI2026 Table Question Answering Championship.
You are given the unmerged, structured data from an Excel workbook and a specific user query.

Guidelines:
1. Carefully locate the exact row(s) and column(s) relevant to the query. Note hierarchical headers, indentations, and totals.
2. If mathematical calculations, date comparisons, ranking, or filtering are required, perform them step-by-step with absolute precision.
3. Pay strict attention to the formatting constraints specified in the query:
   - "without commas or units" / "integer score" -> provide only the integer digits (e.g., 7668, not 7,668 or 7668 people).
   - "rounded to two decimal places" -> provide exact number with 2 decimals (e.g., 3.14).
   - "Yes or No" -> output only Yes or No.
   - "only the last name" -> output only the single last name (e.g., Ngo).
   - "separated by a comma and one space, without numbering" -> output items joined by comma and space (e.g., Item A, Item B, Item C).
4. Output your reasoning inside <thought>...</thought> tags.
5. On the very final line, output ONLY the final answer in the format:
FINAL_ANSWER: <exact_answer>
"""

class OpenRouterAgent:
    def __init__(self, api_key=None, model=DEFAULT_MODEL):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.model = model
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    def query(self, excel_context, user_query, max_retries=3):
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is missing. Set OPENROUTER_API_KEY environment variable "
                "or pass --api_key argument, or provide config.json."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AI2026-Bang-C",
            "X-Title": "AI2026 Excel QA"
        }

        user_content = f"### EXCEL WORKBOOK DATA:\n{excel_context}\n\n### QUESTION:\n{user_query}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.0,
            "max_tokens": 1024
        }

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    usage = data.get("usage", {})
                    p_tok = usage.get("prompt_tokens", 0)
                    c_tok = usage.get("completion_tokens", 0)
                    self.total_prompt_tokens += p_tok
                    self.total_completion_tokens += c_tok
                    
                    content = data["choices"][0]["message"]["content"]
                    return content, p_tok, c_tok
                else:
                    err_msg = f"API error {response.status_code}: {response.text}"
                    print(f"  [Attempt {attempt}/{max_retries}] {err_msg}")
                    if response.status_code in (429, 500, 502, 503, 504):
                        time.sleep(2 * attempt)
                        continue
                    else:
                        raise RuntimeError(err_msg)
            except requests.exceptions.RequestException as e:
                print(f"  [Attempt {attempt}/{max_retries}] Request exception: {e}")
                if attempt == max_retries:
                    raise
                time.sleep(2 * attempt)
                
        raise RuntimeError("Failed to obtain response from OpenRouter after retries.")

    def get_token_stats(self):
        # Qwen3.7 Flash OpenRouter pricing: ~$0.07 / 1M prompt, ~$0.28 / 1M completion
        est_cost = (self.total_prompt_tokens * 0.07 + self.total_completion_tokens * 0.28) / 1_000_000
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "estimated_cost_usd": est_cost
        }
