import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import chardet

def detect_encoding(file_path):
    """파일 인코딩 자동 감지 (정확도 향상)"""
    with open(file_path, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        return result['encoding'] or 'utf-8'  # 기본값 설정

def list_and_display_files():
    """
    선택된 폴더와 모든 하위 폴더 내의 .py, .html, .css, .js 파일 목록을 가져와 내용과 함께 출력합니다.
    (__init__.py 파일과 __pycache__, except, venv, archive 폴더 제외)
    """
    folder_path = filedialog.askdirectory(title="Select a Folder")
    if not folder_path:
        return

    text_widget.delete("1.0", tk.END)  # Clear previous content
    supported_files = []

    # 지원할 파일 확장자
    supported_extensions = ['.py', '.html', '.css', '.js']

    try:
        # 모든 하위 폴더 탐색
        for root_dir, dirs, files in os.walk(folder_path):
            # 제외할 폴더들 확인
            path_parts = root_dir.split(os.sep)
            if any(excluded in path_parts for excluded in ["__pycache__", "except", "venv", "archive"]):
                continue
                
            # 각 파일 확인
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                # 지원하는 확장자이고 __init__.py가 아닌 경우만 처리
                if file_ext in supported_extensions and file != "__init__.py":
                    full_path = os.path.join(root_dir, file)
                    supported_files.append((full_path, file_ext))
        
        # 찾은 파일 수 표시
        text_widget.insert(tk.END, f"총 {len(supported_files)}개의 지원 파일을 찾았습니다.\n")
        text_widget.insert(tk.END, f"(지원 확장자: {', '.join(supported_extensions)})\n\n")
        
        # 각 파일 내용 표시
        for full_path, file_ext in supported_files:
            # --- Display file name and separator ---
            text_widget.insert(tk.END, "\n" + "=" * 60 + "\n")
            text_widget.insert(tk.END, f"File: {full_path} ({file_ext[1:]} 파일)\n")
            text_widget.insert(tk.END, "=" * 60 + "\n")

            # --- Read and display file content ---
            try:
                encoding = detect_encoding(full_path)
                with open(full_path, "r", encoding=encoding, errors='replace') as f:
                    content = f.read()
                text_widget.insert(tk.END, content + "\n")
            except Exception as e:
                text_widget.insert(tk.END, f"<< File read error: {e} >>\n")

    except Exception as e:
        text_widget.insert(tk.END, f"Error reading folder:\n{e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Code File Lister and Viewer")

open_button = tk.Button(root, text="Select Folder", command=list_and_display_files)
open_button.pack(pady=10)

text_widget = scrolledtext.ScrolledText(root, width=80, height=30, wrap=tk.WORD)  # Increased width/height
text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
