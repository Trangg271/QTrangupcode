import re

def clean_answer(raw_answer, query):
    """
    Cleans and standardizes the LLM's raw answer according to the query's instructions
    to achieve 100% Exact Match.
    """
    if raw_answer is None:
        return ""
    
    text = str(raw_answer).strip()
    
    # 1. Look for FINAL_ANSWER: marker if present
    match = re.search(r'FINAL_ANSWER:\s*(.*)', text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    else:
        # Check if output has multiple lines; often the last line is the answer
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            # If the last line contains answer or is short, prefer the last line
            for l in reversed(lines):
                if not l.startswith(('#', '```', 'Note:', 'Explanation:')):
                    text = l
                    break

    # Strip surrounding markdown (quotes, backticks, bold, italic)
    text = re.sub(r'^[\s`"\'*]+|[\s`"\'*]+$', '', text)
    # Strip prefixes like "Answer:", "Result:"
    text = re.sub(r'^(?:Answer|Result|The answer is|Output)[:\s]+', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'^[\s`"\'*]+|[\s`"\'*]+$', '', text)
    
    q_lower = query.lower()

    # Rule 1: Yes or No
    if 'yes or no' in q_lower or "'yes' or 'no'" in q_lower or '"yes" or "no"' in q_lower:
        m = re.search(r'\b(yes|no)\b', text, re.IGNORECASE)
        if m:
            return 'Yes' if m.group(1).lower() == 'yes' else 'No'

    # Rule 2: Float rounded to two decimal places
    if 'rounded to two decimal places' in q_lower or 'two decimal places' in q_lower:
        # Check if question expects multiple decimal values (like `men, women`)
        # e.g., query 19: "Answer as `men, women`, using exactly two decimal places and separating the values with a comma and one space."
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        if len(nums) >= 2 and ('men, women' in q_lower or 'separated by a comma' in q_lower):
            val1 = float(nums[0])
            val2 = float(nums[1])
            return f"{val1:.2f}, {val2:.2f}"
        elif nums:
            val = float(nums[0])
            return f"{val:.2f}"

    # Rule 3: Two integers separated by comma and one space
    if 'two integers' in q_lower and 'separated by a comma and one space' in q_lower:
        nums = re.findall(r'-?\d[\d,]*', text)
        clean_nums = [n.replace(',', '') for n in nums if n.replace(',', '').isdigit()]
        if len(clean_nums) >= 2:
            return f"{clean_nums[0]}, {clean_nums[1]}"

    # Rule 4: Integer only (without commas or units)
    if 'integer' in q_lower or 'without commas or units' in q_lower:
        # If float with .0, extract integer
        m = re.search(r'-?\d[\d,]*', text)
        if m:
            int_str = m.group(0).replace(',', '')
            return int_str

    # Rule 5: Only last name
    if 'only the last name' in q_lower or 'last name' in q_lower:
        words = re.findall(r'[A-Za-z]+', text)
        if words:
            # If answer gave full name or multiple words, return the last word
            return words[-1]

    # Rule 6: Comma separated list (e.g. descending order)
    if 'separated by a comma and one space' in q_lower:
        parts = [p.strip().strip('"\'') for p in text.split(',') if p.strip()]
        return ", ".join(parts)

    # General cleanup: remove trailing punctuation like period if not part of a decimal
    if text.endswith('.') and not re.search(r'\d\.\d$', text):
        text = text[:-1].strip()

    return text
