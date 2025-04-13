from tkinter import filedialog
import pandas as pd

def select_excel_file():
    return filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])

def select_save_path():
    return filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

def read_keywords_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df['키워드'].tolist()

def save_to_excel(df, path):
    df.to_excel(path, index=False)
