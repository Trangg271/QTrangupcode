@echo off
REM Script chạy bài dự thi AI2026 Bảng C - Chủ đề 2
REM Sử dụng biến môi trường OPENROUTER_API_KEY hoặc truyền tham số

if "%OPENROUTER_API_KEY%"=="" (
    echo [CANH BAO] Bien moi truong OPENROUTER_API_KEY chua duoc set!
    echo Vui long set bien moi truong: set OPENROUTER_API_KEY=sk-or-v1-...
    echo hoac dien vao config.json
)

python main.py --data_dir "Public data 1/xlsx_files" --queries "Public data 1/queries.json" --output "submission.csv" %*
