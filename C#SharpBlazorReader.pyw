import os
import re
import tkinter as tk
from tkinter import filedialog, font, BooleanVar, Checkbutton
import chardet
import hashlib

# -------------------- 전역 변수: 최근 열린 sln 경로 --------------------
last_sln_path = None

def detect_encoding(file_path):
    """파일 인코딩 자동 감지"""
    with open(file_path, 'rb') as f:
        rawdata = f.read(20000)
        result = chardet.detect(rawdata)
        return result['encoding'] or 'utf-8'

def is_identity_template_file(file_path, relative_path):
    """Identity 템플릿 파일인지 확인 (강화된 버전)"""
    
    # 1. Components\Account 폴더의 모든 파일 무조건 제외
    normalized_path = relative_path.replace('\\', '/')
    if re.match(r'.*Components[/\\]Account[/\\].*', normalized_path, re.IGNORECASE):
        return True
    
    # 2. Areas\Identity 폴더의 모든 파일
    if re.match(r'.*Areas[/\\]Identity[/\\].*', normalized_path, re.IGNORECASE):
        return True
    
    # 3. Identity 관련 파일명 패턴 (매우 강화)
    filename = os.path.basename(file_path).lower()
    identity_file_patterns = [
        r'.*identity.*',
        r'.*login.*',
        r'.*register.*',
        r'.*manage.*',
        r'.*account.*',
        r'.*authentication.*',
        r'.*authorize.*',
        r'.*external.*login.*',
        r'.*twofactor.*',
        r'.*recovery.*',
        r'.*confirmation.*',
        r'.*password.*',
        r'.*email.*sender.*',
        r'.*redirect.*manager.*',
        r'.*user.*accessor.*',
        r'.*accessdenied.*',
        r'.*confirmemail.*',
        r'.*lockout.*',
        r'.*personaldata.*',
        r'.*disable2fa.*',
        r'.*enableauthenticator.*',
        r'.*resetauthenticator.*',
        r'.*statusmessage.*',
        r'.*applicationuser.*',
        r'.*applicationdbcontext.*',
    ]
    
    for pattern in identity_file_patterns:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    
    return False

def is_template_file_modified(file_path, relative_path):
    """템플릿 파일이 수정되었는지 확인"""
    filename = os.path.basename(file_path).lower()
    
    # 기본 Blazor 템플릿 파일들의 원본 특징들
    template_signatures = {
        'counter.razor': [
            '@page "/counter"',
            'currentCount',
            'IncrementCount',
            'Click me'
        ],
        'weather.razor': [
            '@page "/weather"',
            'WeatherForecast',
            'Loading...',
            'forecasts'
        ],
        'fetchdata.razor': [
            '@page "/fetchdata"',
            'Weather forecast',
            'Loading...',
            'Date'
        ],
        'mainlayout.razor': [
            '@inherits LayoutView',
            'sidebar',
            'main'
        ],
        'navmenu.razor': [
            'navbar-toggler',
            'Home',
            'Counter',
            'Weather'
        ],
        'home.razor': [
            '@page "/"',
            'Hello, world!',
            'Welcome to your new app'
        ]
    }
    
    if filename in template_signatures:
        try:
            encoding = detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
                
            # 원본 템플릿의 특징적인 문자열들이 모두 있는지 확인
            signatures = template_signatures[filename]
            original_features = sum(1 for sig in signatures if sig in content)
            
            # 50% 이상의 원본 특징이 남아있으면 기본 템플릿으로 간주
            if original_features / len(signatures) >= 0.5:
                return False  # 수정되지 않은 기본 템플릿
            else:
                return True   # 수정된 템플릿
        except:
            return True  # 읽기 실패시 포함
    
    return True  # 템플릿이 아니거나 확인 불가시 포함

def is_important_config_file(file_path, relative_path):
    """중요한 설정 파일인지 확인"""
    filename = os.path.basename(file_path).lower()
    
    important_files = {
        'program.cs': True,           # 거의 항상 수정됨
        'startup.cs': True,           # 거의 항상 수정됨  
        'appsettings.json': True,     # 기본 설정 (중요)
        '_imports.razor': True,       # 전역 using 추가
        'app.razor': True,            # 앱 루트 컴포넌트
        '_host.cshtml': True,         # Blazor Server 호스트
        'routes.razor': True,         # 라우팅 설정
    }
    
    # Development, Production 등 환경별 설정은 제외
    if 'appsettings.' in filename and filename != 'appsettings.json':
        return False
        
    return important_files.get(filename, False)

def is_user_written_gtd_file(file_path, relative_path):
    """명백히 사용자가 작성한 GTD 관련 파일인지 확인"""
    filename = os.path.basename(file_path).lower()
    relative_lower = relative_path.lower()
    
    # GTD/Task 관련 명확한 키워드
    gtd_keywords = [
        'gtd', 'task', 'todo', 'project', 'board',
        'card', 'tree', 'dragdrop'
    ]
    
    for keyword in gtd_keywords:
        if keyword in filename or keyword in relative_lower:
            return True
    
    # 사용자 정의 서비스/모델/컨텍스트
    user_patterns = [
        r'.*service.*\.cs$',
        r'.*context.*\.cs$', 
        r'.*model.*\.cs$',
        r'.*dto.*\.cs$',
        r'.*entity.*\.cs$',
        r'.*repository.*\.cs$',
    ]
    
    for pattern in user_patterns:
        if re.match(pattern, filename, re.IGNORECASE):
            # Identity 관련이 아닌 경우만
            if not is_identity_template_file(file_path, relative_path):
                return True
    
    return False

def has_user_modifications(file_path, relative_path):
    """사용자 수정사항이 있는지 확인"""
    try:
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
            
        # 사용자 수정을 나타내는 지표들 (GTD 관련)
        user_modification_indicators = [
            # GTD 관련 키워드
            'TaskService', 'GTDService', 'TodoService', 'ProjectService',
            'TaskItem', 'Project', 'GTDContext', 'GTD',
            'TaskCard', 'TaskTree', 'GTDBoard',
            # 사용자 정의 서비스/의존성 주입 (Identity 제외)
            'AddScoped<Task', 'AddScoped<GTD', 'AddScoped<Todo',
            'AddSingleton<Task', 'AddSingleton<GTD', 'AddSingleton<Todo',
            'AddTransient<Task', 'AddTransient<GTD', 'AddTransient<Todo',
            # 데이터베이스 설정 (Identity 제외)
            'GTDContext', 'TaskContext', 'TodoContext',
            # 사용자 정의 CSS/JS
            'gtd.css', 'dragdrop.js', 'task.js', 'todo.js',
        ]
        
        content_lower = content.lower()
        for indicator in user_modification_indicators:
            if indicator.lower() in content_lower:
                return True
                
        return False
    except:
        return True  # 읽기 실패시 포함

def should_include_file(file_path, relative_path, valid_exts):
    """파일을 포함할지 결정하는 스마트 함수 (강화된 버전)"""
    filename = os.path.basename(file_path)
    filename_lower = filename.lower()
    _, ext = os.path.splitext(filename)
    
    # 1. 확장자 확인
    if ext.lower() not in valid_exts:
        return False
    
    # 2. Identity 템플릿 파일들은 무조건 제외 (강화된 필터)
    if is_identity_template_file(file_path, relative_path):
        return False
    
    # 3. 확실한 자동생성 파일들은 무조건 제외
    definite_auto_generated = [
        r'.*\.g\.cs$',
        r'.*\.designer\.cs$', 
        r'.*\.rz\.scp\.css$',
        r'.*\.deps\.json$',
        r'.*\.runtimeconfig\.json$',
        r'.*\.min\.js$',
        r'.*\.min\.css$',
        r'.*\.AssemblyInfo\.cs$',
        r'.*\.GlobalUsings\.g\.cs$',
        r'blazor\.boot\.json$',
    ]
    
    for pattern in definite_auto_generated:
        if re.match(pattern, filename, re.IGNORECASE):
            return False
    
    # 4. 확실한 제외 폴더들
    excluded_path_patterns = [
        r'.*[/\\]_framework[/\\].*',
        r'.*[/\\]lib[/\\].*',
        r'.*[/\\]Generated[/\\].*',
        r'.*[/\\]Migrations[/\\].*',
        r'.*[/\\]node_modules[/\\].*',
        r'.*[/\\]packages[/\\].*',
        r'.*[/\\]\.nuget[/\\].*',
    ]
    
    normalized_path = relative_path.replace('\\', '/')
    for pattern in excluded_path_patterns:
        if re.match(pattern, normalized_path, re.IGNORECASE):
            return False
    
    # 5. 중요한 설정 파일들은 항상 포함
    if is_important_config_file(file_path, relative_path):
        return True
    
    # 6. 명백히 사용자가 작성한 GTD 파일들
    if is_user_written_gtd_file(file_path, relative_path):
        return True
    
    # 7. 템플릿 파일이지만 수정된 경우 포함
    template_files = {
        'counter.razor', 'weather.razor', 'fetchdata.razor',
        'home.razor', 'privacy.razor', 'mainlayout.razor', 
        'navmenu.razor'
    }
    
    if filename_lower in template_files:
        # 수정된 템플릿인지 확인
        if is_template_file_modified(file_path, relative_path):
            return True
        else:
            return False  # 수정되지 않은 기본 템플릿은 제외
    
    # 8. 파일 내용에 GTD 관련 사용자 수정사항이 있는지 확인
    if has_user_modifications(file_path, relative_path):
        return True
    
    # 9. 기타 확실한 템플릿/자동생성 파일들은 제외
    common_template_files = {
        'weatherforecast.cs', 'weatherforecastservice.cs',
        'error.razor', '_layout.cshtml', '_viewstart.cshtml',
        '_viewimports.cshtml', 'auth.razor'
    }
    
    if filename_lower in common_template_files:
        return False
    
    # 10. 개발 환경 설정 파일들 제외
    if filename_lower.startswith('appsettings.') and filename_lower != 'appsettings.json':
        return False
    
    # 11. 나머지는 제외 (보수적 → 엄격한 접근으로 변경)
    return False

def open_sln_file(sln_path=None):
    """sln 파일 열기 및 결과 표시 (강화된 Identity 필터링 버전)"""
    global last_sln_path
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
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f".sln 파일을 읽는 중 오류가 발생했습니다: {e}")
        return
    
    pattern = r'Project\("{[^"]+}"\)\s*=\s*"[^"]+",\s*"([^"]+\.csproj)",\s*"{[^"]+}"'
    project_paths = re.findall(pattern, sln_text)
    
    text_widget.delete("1.0", tk.END)

    if not project_paths:
        text_widget.insert(tk.END, "솔루션 파일(.sln)에서 유효한 프로젝트(.csproj)를 찾지 못했습니다.")
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

    # 통계 변수
    total_files_found = 0
    excluded_files_count = 0
    identity_template_count = 0
    modified_template_count = 0
    user_written_count = 0
    config_count = 0

    for proj_relpath in project_paths:
        proj_fullpath = os.path.normpath(os.path.join(sln_dir, proj_relpath))
        project_folder = os.path.dirname(proj_fullpath)

        text_widget.insert(tk.END, f"===== Project: {os.path.basename(proj_relpath)} =====\n\n", "header")
        
        excluded_dirs = {
            "bin", "obj", ".vs", "Properties", 
            "_framework", "lib", "Generated", "Migrations",
            "node_modules", "packages", ".nuget"
        }
        
        files_to_show = []
        excluded_files = []
        
        try:
            for root, dirs, files in os.walk(project_folder):
                dirs[:] = [d for d in dirs if d.lower() not in {ed.lower() for ed in excluded_dirs}]
                
                for fname in files:
                    _, ext = os.path.splitext(fname)
                    if ext.lower() in valid_exts:
                        total_files_found += 1
                        full_path = os.path.join(root, fname)
                        relative_path = os.path.relpath(full_path, start=project_folder)
                        
                        # Identity 템플릿 파일 체크
                        if is_identity_template_file(full_path, relative_path):
                            identity_template_count += 1
                            excluded_files.append((relative_path, "🔐 Identity Template"))
                            continue
                        
                        if should_include_file(full_path, relative_path, valid_exts):
                            # 파일 분류
                            if is_important_config_file(full_path, relative_path):
                                config_count += 1
                                files_to_show.append((full_path, relative_path, "⚙️ Config"))
                            elif is_user_written_gtd_file(full_path, relative_path):
                                user_written_count += 1
                                files_to_show.append((full_path, relative_path, "🎯 GTD Code"))
                            else:
                                user_written_count += 1
                                files_to_show.append((full_path, relative_path, "📝 User Code"))
                        else:
                            excluded_files_count += 1
                            excluded_files.append((relative_path, "🚫 Excluded"))

        except Exception as e:
            text_widget.insert(tk.END, f"프로젝트 폴더를 읽는 중 오류 발생:\n{e}\n")
            continue

        # 📋 파일 목록 먼저 표시
        text_widget.insert(tk.END, f"🎯 핵심 파일 목록 ({len(files_to_show)}개):\n", "header")
        text_widget.insert(tk.END, "="*80 + "\n")
        
        files_to_show.sort(key=lambda x: x[1])
        for i, (fpath, relative_path, file_type) in enumerate(files_to_show, 1):
            text_widget.insert(tk.END, f"{i:2d}. {file_type} {relative_path}\n", "filepath")
        
        text_widget.insert(tk.END, "\n")
        
        # 🚫 제외된 파일 목록도 표시 (처음 15개)
        if excluded_files:
            text_widget.insert(tk.END, f"🚫 제외된 파일 목록 (처음 15개, 총 {len(excluded_files)}개):\n", "info")
            text_widget.insert(tk.END, "-"*80 + "\n")
            for i, (relative_path, status) in enumerate(excluded_files[:15], 1):
                text_widget.insert(tk.END, f"{i:2d}. {status} {relative_path}\n", "info")
            if len(excluded_files) > 15:
                text_widget.insert(tk.END, f"... 그 외 {len(excluded_files)-15}개 더\n", "info")
            text_widget.insert(tk.END, "\n")

        # 📊 통계
        text_widget.insert(tk.END, f"📊 파일 분석 결과:\n", "info")
        gtd_files = len([f for f in files_to_show if f[2] == "🎯 GTD Code"])
        other_user_files = len([f for f in files_to_show if f[2] == "📝 User Code"])
        text_widget.insert(tk.END, f"  🎯 GTD 핵심 코드: {gtd_files}개\n", "success")
        text_widget.insert(tk.END, f"  📝 기타 사용자 코드: {other_user_files}개\n", "success")
        text_widget.insert(tk.END, f"  ⚙️ 설정 파일: {config_count}개\n", "info")
        text_widget.insert(tk.END, f"  🔐 Identity 템플릿: {identity_template_count}개\n", "warning")
        text_widget.insert(tk.END, f"  🚫 기타 제외: {excluded_files_count}개\n\n", "info")

        if not files_to_show:
            text_widget.insert(tk.END, f"📝 표시할 파일이 없습니다: {project_folder}\n")
            continue

        # 📄 파일 내용 표시
        text_widget.insert(tk.END, f"📄 파일 내용:\n", "header")
        text_widget.insert(tk.END, "="*80 + "\n\n")

        for fpath, relative_path, file_type in files_to_show:
            text_widget.insert(tk.END, "\n" + "="*80 + "\n")
            text_widget.insert(tk.END, f"{file_type} File: {relative_path}\n", "filepath")
            text_widget.insert(tk.END, "="*80 + "\n")
            try:
                encoding = detect_encoding(fpath)
                with open(fpath, "r", encoding=encoding, errors="replace") as f:
                    content = f.read()
                text_widget.insert(tk.END, content + "\n")
            except Exception as e:
                text_widget.insert(tk.END, f"<< 파일 읽기 오류: {e} >>\n")

    # 전체 통계
    text_widget.insert(tk.END, f"\n\n=== 📊 최종 분석 결과 ===\n", "header")
    text_widget.insert(tk.END, f"🔍 총 스캔된 파일: {total_files_found}개\n", "info")
    text_widget.insert(tk.END, f"🎯 실제 포함된 파일: {user_written_count + config_count}개\n", "success")
    text_widget.insert(tk.END, f"🔐 Identity 템플릿: {identity_template_count}개\n", "warning")
    text_widget.insert(tk.END, f"🚫 기타 제외: {excluded_files_count}개\n", "info")

def refresh_sln():
    """새로고침 기능"""
    if last_sln_path:
        open_sln_file(last_sln_path)
    else:
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, "먼저 .sln 파일을 열어주세요.")

# GUI 구성
root = tk.Tk()
root.title("🎯 Ultra-Filtered GTD Code Viewer - Only Essential Files!")
root.geometry("1400x1000")

default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Malgun Gothic", size=10)
text_font = ("D2Coding", 10, "normal") if "D2Coding" in font.families() else ("Consolas", 10)

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=5, pady=5)

open_button = tk.Button(top_frame, text="📂 Open .sln file", command=open_sln_file, font=("Malgun Gothic", 10, "bold"))
open_button.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(top_frame, text="🔄 새로고침", command=refresh_sln, font=("Malgun Gothic", 10))
refresh_button.pack(side=tk.LEFT, padx=5)

separator = tk.Label(top_frame, text="|", font=("Malgun Gothic", 10))
separator.pack(side=tk.LEFT, padx=10)

include_csharp_razor_var = BooleanVar(value=True)
Checkbutton(top_frame, text="📄 C# & Razor (.cs, .razor)", variable=include_csharp_razor_var, font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_web_var = BooleanVar(value=True)
Checkbutton(top_frame, text="🌐 Web (.html, .css, .js)", variable=include_web_var, font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_config_var = BooleanVar(value=True)
Checkbutton(top_frame, text="⚙️ Config (.json, .webmanifest)", variable=include_config_var, font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_csproj_var = BooleanVar(value=False)
Checkbutton(top_frame, text="📦 .csproj", variable=include_csproj_var, font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

include_xml_var = BooleanVar(value=False)
Checkbutton(top_frame, text="📋 .xml", variable=include_xml_var, font=("Malgun Gothic", 9)).pack(side=tk.LEFT, padx=5)

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
text_widget.tag_configure("success", font=(text_font[0], 10, "bold"), foreground="green")
text_widget.tag_configure("warning", font=(text_font[0], 10, "bold"), foreground="orange")

root.mainloop()