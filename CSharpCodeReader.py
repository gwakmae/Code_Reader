import os
import re
import tkinter as tk
from tkinter import filedialog, font, BooleanVar, Checkbutton
import chardet

# -------------------- 전역 변수: 최근 열린 sln 경로 --------------------
last_sln_path = None  # 새로고침용

def detect_encoding(file_path):
    """파일 인코딩 자동 감지 (정확도 향상)"""
    with open(file_path, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        return result['encoding'] or 'utf-8'  # 기본값 설정

def open_sln_file(sln_path=None):
    """sln 파일 열기 및 결과 표시 (sln_path 인자 추가)"""
    global last_sln_path
    if sln_path is None:
        sln_path = filedialog.askopenfilename(
            title="Select .sln file",
            filetypes=[("Solution Files", "*.sln"), ("All Files", "*.*")]
        )
    if not sln_path:
        return

    last_sln_path = sln_path  # 최근 sln 경로 저장

    # 1) .sln 파일이 위치한 폴더
    sln_dir = os.path.dirname(sln_path)
    
    # 2) .sln 파일 내용에서 'Project(...) = "이름", "상대경로\프로젝트.csproj", "{GUID}"'를 정규식으로 찾아본다.
    with open(sln_path, "r", encoding="utf-8", errors="replace") as f:
        sln_text = f.read()
    
    # 정규식: Project("...GUID...") = "프로젝트명", "상대경로\xxx.csproj", "{...GUID...}"
    pattern = r'Project\("(?P<proj_type_guid>[^"]+)"\)\s*=\s*"(?P<proj_name>[^"]+)"\s*,\s*"(?P<proj_relpath>[^"]+\.csproj)"\s*,\s*"{(?P<proj_guid>[^}]+)}"'
    match = re.search(pattern, sln_text)
    
    text_widget.delete("1.0", tk.END)  # 항상 먼저 비움

    if not match:
        text_widget.insert(tk.END, "No valid project found in the .sln file.")
        return

    # 3) 상대경로(프로젝트 폴더 + csproj)에서 프로젝트 폴더만 추출
    proj_relpath = match.group("proj_relpath")
    proj_fullpath = os.path.join(sln_dir, proj_relpath)
    proj_fullpath = os.path.normpath(proj_fullpath)
    
    # 최종 폴더만 얻기
    project_folder = os.path.dirname(proj_fullpath)  # 예: "C:\\...\\ProgramManager"

    # 4) 해당 프로젝트 폴더에서 **하위 폴더 포함** → os.walk() 사용
    valid_exts = {".cs", ".xaml"}
    if include_csproj_var.get():
        valid_exts.add(".csproj")
    if include_xml_var.get():
        valid_exts.add(".xml")
    
    excluded_dirs = {"bin", "obj", "Properties"}
    files_to_show = []
    
    try:
        for root, dirs, files in os.walk(project_folder):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for fname in files:
                _, ext = os.path.splitext(fname)
                if ext.lower() in valid_exts:
                    full_path = os.path.join(root, fname)
                    files_to_show.append(full_path)
    except Exception as e:
        text_widget.insert(tk.END, f"Error reading project folder:\n{e}")
        return

    if not files_to_show:
        text_widget.insert(tk.END, f"No valid files found in: {project_folder}")
        return

    for fpath in files_to_show:
        text_widget.insert(tk.END, "\n" + "="*60 + "\n")
        text_widget.insert(tk.END, f"File: {fpath}\n")
        text_widget.insert(tk.END, "="*60 + "\n")
        try:
            encoding = detect_encoding(fpath)
            with open(fpath, "r", encoding=encoding, errors="replace") as f:
                content = f.read()
            text_widget.insert(tk.END, content + "\n")
        except Exception as e:
            text_widget.insert(tk.END, f"<< 파일 읽기 오류: {e} >>\n")

# -------------------- 새로고침 기능 --------------------
def refresh_sln():
    if last_sln_path:
        open_sln_file(last_sln_path)
    else:
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, "아직 .sln 파일을 열지 않았습니다.")

# -------------------- GUI 구성 (폰트 설정 추가) --------------------
root = tk.Tk()
root.title("C# Project Viewer")

# 한국어 지원 폰트 설정 (Windows 기준 'Malgun Gothic')
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Malgun Gothic", size=10)

# 상단 프레임 (버튼과 체크박스 포함)
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=5, pady=5)

# .sln 파일 열기 버튼
open_button = tk.Button(top_frame, text="Open .sln file", command=open_sln_file)
open_button.pack(side=tk.LEFT, padx=5)

# -------------------- 새로고침 버튼 추가 --------------------
refresh_button = tk.Button(top_frame, text="새로고침", command=refresh_sln)
refresh_button.pack(side=tk.LEFT, padx=5)

# .csproj 파일 포함 여부 체크박스
include_csproj_var = BooleanVar(value=False)
include_csproj_check = Checkbutton(
    top_frame, 
    text=".csproj 파일 포함", 
    variable=include_csproj_var,
    onvalue=True, 
    offvalue=False
)
include_csproj_check.pack(side=tk.LEFT, padx=10)

# .xml 파일 포함 여부 체크박스
include_xml_var = BooleanVar(value=True)  # 기본값은 포함
include_xml_check = Checkbutton(
    top_frame, 
    text=".xml 파일 포함", 
    variable=include_xml_var,
    onvalue=True, 
    offvalue=False
)
include_xml_check.pack(side=tk.LEFT, padx=10)

# 텍스트 위젯과 스크롤바
text_widget = tk.Text(root, wrap=tk.NONE, font=("Malgun Gothic", 9))
text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

scroll_y = tk.Scrollbar(root, orient=tk.VERTICAL, command=text_widget.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

text_widget.configure(yscrollcommand=scroll_y.set)

root.mainloop()
