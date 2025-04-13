import tkinter as tk
from tkinter import messagebox, scrolledtext
from core import crawler, file_manager as fm

class CrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("네이버 파워링크 순위 추출기")
        self.root.geometry("600x500")

        self.excel_path = ""
        self.save_path = ""

        self.build_ui()

    def build_ui(self):
        tk.Button(self.root, text="엑셀 파일 선택", command=self.load_file).pack(pady=5)

        tk.Label(self.root, text="업체명 입력").pack()
        self.company_entry = tk.Entry(self.root, width=40)
        self.company_entry.pack(pady=5)

        # 크롤링 환경 선택
        tk.Label(self.root, text="크롤링 환경 선택").pack()
        self.env_var = tk.StringVar(value="mobile")
        tk.Radiobutton(self.root, text="모바일", variable=self.env_var, value="mobile").pack()
        tk.Radiobutton(self.root, text="PC", variable=self.env_var, value="pc").pack()

        tk.Button(self.root, text="결과 저장 경로", command=self.set_save_path).pack(pady=5)
        tk.Button(self.root, text="크롤링 시작", command=self.start_crawling, bg="green", fg="white").pack(pady=5)

        self.log = scrolledtext.ScrolledText(self.root, height=15, width=70)
        self.log.pack(pady=5)

    def log_write(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.root.update()

    def load_file(self):
        self.excel_path = fm.select_excel_file()
        self.log_write(f"선택된 파일: {self.excel_path}")

    def set_save_path(self):
        self.save_path = fm.select_save_path()
        self.log_write(f"저장 경로 설정됨: {self.save_path}")

    def start_crawling(self):
        if not self.excel_path or not self.company_entry.get() or not self.save_path:
            messagebox.showerror("에러", "모든 항목을 입력하세요.")
            return

        try:
            keywords = fm.read_keywords_from_excel(self.excel_path)
            env = self.env_var.get()
            df = crawler.crawl_keywords(keywords, self.company_entry.get(), env, logger=self.log_write)
            fm.save_to_excel(df, self.save_path)
            messagebox.showinfo("완료", "크롤링 완료 및 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("실패", str(e))
