import os
import zipfile

FILES_TO_PACK = [
    "main.py",
    "excel_parser.py",
    "llm_agent.py",
    "formatter.py",
    "evaluate.py",
    "config.json",
    "requirements.txt",
    "README.md",
    "run.sh",
    "run.bat"
]

OUTPUT_ZIP = "submission.zip"

def package():
    print(f"Creating {OUTPUT_ZIP}...")
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for fname in FILES_TO_PACK:
            if os.path.exists(fname):
                z.write(fname, fname)
                print(f"  + Added {fname}")
            else:
                print(f"  - Warning: Missing {fname}")
                
    size_bytes = os.path.getsize(OUTPUT_ZIP)
    size_mb = size_bytes / (1024 * 1024)
    print(f"\nCreated {OUTPUT_ZIP} successfully!")
    print(f"File size: {size_bytes} bytes ({size_mb:.2f} MB)")
    if size_mb < 100:
        print("[CHECK] Size is well within BTC limit (< 100 MB). PASSED!")
    else:
        print("[WARNING] Size exceeds 100 MB!")

if __name__ == "__main__":
    package()
