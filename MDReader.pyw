import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import chardet

class MDFileViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("MD 파일 뷰어")
        self.root.geometry("800x600")
        
        # 상단 프레임 (버튼)
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)
        
        # 폴더 선택 버튼
        self.select_button = tk.Button(
            top_frame, 
            text="폴더 선택", 
            command=self.select_folder,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=20
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # 새로고침 버튼
        self.refresh_button = tk.Button(
            top_frame,
            text="새로고침",
            command=self.refresh_files,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            padx=20,
            state=tk.DISABLED
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 선택된 폴더 경로 표시
        self.path_label = tk.Label(
            root, 
            text="폴더를 선택해주세요", 
            font=("Arial", 10),
            fg="gray"
        )
        self.path_label.pack(pady=(0, 10))
        
        # 텍스트 영역 (스크롤 가능)
        self.text_area = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=("Consolas", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.selected_folder = None
    
    def detect_encoding(self, file_path):
        """파일의 인코딩을 감지합니다."""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            print(f"인코딩 감지 오류 ({file_path}): {e}")
            return 'utf-8'  # 기본값
    
    def read_md_file(self, file_path):
        """MD 파일을 읽어서 내용을 반환합니다."""
        try:
            # 인코딩 감지
            encoding = self.detect_encoding(file_path)
            
            # 파일 읽기
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                return content, encoding
        except Exception as e:
            return f"파일 읽기 오류: {str(e)}", "error"
    
    def find_md_files(self, folder_path):
        """폴더에서 MD 파일들을 찾아 중복 제거하여 반환합니다."""
        md_files = set()  # set을 사용하여 중복 제거
        
        try:
            # 폴더 내 모든 파일 검사
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                
                # 파일인지 확인하고 확장자 검사
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file_name.lower())
                    if ext == '.md':
                        md_files.add(file_path)
        except Exception as e:
            print(f"폴더 읽기 오류: {e}")
        
        return sorted(list(md_files))  # 정렬된 리스트로 반환
    
    def select_folder(self):
        """폴더 선택 대화상자를 엽니다."""
        folder_path = filedialog.askdirectory(title="MD 파일이 있는 폴더를 선택하세요")
        
        if folder_path:
            self.selected_folder = folder_path
            self.path_label.config(text=f"선택된 폴더: {folder_path}")
            self.refresh_button.config(state=tk.NORMAL)
            self.load_md_files()
    
    def refresh_files(self):
        """현재 선택된 폴더의 MD 파일들을 다시 로드합니다."""
        if self.selected_folder:
            self.load_md_files()
    
    def load_md_files(self):
        """선택된 폴더의 모든 MD 파일을 로드합니다."""
        if not self.selected_folder:
            return
        
        # 텍스트 영역 초기화
        self.text_area.delete(1.0, tk.END)
        
        # MD 파일 찾기 (중복 제거됨)
        md_files = self.find_md_files(self.selected_folder)
        
        if not md_files:
            self.text_area.insert(tk.END, "선택된 폴더에 MD 파일이 없습니다.")
            return
        
        total_files = len(md_files)
        self.text_area.insert(tk.END, f"총 {total_files}개의 MD 파일을 발견했습니다.\n")
        self.text_area.insert(tk.END, "=" * 80 + "\n\n")
        
        # 각 MD 파일 읽기
        for i, file_path in enumerate(md_files, 1):
            file_name = os.path.basename(file_path)
            
            self.text_area.insert(tk.END, f"[{i}/{total_files}] 파일: {file_name}\n")
            self.text_area.insert(tk.END, "-" * 60 + "\n")
            
            # 파일 내용 읽기
            content, encoding = self.read_md_file(file_path)
            
            if encoding != "error":
                self.text_area.insert(tk.END, f"인코딩: {encoding}\n")
                self.text_area.insert(tk.END, f"파일 크기: {len(content)} 문자\n")
                self.text_area.insert(tk.END, f"파일 경로: {file_path}\n\n")
                self.text_area.insert(tk.END, content)
            else:
                self.text_area.insert(tk.END, content)
            
            self.text_area.insert(tk.END, "\n\n" + "=" * 80 + "\n\n")
            
            # GUI 업데이트 (긴 파일 처리 시 응답성 유지)
            self.root.update_idletasks()
        
        # 맨 위로 스크롤
        self.text_area.see(1.0)
        
        messagebox.showinfo("완료", f"{total_files}개의 MD 파일을 성공적으로 로드했습니다.")

def main():
    root = tk.Tk()
    app = MDFileViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()