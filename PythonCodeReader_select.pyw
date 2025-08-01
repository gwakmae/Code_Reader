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


def select_and_display_files():
    """
    사용자가 여러 파일 및 폴더를 선택하고, 선택한 파일/폴더 내 파일들의 내용과 인코딩 출력.
    (.py, .ipynb, .pyw 파일 지원)
    """

    # 기존 선택된 파일 목록 유지 (또는 초기화)
    if not hasattr(select_and_display_files, 'selected_files'):
        select_and_display_files.selected_files = []

    # 파일 선택 (여러 번 호출 가능하도록 askopenfilenames 사용)
    new_files = list(filedialog.askopenfilenames(
        title="Select Python Files",
        filetypes=[("Python Files", "*.py;*.ipynb;*.pyw"), ("All files", "*.*")]
    ))

    # 재귀적으로 폴더 내 파일 추가 (폴더 직접 선택 X, 파일 선택 대화상자에서 폴더 내용 보여줌)
    def add_files_from_folder(file_list):
        expanded_files = []
        for file_or_folder in file_list:
            if os.path.isdir(file_or_folder):
                for root, _, files in os.walk(file_or_folder):
                    for file in files:
                        if file.endswith(('.py', '.ipynb', '.pyw')):
                            expanded_files.append(os.path.join(root, file))
            else:  # 이미 파일인 경우
                expanded_files.append(file_or_folder)
        return expanded_files

    new_files = add_files_from_folder(new_files)  # 폴더 있으면 파일로 확장


    # 중복 제거 및 기존 목록에 추가
    select_and_display_files.selected_files = list(set(select_and_display_files.selected_files + new_files))
    file_paths = select_and_display_files.selected_files

    if not file_paths:
        return

    text_widget.delete("1.0", tk.END)  # 이전 내용 지우기

    try:
        text_widget.insert(tk.END, f"총 {len(file_paths)}개의 파일을 선택했습니다.\n\n")

        for full_path in file_paths:
            text_widget.insert(tk.END, "\n" + "=" * 60 + "\n")
            text_widget.insert(tk.END, f"File: {full_path}\n")
            text_widget.insert(tk.END, "=" * 60 + "\n")

            try:
                encoding = detect_encoding(full_path)
                text_widget.insert(tk.END, f"Detected Encoding: {encoding}\n")
                text_widget.insert(tk.END, "-" * 60 + "\n")

                with open(full_path, "r", encoding=encoding, errors='replace') as f:
                    content = f.read()
                text_widget.insert(tk.END, content + "\n")
            except Exception as e:
                text_widget.insert(tk.END, f"<< File read error: {e} >>\n")

    except Exception as e:
        text_widget.insert(tk.END, f"Error: {e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Python and IPython File Viewer")

open_button = tk.Button(root, text="Select Files and Folders", command=select_and_display_files)
open_button.pack(pady=10)

text_widget = scrolledtext.ScrolledText(root, width=80, height=30, wrap=tk.WORD)
text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()