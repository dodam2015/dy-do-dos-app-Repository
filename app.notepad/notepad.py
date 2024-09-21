import tkinter as tk
from tkinter import filedialog, messagebox, font

class Notepad:
    def __init__(self, master):
        self.master = master
        master.title("메모장")

        self.text_area = tk.Text(master, wrap='word', font=("Arial", 12))
        self.text_area.pack(expand=True, fill='both')

        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        # 파일 메뉴 추가
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="파일", menu=self.file_menu)
        self.file_menu.add_command(label="새로 만들기", command=self.new_file)
        self.file_menu.add_command(label="열기", command=self.open_file)
        self.file_menu.add_command(label="저장", command=self.save_file)
        self.file_menu.add_separator()
        
        # 종료 버튼 추가
        self.file_menu.add_command(label="종료", command=master.quit)

        # 편집 메뉴 추가
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="편집", menu=self.edit_menu)
        self.edit_menu.add_command(label="복사", command=self.copy_text)
        self.edit_menu.add_command(label="붙여넣기", command=self.paste_text)
        self.edit_menu.add_command(label="잘라내기", command=self.cut_text)

        # 설정 메뉴 추가
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="설정", menu=self.settings_menu)
        self.settings_menu.add_command(label="글자 크기 및 폰트 선택", command=self.open_settings)

        # 상태 표시줄 추가
        self.status_bar = tk.Label(master, text="인코딩: UTF-8 | 글자수: 0 | 용량: 0 Byte", anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

        # 텍스트 변경 시 상태 업데이트
        self.text_area.bind('<KeyRelease>', self.update_status)

    def new_file(self):
        self.text_area.delete(1.0, tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.update_status()  # 파일 열 때 상태 업데이트

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.update_status()  # 파일 저장 후 상태 업데이트

    def calculate_size(self, text):
        return len(text.encode('utf-8'))

    def update_status(self, event=None):
        text = self.text_area.get(1.0, tk.END)
        char_count = len(text) - 1  # 마지막 개행 문자 제외
        size_in_bytes = self.calculate_size(text)

        # 용량 변환
        if size_in_bytes < 1024:
            size_display = f"{size_in_bytes} Byte"
        elif size_in_bytes < 1024**2:
            size_display = f"{size_in_bytes / 1024:.2f} KB"
        elif size_in_bytes < 1024**3:
            size_display = f"{size_in_bytes / (1024**2):.2f} MB"
        elif size_in_bytes < 1024**4:
            size_display = f"{size_in_bytes / (1024**3):.2f} GB"
        else:
            size_display = f"{size_in_bytes / (1024**4):.2f} TB"

        self.status_bar.config(text=f"인코딩: UTF-8 | 글자수: {char_count} | 용량: {size_display}")

    def copy_text(self):
        self.master.clipboard_clear()
        text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        self.master.clipboard_append(text)

    def paste_text(self):
        try:
            text = self.master.clipboard_get()
            self.text_area.insert(tk.INSERT, text)
            self.update_status()  # 붙여넣기 후 상태 업데이트
        except tk.TclError:
            messagebox.showwarning("붙여넣기 오류", "클립보드에 붙여넣을 내용이 없습니다.")

    def cut_text(self):
        self.copy_text()
        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def open_settings(self):
        # 설정 창을 만듭니다.
        settings_window = tk.Toplevel(self.master)
        settings_window.title("설정")

        # 글자 크기 선택
        tk.Label(settings_window, text="글자 크기:").pack(pady=10)
        self.font_size_var = tk.IntVar(value=12)  # 기본 글자 크기
        font_size_entry = tk.Entry(settings_window, textvariable=self.font_size_var)
        font_size_entry.pack(pady=5)

        # 설치된 폰트를 보여주기 위한 프레임과 리스트박스 생성
        tk.Label(settings_window, text="폰트 선택:").pack(pady=10)
        
        self.font_listbox = tk.Listbox(settings_window, height=15, width=40)  # 리스트박스 생성
        available_fonts = font.families()  # 시스템에 설치된 폰트를 가져옵니다.
        for f in available_fonts:
            self.font_listbox.insert(tk.END, f)  # 각 폰트를 리스트박스에 추가합니다.
        
        self.font_listbox.pack(pady=5)

        # 선택된 폰트를 저장하기 위해 StringVar 사용
        self.font_var = tk.StringVar()
        self.font_listbox.bind('<<ListboxSelect>>', self.on_font_select)  # 리스트박스 선택 변화에 따른 이벤트 바인딩

        # 적용 버튼
        apply_button = tk.Button(settings_window, text="적용", command=self.apply_settings)
        apply_button.pack(pady=20)

    def on_font_select(self, event):
        # 리스트박스에서 선택된 폰트를 가져옴
        selected_indices = self.font_listbox.curselection()
        if selected_indices:
            selected_font = self.font_listbox.get(selected_indices[0])
            self.font_var.set(selected_font)  # 선택된 폰트를 변수에 저장

    def apply_settings(self):
        # 설정을 적용하는 메소드
        new_font_size = self.font_size_var.get()
        new_font_family = self.font_var.get()  # 선택된 폰트를 가져옴
        self.text_area.config(font=(new_font_family, new_font_size))

if __name__ == "__main__":
    root = tk.Tk()
    notepad = Notepad(root)
    root.mainloop()