import csv
import argparse
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def evaluate(pred_file, gt_file):
    print("=" * 60)
    print("AI2026 - EXACT MATCH EVALUATION")
    print(f"Predictions : {pred_file}")
    print(f"Ground Truth: {gt_file}")
    print("=" * 60)

    gt = {}
    with open(gt_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row:
                gt[row[0].strip()] = row[1].strip()

    pred = {}
    with open(pred_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row:
                pred[row[0].strip()] = row[1].strip()

    total = len(gt)
    correct = 0
    mismatches = []

    for qid, gt_ans in gt.items():
        p_ans = pred.get(qid, "")
        # Exact match comparison (case sensitive and case-insensitive check)
        is_em = (p_ans == gt_ans)
        if is_em:
            correct += 1
        else:
            mismatches.append((qid, p_ans, gt_ans))

    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\nResult: {correct}/{total} correct ({accuracy:.2f}% Exact Match)")
    
    if mismatches:
        print("\n--- Mismatches ---")
        for qid, p_ans, gt_ans in mismatches:
            print(f"[{qid}] Pred: '{p_ans}' | GT: '{gt_ans}'")
    else:
        print("\n🎉 PERFECT SCORE! 100% Exact Match on all queries!")
    print("=" * 60)
    return correct, total

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", type=str, default="submission.csv")
    parser.add_argument("--gt", type=str, default="Public data 1/sample_submission.csv")
    args = parser.parse_args()
    evaluate(args.pred, args.gt)
