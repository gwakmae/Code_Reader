import os
import re
import tkinter as tk
from tkinter import filedialog, font, BooleanVar, Checkbutton, messagebox
from tkinter import ttk
import chardet
import json
import hashlib

# -------------------- 전역 변수 --------------------
last_sln_path = None
selection_cache = {}  # 선택 캐시 저장소
current_files = []    # 현재 프로젝트의 모든 파일 목록

def detect_encoding(file_path):
    """파일 인코딩 자동 감지"""
    with open(file_path, 'rb') as f:
        rawdata = f.read(20000)
        result = chardet.detect(rawdata)
        return result['encoding'] or 'utf-8'

def get_project_hash(sln_path):
    """프로젝트 고유 해시 생성 (선택 저장용)"""
    return hashlib.md5(sln_path.encode()).hexdigest()[:8]

def save_selection_cache():
    """선택 캐시를 파일로 저장"""
    try:
        cache_file = os.path.join(os.path.dirname(__file__), 'gtd_selection_cache.json')
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(selection_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"선택 캐시 저장 실패: {e}")

def load_selection_cache():
    """선택 캐시를 파일에서 로드"""
    global selection_cache
    try:
        cache_file = os.path.join(os.path.dirname(__file__), 'gtd_selection_cache.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                selection_cache = json.load(f)
    except Exception as e:
        print(f"선택 캐시 로드 실패: {e}")
        selection_cache = {}

def classify_file_basic(file_path, relative_path):
    """기본적인 파일 분류 (자동생성/제외 파일만 걸러냄)"""
    filename = os.path.basename(file_path).lower()
    
    # 확실히 제외할 파일들
    auto_generated_patterns = [
        r'.*\.g\.cs$',                    # Razor 생성 파일
        r'.*\.designer\.cs$',             # 디자이너 파일
        r'.*\.rz\.scp\.css$',           # Razor CSS 생성 파일
        r'.*\.deps\.json$',               # 의존성 파일
        r'.*\.runtimeconfig\.json$',      # 런타임 설정
        r'.*\.min\.js$',                  # 압축된 JS
        r'.*\.min\.css$',                 # 압축된 CSS
        r'.*\.AssemblyInfo\.cs$',         # 어셈블리 정보
        r'.*\.GlobalUsings\.g\.cs$',     # 전역 using 생성
        r'blazor\.boot\.json$',           # Blazor 부트 파일
    ]
    
    for pattern in auto_generated_patterns:
        if re.match(pattern, filename, re.IGNORECASE):
            return "AUTO_GENERATED"
    
    # 제외할 폴더
    excluded_path_patterns = [
        r'.*[/\\]bin[/\\].*',
        r'.*[/\\]obj[/\\].*',
        r'.*[/\\]_framework[/\\].*',
        r'.*[/\\]Generated[/\\].*',
        r'.*[/\\]node_modules[/\\].*',
        r'.*[/\\]packages[/\\].*',
        r'.*[/\\]\.nuget[/\\].*',
        r'.*[/\\]\.vs[/\\].*',
    ]
    
    normalized_path = relative_path.replace('\\', '/')
    for pattern in excluded_path_patterns:
        if re.match(pattern, normalized_path, re.IGNORECASE):
            return "EXCLUDED_FOLDER"
    
    return "SELECTABLE"

def open_sln_file(sln_path=None):
    """sln 파일 열기 및 파일 목록 생성"""
    global last_sln_path, current_files
    
    if sln_path is None:
        sln_path = filedialog.askopenfilename(
            title="Select .sln file",
            filetypes=[("Solution Files", "*.sln"), ("All Files", "*.*")]
        )
    if not sln_path:
        return

    last_sln_path = sln_path
    sln_dir = os.path.dirname(sln_path)
    
    try:
        with open(sln_path, "r", encoding="utf-8", errors="replace") as f:
            sln_text = f.read()
    except Exception as e:
        messagebox.showerror("오류", f".sln 파일을 읽는 중 오류가 발생했습니다: {e}")
        return
    
    pattern = r'Project\("{[^"]+}"\)\s*=\s*"[^"]+",\s*"([^"]+\.csproj)",\s*"{[^"]+}"'
    project_paths = re.findall(pattern, sln_text)
    
    if not project_paths:
        messagebox.showwarning("경고", "솔루션 파일(.sln)에서 유효한 프로젝트(.csproj)를 찾지 못했습니다.")
        return

    # 읽어올 파일 확장자 설정
    valid_exts = set()
    if include_csharp_razor_var.get():
        valid_exts.update({".cs", ".razor"})
    if include_web_var.get():
        valid_exts.update({".html", ".css", ".js"})
    if include_config_var.get():
        valid_exts.update({".json", ".webmanifest"})
    if include_csproj_var.get():
        valid_exts.add(".csproj")
    if include_xml_var.get():
        valid_exts.add(".xml")

    current_files = []
    
    for proj_relpath in project_paths:
        proj_fullpath = os.path.normpath(os.path.join(sln_dir, proj_relpath))
        project_folder = os.path.dirname(proj_fullpath)
        project_name = os.path.basename(proj_relpath)
        
        try:
            for root, dirs, files in os.walk(project_folder):
                # 기본 제외 디렉토리만 제외
                basic_excluded_dirs = {"bin", "obj", ".vs"}
                dirs[:] = [d for d in dirs if d.lower() not in {ed.lower() for ed in basic_excluded_dirs}]
                
                for fname in files:
                    _, ext = os.path.splitext(fname)
                    if ext.lower() in valid_exts:
                        full_path = os.path.join(root, fname)
                        relative_path = os.path.relpath(full_path, start=project_folder)
                        
                        classification = classify_file_basic(full_path, relative_path)
                        
                        if classification == "SELECTABLE":
                            current_files.append({
                                'full_path': full_path,
                                'relative_path': relative_path,
                                'project_name': project_name,
                                'file_name': fname,
                                'ext': ext.lower(),
                                'folder': os.path.dirname(relative_path) if os.path.dirname(relative_path) else "Root"
                            })

        except Exception as e:
            messagebox.showerror("오류", f"프로젝트 폴더를 읽는 중 오류 발생:\n{e}")
            continue

    # 파일 선택 창 열기
    if current_files:
        open_file_selector()
    else:
        messagebox.showinfo("정보", "선택 가능한 파일이 없습니다.")

def open_file_selector():
    """파일 선택 창 열기"""
    global current_files, selection_cache, last_sln_path
    
    # 새 창 생성
    selector_window = tk.Toplevel(root)
    selector_window.title("📁 파일 선택 - VSCode 스타일")
    selector_window.geometry("1200x800")
    
    # 프로젝트 해시 (선택 저장용)
    project_hash = get_project_hash(last_sln_path)
    saved_selections = selection_cache.get(project_hash, [])
    
    # 상단 정보
    info_frame = tk.Frame(selector_window)
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(info_frame, text=f"📂 프로젝트: {os.path.basename(last_sln_path)}", 
             font=("Malgun Gothic", 12, "bold")).pack(side=tk.LEFT)
    tk.Label(info_frame, text=f"총 {len(current_files)}개 파일", 
             font=("Malgun Gothic", 10)).pack(side=tk.RIGHT)
    
    # 트리뷰 생성 (VSCode 탐색기 스타일)
    tree_frame = tk.Frame(selector_window)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # 트리뷰 설정
    tree = ttk.Treeview(tree_frame, columns=("type", "size"), show="tree headings", selectmode="extended")
    tree.heading("#0", text="📁 파일/폴더", anchor="w")
    tree.heading("type", text="유형", anchor="center")
    tree.heading("size", text="확장자", anchor="center")
    
    tree.column("#0", width=600, minwidth=300)
    tree.column("type", width=150, minwidth=100)
    tree.column("size", width=100, minwidth=80)
    
    # 스크롤바
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    
    tree.pack(side="left", fill="both", expand=True)
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x.pack(side="bottom", fill="x")
    
    # 파일을 폴더별로 그룹화
    folder_groups = {}
    for file_info in current_files:
        folder = file_info['folder']
        if folder not in folder_groups:
            folder_groups[folder] = []
        folder_groups[folder].append(file_info)
    
    # 트리에 항목 추가
    folder_nodes = {}
    file_items = {}  # 파일 경로 -> tree item ID 매핑
    
    for folder, files in sorted(folder_groups.items()):
        # 폴더 노드 생성
        if folder == "Root":
            folder_id = tree.insert("", "end", text="📁 Root", values=("폴더", ""), open=True)
        else:
            folder_id = tree.insert("", "end", text=f"📁 {folder}", values=("폴더", ""), open=True)
        folder_nodes[folder] = folder_id
        
        # 파일 노드 생성
        for file_info in sorted(files, key=lambda x: x['file_name'].lower()):
            file_type = get_file_type_icon(file_info['ext'])
            file_id = tree.insert(folder_id, "end", 
                                text=f"{file_type} {file_info['file_name']}", 
                                values=(get_file_type_name(file_info['ext']), file_info['ext']))
            file_items[file_info['relative_path']] = file_id
    
    # 저장된 선택 복원
    for saved_path in saved_selections:
        if saved_path in file_items:
            tree.selection_add(file_items[saved_path])
    
    # 버튼 프레임
    button_frame = tk.Frame(selector_window)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # 선택 통계 라벨
    selection_label = tk.Label(button_frame, text="선택된 파일: 0개", font=("Malgun Gothic", 10))
    selection_label.pack(side=tk.LEFT)
    
    def update_selection_count():
        """선택 개수 업데이트"""
        selected_count = len([item for item in tree.selection() if tree.parent(item) != ""])
        selection_label.config(text=f"선택된 파일: {selected_count}개")
    
    tree.bind("<<TreeviewSelect>>", lambda e: update_selection_count())
    
    # 빠른 선택 버튼들
    quick_frame = tk.Frame(button_frame)
    quick_frame.pack(side=tk.LEFT, padx=20)
    
    def select_by_pattern(pattern_func, name):
        """패턴으로 선택"""
        tree.selection_remove(tree.selection())
        for file_info in current_files:
            if pattern_func(file_info):
                if file_info['relative_path'] in file_items:
                    tree.selection_add(file_items[file_info['relative_path']])
        update_selection_count()
        messagebox.showinfo("선택 완료", f"{name} 파일들이 선택되었습니다.")
    
    tk.Button(quick_frame, text="🎯 GTD 관련", 
              command=lambda: select_by_pattern(
                  lambda f: any(keyword in f['relative_path'].lower() or keyword in f['file_name'].lower() 
                              for keyword in ['gtd', 'task', 'todo', 'project', 'board', 'card', 'kanban']), 
                  "GTD 관련")).pack(side=tk.LEFT, padx=2)
    
    tk.Button(quick_frame, text="⚙️ 설정파일", 
              command=lambda: select_by_pattern(
                  lambda f: f['file_name'].lower() in ['program.cs', 'startup.cs', 'appsettings.json', '_imports.razor', 'app.razor'], 
                  "설정")).pack(side=tk.LEFT, padx=2)
    
    tk.Button(quick_frame, text="🧩 컴포넌트", 
              command=lambda: select_by_pattern(
                  lambda f: f['ext'] == '.razor' and 'component' in f['relative_path'].lower(), 
                  "컴포넌트")).pack(side=tk.LEFT, padx=2)
    
    tk.Button(quick_frame, text="🔧 서비스", 
              command=lambda: select_by_pattern(
                  lambda f: 'service' in f['file_name'].lower() and f['ext'] == '.cs', 
                  "서비스")).pack(side=tk.LEFT, padx=2)
    
    # 주요 버튼들
    main_button_frame = tk.Frame(button_frame)
    main_button_frame.pack(side=tk.RIGHT)
    
    def select_all_files():
        """모든 파일 선택"""
        for file_info in current_files:
            if file_info['relative_path'] in file_items:
                tree.selection_add(file_items[file_info['relative_path']])
        update_selection_count()
    
    def clear_selection():
        """선택 해제"""
        tree.selection_remove(tree.selection())
        update_selection_count()
    
    def apply_selection():
        """선택 적용 및 내용 표시"""
        selected_items = tree.selection()
        selected_files = []
        
        for item in selected_items:
            # 파일 항목만 (폴더 제외)
            if tree.parent(item) != "":
                item_text = tree.item(item, "text")
                # 아이콘 제거하고 파일명만 추출
                file_name = item_text.split(" ", 1)[1] if " " in item_text else item_text
                
                # 해당 파일 정보 찾기
                for file_info in current_files:
                    if file_info['file_name'] == file_name:
                        # 상대 경로로 중복 확인
                        parent_item = tree.parent(item)
                        parent_text = tree.item(parent_item, "text")
                        folder_name = parent_text.replace("📁 ", "")
                        
                        if (folder_name == "Root" and file_info['folder'] == "Root") or \
                           (folder_name == file_info['folder']):
                            selected_files.append(file_info)
                            break
        
        if not selected_files:
            messagebox.showwarning("경고", "선택된 파일이 없습니다.")
            return
        
        # 선택 저장
        selection_cache[project_hash] = [f['relative_path'] for f in selected_files]
        save_selection_cache()
        
        # 내용 표시
        display_selected_files(selected_files)
        selector_window.destroy()
    
    tk.Button(main_button_frame, text="✅ 모두 선택", command=select_all_files, 
              font=("Malgun Gothic", 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(main_button_frame, text="❌ 선택 해제", command=clear_selection, 
              font=("Malgun Gothic", 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(main_button_frame, text="🚀 적용하기", command=apply_selection, 
              font=("Malgun Gothic", 10, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
    
    update_selection_count()

def get_file_type_icon(ext):
    """파일 확장자별 아이콘"""
    icons = {
        '.cs': '🔷',
        '.razor': '⚡',
        '.html': '🌐',
        '.css': '🎨',
        '.js': '💛',
        '.json': '📋',
        '.xml': '📄',
        '.csproj': '📦'
    }
    return icons.get(ext, '📄')

def get_file_type_name(ext):
    """파일 확장자별 타입명"""
    types = {
        '.cs': 'C# 코드',
        '.razor': 'Razor 페이지',
        '.html': 'HTML',
        '.css': 'CSS',
        '.js': 'JavaScript',
        '.json': 'JSON 설정',
        '.xml': 'XML',
        '.csproj': '프로젝트 파일'
    }
    return types.get(ext, '기타')

def display_selected_files(selected_files):
    """선택된 파일들의 내용을 표시"""
    text_widget.delete("1.0", tk.END)
    
    if not selected_files:
        text_widget.insert(tk.END, "선택된 파일이 없습니다.")
        return
    
    # 헤더 정보
    text_widget.insert(tk.END, f"🎯 선택된 파일 ({len(selected_files)}개)\n", "header")
    text_widget.insert(tk.END, f"📂 프로젝트: {os.path.basename(last_sln_path)}\n", "info")
    text_widget.insert(tk.END, "="*100 + "\n\n")
    
    # 파일 목록
    text_widget.insert(tk.END, "📋 선택된 파일 목록:\n", "header")
    for i, file_info in enumerate(selected_files, 1):
        icon = get_file_type_icon(file_info['ext'])
        text_widget.insert(tk.END, f"{i:2d}. {icon} {file_info['relative_path']}\n", "filepath")
    
    text_widget.insert(tk.END, "\n" + "="*100 + "\n\n")
    
    # 파일 내용 표시
    text_widget.insert(tk.END, "📄 파일 내용:\n", "header")
    text_widget.insert(tk.END, "="*100 + "\n\n")
    
    for file_info in selected_files:
        text_widget.insert(tk.END, "\n" + "="*100 + "\n")
        icon = get_file_type_icon(file_info['ext'])
        text_widget.insert(tk.END, f"{icon} File: {file_info['relative_path']}\n", "filepath")
        text_widget.insert(tk.END, "="*100 + "\n")
        
        try:
            encoding = detect_encoding(file_info['full_path'])
            with open(file_info['full_path'], "r", encoding=encoding, errors="replace") as f:
                content = f.read()
            text_widget.insert(tk.END, content + "\n")
        except Exception as e:
            text_widget.insert(tk.END, f"<< 파일 읽기 오류: {e} >>\n")

def refresh_sln():
    """새로고침 기능"""
    if last_sln_path:
        open_sln_file(last_sln_path)
    else:
        messagebox.showinfo("정보", "먼저 .sln 파일을 열어주세요.")

# 캐시 로드
load_selection_cache()

# GUI 구성
root = tk.Tk()
root.title("🎯 GTD Code Viewer - Manual Selection")
root.geometry("1400x1000")

default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Malgun Gothic", size=10)
text_font = ("D2Coding", 10, "normal") if "D2Coding" in font.families() else ("Consolas", 10)

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=5, pady=5)

open_button = tk.Button(top_frame, text="📂 Open .sln file", command=open_sln_file, 
                       font=("Malgun Gothic", 10, "bold"), bg="#2196F3", fg="white")
open_button.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(top_frame, text="🔄 새로고침", command=refresh_sln, font=("Malgun Gothic", 10))
refresh_button.pack(side=tk.LEFT, padx=5)

separator = tk.Label(top_frame, text="|", font=("Malgun Gothic", 10))
separator.pack(side=tk.LEFT, padx=10)

include_csharp_razor_var = BooleanVar(value=True)
Checkbutton(top_frame, text="📄 C# & Razor (.cs, .razor)", variable=include_csharp_razor_var, 
           font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_web_var = BooleanVar(value=True)
Checkbutton(top_frame, text="🌐 Web (.html, .css, .js)", variable=include_web_var, 
           font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_config_var = BooleanVar(value=True)
Checkbutton(top_frame, text="⚙️ Config (.json, .webmanifest)", variable=include_config_var, 
           font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_csproj_var = BooleanVar(value=False)
Checkbutton(top_frame, text="📦 .csproj", variable=include_csproj_var, 
           font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_xml_var = BooleanVar(value=False)
Checkbutton(top_frame, text="📋 .xml", variable=include_xml_var, 
           font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True)

text_widget = tk.Text(text_frame, wrap=tk.NONE, font=text_font, undo=True)
text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

scroll_y = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=text_widget.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

text_widget.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

text_widget.tag_configure("header", font=(text_font[0], 12, "bold"), foreground="blue")
text_widget.tag_configure("filepath", font=(text_font[0], 10, "bold"), foreground="darkgreen")
text_widget.tag_configure("info", font=(text_font[0], 9, "normal"), foreground="gray")

root.mainloop()