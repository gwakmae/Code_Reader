import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox # messagebox 추가
import chardet

# 마지막으로 선택한 폴더 경로를 저장할 전역 변수
last_selected_folder = None

def detect_encoding(file_path):
    """파일 인코딩 자동 감지 (정확도 향상)"""
    try:
        with open(file_path, 'rb') as f:
            rawdata = f.read(1024 * 5) # 첫 5KB 정도만 읽어서 성능 향상 시도
            # 파일 크기가 작으면 전체를 읽음
            if len(rawdata) < 1024 * 5:
                f.seek(0)
                rawdata = f.read()
            result = chardet.detect(rawdata)
            # 신뢰도가 너무 낮으면 utf-8 시도
            encoding = result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
            # None이 반환될 경우 utf-8 사용
            return encoding or 'utf-8'
    except Exception:
        # 파일 읽기 실패 시 기본값 반환
        return 'utf-8'

def display_files_from_folder(folder_path):
    """
    주어진 폴더 경로와 모든 하위 폴더 내의 .mq5 및 .mqh 파일 목록과 내용을 표시합니다.
    (폴더 제외 규칙 없음)
    """
    global text_widget # 전역 text_widget 사용 명시

    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showerror("오류", "유효한 폴더 경로가 아닙니다.")
        return

    text_widget.config(state=tk.NORMAL) # 편집 가능하게 설정
    text_widget.delete("1.0", tk.END)  # 이전 내용 지우기
    mql_files = [] # 찾은 MQL 파일(.mq5, .mqh) 경로를 저장할 리스트

    try:
        # os.walk를 사용하여 선택된 폴더 및 모든 하위 폴더 탐색
        for root_dir, dirs, files in os.walk(folder_path):
            # 현재 폴더(root_dir) 내의 파일들을 순회
            for file in files:
                # 파일 확장자가 .mq5 또는 .mqh 인 경우만 처리
                if file.endswith(".mq5") or file.endswith(".mqh"):
                    full_path = os.path.join(root_dir, file) # 파일의 전체 경로 생성
                    mql_files.append(full_path) # 리스트에 추가

        # 찾은 파일의 총 개수 표시
        text_widget.insert(tk.END, f"폴더: {folder_path}\n")
        text_widget.insert(tk.END, f"총 {len(mql_files)}개의 MQ5/MQH 파일을 찾았습니다.\n\n")

        # 찾은 각 파일의 내용 표시
        for full_path in mql_files:
            # --- 파일 이름과 구분선 표시 ---
            text_widget.insert(tk.END, "\n" + "=" * 60 + "\n")
            # 상대 경로 표시 (옵션) - 폴더 경로 부분을 제외하고 표시
            relative_path = os.path.relpath(full_path, folder_path)
            text_widget.insert(tk.END, f"파일: {relative_path}\n")
            text_widget.insert(tk.END, "=" * 60 + "\n")

            # --- 파일 내용 읽기 및 표시 ---
            try:
                # 파일 인코딩 감지
                encoding = detect_encoding(full_path)
                # 감지된 인코딩으로 파일 열기, 읽기 오류 시 대체 문자로 처리 ('replace')
                with open(full_path, "r", encoding=encoding, errors='replace') as f:
                    content = f.read()
                # 파일 내용을 텍스트 위젯에 추가
                text_widget.insert(tk.END, content + "\n")
            except Exception as e:
                # 파일 읽기 중 오류 발생 시 오류 메시지 표시
                text_widget.insert(tk.END, f"<< 파일 읽기 오류 ({full_path}): {e} >>\n")

    except Exception as e:
        # 폴더 읽기 중 오류 발생 시 오류 메시지 표시
        text_widget.insert(tk.END, f"폴더 읽기 오류 ({folder_path}):\n{e}")
    finally:
        # 작업 완료 후 텍스트 위젯을 읽기 전용으로 설정 (선택 사항)
        text_widget.config(state=tk.DISABLED)


def list_and_display_mql_files():
    """
    사용자에게 폴더 선택을 요청하고, 선택된 폴더의 MQL 파일 내용을 표시합니다.
    """
    global last_selected_folder # 전역 변수 사용 명시

    folder_path = filedialog.askdirectory(title="MQL 파일이 있는 폴더 선택")
    if not folder_path:
        # 사용자가 폴더 선택을 취소한 경우
        if last_selected_folder is None: # 이전에 선택한 폴더도 없으면
             text_widget.config(state=tk.NORMAL)
             text_widget.delete("1.0", tk.END)
             text_widget.insert(tk.END, "폴더를 선택해주세요.")
             text_widget.config(state=tk.DISABLED)
        return # 함수 종료

    # 새 폴더가 선택되었으므로 전역 변수 업데이트
    last_selected_folder = folder_path
    # 선택된 폴더의 내용을 표시하는 함수 호출
    display_files_from_folder(last_selected_folder)
    # 새로고침 버튼 활성화 (폴더가 한 번이라도 선택되면)
    refresh_button.config(state=tk.NORMAL)

def refresh_display():
    """
    마지막으로 선택했던 폴더의 내용을 다시 로드하여 표시합니다.
    """
    global last_selected_folder # 전역 변수 사용 명시

    if last_selected_folder:
        print(f"새로고침: {last_selected_folder}") # 콘솔에 로그 출력 (디버깅용)
        display_files_from_folder(last_selected_folder)
    else:
        # 아직 폴더가 선택된 적이 없으면 메시지 표시
        messagebox.showinfo("정보", "먼저 '폴더 선택' 버튼을 사용하여 폴더를 지정해주세요.")

# --- GUI 설정 ---
root = tk.Tk()
root.title("MQ5/MQH 파일 리스터 및 뷰어 (새로고침 기능)") # 창 제목 변경
root.geometry("800x600") # 창 기본 크기 설정

# --- 버튼 프레임 ---
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# 폴더 선택 버튼 생성 및 배치
open_button = tk.Button(button_frame, text="폴더 선택", command=list_and_display_mql_files, width=15)
open_button.pack(side=tk.LEFT, padx=5)

# 새로고침 버튼 생성 및 배치 (초기에는 비활성화)
refresh_button = tk.Button(button_frame, text="새로고침", command=refresh_display, width=15, state=tk.DISABLED)
refresh_button.pack(side=tk.LEFT, padx=5)

# 스크롤 가능한 텍스트 위젯 생성 및 배치 (크기 조정)
text_widget = scrolledtext.ScrolledText(root, width=100, height=30, wrap=tk.WORD, state=tk.DISABLED) # 초기 상태 비활성화
text_widget.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True) # 창 크기 변경에 따라 위젯 크기도 조절되도록 설정

# 초기 안내 메시지
text_widget.config(state=tk.NORMAL)
text_widget.insert(tk.END, "먼저 '폴더 선택' 버튼을 눌러 MQL 파일이 있는 폴더를 지정해주세요.")
text_widget.config(state=tk.DISABLED)


# GUI 이벤트 루프 시작
root.mainloop()