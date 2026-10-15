#!/bin/bash
# Script chạy bài dự thi AI2026 Bảng C - Chủ đề 2

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "[CANH BAO] Bien moi truong OPENROUTER_API_KEY chua duoc set!"
    echo "Vui long export: export OPENROUTER_API_KEY=sk-or-v1-..."
    echo "hoac dien vao config.json"
fi

python main.py --data_dir "Public data 1/xlsx_files" --queries "Public data 1/queries.json" --output "submission.csv" "$@"
