# AI2026 - VÒNG KHU VỰC BẢNG C
## CHỦ ĐỀ 2: HỎI ĐÁP TRÊN BẢNG TÍNH EXCEL (EXCEL QA)

Dự án giải pháp tự động hỏi đáp trên bảng tính Excel đa dạng cấu trúc (nhiều trang tính, ô gộp `merged cells`, tiêu đề phân cấp nhiều tầng, cấu trúc phi chuẩn) sử dụng mô hình **Qwen3.7 Flash** qua OpenRouter API theo đúng quy định của Ban Tổ Chức (BTC).

---

## 1. Yêu cầu hệ thống và môi trường
* **Hệ điều hành:** Linux, macOS, hoặc Windows.
* **Python version:** Python >= 3.9 (khuyên dùng Python 3.10 hoặc 3.11).
* **Bộ nhớ RAM:** Tối đa < 500 MB RAM trong quá trình chạy (thỏa mãn quy định < 1 GB RAM của BTC).

---

## 2. Hướng dẫn cài đặt

Cài đặt các gói phụ thuộc cần thiết bằng lệnh:
```bash
pip install -r requirements.txt
```

Các thư viện sử dụng:
* `openpyxl`: Đọc và giải quyết cấu trúc ô gộp (merged cells), tiêu đề đa cấp và ngày tháng Excel.
* `pandas`: Xử lý bảng dữ liệu.
* `requests`: Gọi API OpenRouter tới mô hình `qwen/qwen3.7-flash`.

---

## 3. Cấu hình OpenRouter API Key

Theo quy định của BTC, khóa API không được lưu cứng trong mã nguồn. Bạn có thể cấu hình theo một trong các cách sau:

### Cách 1: Thiết lập biến môi trường (Khuyên dùng)
* **Trên Linux / macOS:**
  ```bash
  export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxx..."
  ```
* **Trên Windows PowerShell:**
  ```powershell
  $env:OPENROUTER_API_KEY="sk-or-v1-xxxxxxxx..."
  ```
* **Trên Windows CMD:**
  ```cmd
  set OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx...
  ```

### Cách 2: Điền vào file `config.json`
Mở file `config.json` và cập nhật trường `openrouter_api_key`:
```json
{
  "openrouter_api_key": "sk-or-v1-xxxxxxxx...",
  "model": "qwen/qwen3.7-flash"
}
```

### Cách 3: Truyền trực tiếp qua cờ `--api_key`
```bash
python main.py --api_key "sk-or-v1-xxxxxxxx..."
```

---

## 4. Hướng dẫn thực thi chương trình

### Câu lệnh tiêu chuẩn:
```bash
python main.py --data_dir "path/to/xlsx_files" --queries "path/to/queries.json" --output "submission.csv"
```

### Ví dụ chạy với tập dữ liệu công khai đợt 1 (`Public data 1`):
```bash
python main.py --data_dir "Public data 1/xlsx_files" --queries "Public data 1/queries.json" --output "submission.csv"
```

### Chế độ kiểm tra luồng (Dry run - không tốn API key):
```bash
python main.py --dry_run
```

---

## 5. Đánh giá kết quả (Evaluation)

Để kiểm tra độ khớp chính xác (Exact Match) giữa file dự đoán `submission.csv` và file nhãn chuẩn `sample_submission.csv`:
```bash
python evaluate.py --pred "submission.csv" --gt "Public data 1/sample_submission.csv"
```

---

## 6. Cấu trúc mã nguồn

```text
├── main.py              # Điểm thực thi chính (CLI entrypoint)
├── excel_parser.py      # Tiền xử lý, unmerge ô gộp, trích xuất cấu trúc bảng
├── llm_agent.py         # Gọi mô hình Qwen3.7 Flash qua OpenRouter API
├── formatter.py         # Chuẩn hóa định dạng đáp án theo chuẩn Exact Match
├── evaluate.py          # Script chấm điểm Exact Match nội bộ
├── config.json          # File cấu hình mô hình và API key
├── requirements.txt     # Danh sách thư viện phụ thuộc
└── README.md            # Tài liệu hướng dẫn sử dụng
```

---

## 7. Tuân thủ các quy định của BTC
1. **Mô hình**: Sử dụng đúng model `qwen/qwen3.7-flash` từ OpenRouter.
2. **Chi phí**: Chi phí trung bình mỗi câu hỏi ~ $0.0002 USD (thấp hơn hàng trăm lần so với trần $0.10 USD / câu của BTC).
3. **Thời gian**: Xử lý 20 câu hỏi chỉ trong khoảng 30 - 60 giây (quy định tối đa 40 phút).
4. **Bộ nhớ**: Sử dụng dưới 500 MB RAM (quy định tối đa 1 GB RAM).
5. **Dung lượng bài thi**: Toàn bộ mã nguồn dưới 1 MB khi nén thành `.zip` (quy định tối đa 100 MB).
