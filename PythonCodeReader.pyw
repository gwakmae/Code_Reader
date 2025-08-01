import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import chardet

# 현재 선택된 폴더 경로를 저장할 전역 변수
current_folder_path = None

def detect_encoding(file_path):
    """파일 인코딩 자동 감지 (정확도 향상)"""
    with open(file_path, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        return result['encoding'] or 'utf-8'  # 기본값 설정

def should_exclude_directory(dir_name):
    """제외할 디렉토리 이름인지 확인"""
    excluded_dirs = {
        "__pycache__", 
        ".venv", 
        "venv", 
        ".env",
        "env",
        "except", 
        "archive", 
        "build", 
        "dist", 
        "resources",
        ".git",
        "node_modules",
        ".pytest_cache"
    }
    return dir_name in excluded_dirs or dir_name.startswith('.')

def scan_and_display_files(folder_path):
    """
    지정된 폴더와 모든 하위 폴더 내의 .py 파일 목록을 가져와 내용과 함께 출력합니다.
    """
    text_widget.delete("1.0", tk.END)  # 이전 내용 지우기
    python_files = []

    try:
        # 모든 하위 폴더 탐색
        for root_dir, dirs, files in os.walk(folder_path):
            # 제외할 디렉토리들을 dirs 리스트에서 제거 (탐색 자체를 방지)
            dirs[:] = [d for d in dirs if not should_exclude_directory(d)]
            
            # 각 파일 확인
            for file in files:
                # .py 파일이고 __init__.py가 아닌 경우만 처리
                if file.endswith(".py") and file != "__init__.py":
                    full_path = os.path.join(root_dir, file)
                    python_files.append(full_path)
        
        # 찾은 파일 수 표시
        text_widget.insert(tk.END, f"총 {len(python_files)}개의 Python 파일을 찾았습니다.\n\n")
        
        if not python_files:
            text_widget.insert(tk.END, "Python 파일을 찾을 수 없습니다.")
            return
        
        # 각 파일 내용 표시
        for i, full_path in enumerate(python_files, 1):
            # --- 파일명과 구분선 표시 ---
            text_widget.insert(tk.END, "\n" + "=" * 80 + "\n")
            text_widget.insert(tk.END, f"파일 {i}/{len(python_files)}: {full_path}\n")
            text_widget.insert(tk.END, "=" * 80 + "\n")

            # --- 파일 내용 읽기 및 표시 ---
            try:
                encoding = detect_encoding(full_path)
                with open(full_path, "r", encoding=encoding, errors='replace') as f:
                    content = f.read()
                    if content.strip():  # 빈 파일이 아닌 경우만
                        text_widget.insert(tk.END, content + "\n")
                    else:
                        text_widget.insert(tk.END, "<< 빈 파일 >>\n")
            except Exception as e:
                text_widget.insert(tk.END, f"<< 파일 읽기 오류: {e} >>\n")

    except Exception as e:
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f"폴더 읽기 오류:\n{e}")

def select_folder_and_display():
    """
    폴더 선택 대화상자를 열고, 선택된 폴더의 파일들을 화면에 표시합니다.
    """
    global current_folder_path
    folder_path = filedialog.askdirectory(title="폴더 선택")
    if not folder_path:
        return

    current_folder_path = folder_path
    scan_and_display_files(folder_path)
    refresh_button.config(state=tk.NORMAL)  # 폴더가 선택되면 새로고침 버튼 활성화

def refresh_view():
    """
    현재 선택된 폴더의 내용을 새로고침합니다.
    """
    if current_folder_path:
        scan_and_display_files(current_folder_path)

# --- GUI 설정 ---
root = tk.Tk()
root.title("Python 파일 목록 및 뷰어")
root.geometry("1000x700")  # 창 크기 설정

# 버튼 프레임
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# "폴더 선택" 버튼
open_button = tk.Button(button_frame, text="폴더 선택", command=select_folder_and_display, 
                       font=("맑은 고딕", 10), padx=10, pady=5)
open_button.pack(side=tk.LEFT, padx=5)

# "새로고침" 버튼 (초기에는 비활성화)
refresh_button = tk.Button(button_frame, text="새로고침", command=refresh_view, 
                         font=("맑은 고딕", 10), padx=10, pady=5, state=tk.DISABLED)
refresh_button.pack(side=tk.LEFT, padx=5)

# 텍스트 위젯
text_widget = scrolledtext.ScrolledText(root, width=100, height=35, wrap=tk.WORD, 
                                       font=("Consolas", 9))
text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()