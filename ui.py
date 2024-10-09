import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from tkinter import font as tkFont
import pandas as pd
import sys
from his_geo import geocoder
import threading 


try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"Error setting DPI awareness: {e}")

root = tk.Tk()
root.title("His-Geo Geocoder")
root_bg = root.cget('bg')


defaultFont = tkFont.nametofont("TkDefaultFont")
defaultFont.config(family="Helvetica", size=10)

textFont = tkFont.Font(family="Helvetica", size=12)


style = ttk.Style()
style.theme_use('xpnative')  # 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'


style.configure('TButton', font=textFont)
style.configure('TLabel', font=textFont, padding=5, background=root_bg)
style.configure('TEntry', font=textFont, padding=5)
style.configure('TCheckbutton', font=textFont, padding=5)

class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)  # 自动滚动到最新的输出

    def flush(self):
        pass

def run_geocoder():
    try:
        input_file = input_file_path.get()
        output_folder = output_folder_path.get()
        output_file = f"{output_folder}/output.csv"  # 构建输出文件路径
        location_column = location_column_entry.get()
        preferences = [pref for pref in ["modern", "historic"] if preferences_vars[pref].get()]
        try:
            year_range_begin = int(year_range_begin_entry.get())
            year_range_end = int(year_range_end_entry.get())
            year_range = (year_range_begin, year_range_end)
        except:
            year_range = ()
            print("Invalid year range.")
        replace_words = eval(replace_words_text.get("1.0", tk.END))

        df = pd.read_csv(input_file, encoding='utf-8-sig')
        addresses = df[location_column].tolist()

        geocoder_test = geocoder.Geocoder(
            addresses,
            lang='ch',
            preferences=preferences,
            year_range=year_range,
            replace_words=replace_words,
            if_certainty=False
        )

        geocoder_test.detect_direction()
        geocoder_test.match_address()
        geocoder_test.calculate_point()
        geocoder_test.data.to_csv(output_file, encoding='utf-8-sig')
        
        print("Geocoding completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def start_geocoder_thread():
    geocoder_thread = threading.Thread(target=run_geocoder)
    geocoder_thread.start()


# File selection
ttk.Label(root, text="Input file:", background=root_bg).grid(row=0, column=0, sticky="w")
input_file_path = tk.StringVar()
ttk.Entry(root, textvariable=input_file_path).grid(row=0, column=1, sticky="we", padx=10, pady=5)
ttk.Button(root, text="Browse...", command=lambda: input_file_path.set(filedialog.askopenfilename())).grid(row=0, column=2, padx=10, pady=5)

# Folder selection
ttk.Label(root, text="Output folder:", background=root_bg).grid(row=1, column=0, sticky="w")
output_folder_path = tk.StringVar()
ttk.Entry(root, textvariable=output_folder_path).grid(row=1, column=1, sticky="we", padx=10, pady=5)
ttk.Button(root, text="Browse...", command=lambda: output_folder_path.set(filedialog.askdirectory())).grid(row=1, column=2, padx=10, pady=5)

# Parameters
ttk.Label(root, text="Location Column:", background=root_bg).grid(row=2, column=0, sticky="w")
location_column_entry = ttk.Entry(root)
location_column_entry.grid(row=2, column=1, sticky="we", padx=10, pady=5)

preferences_vars = {"modern": tk.BooleanVar(), "historic": tk.BooleanVar()}
tk.Checkbutton(root, text="Modern", variable=preferences_vars["modern"]).grid(row=4, column=0, sticky="w")
tk.Checkbutton(root, text="Historic", variable=preferences_vars["historic"]).grid(row=4, column=1, sticky="w")
preferences_vars["historic"].set(True)

ttk.Label(root, text="Year Range Begin:", background=root_bg).grid(row=5, column=0, sticky="w")
year_range_begin_entry = ttk.Entry(root)
year_range_begin_entry.grid(row=5, column=1, sticky="we", padx=10, pady=5)
year_range_begin_entry.insert(tk.END, "1636")

ttk.Label(root, text="Year Range End:", background=root_bg).grid(row=6, column=0, sticky="w")
year_range_end_entry = ttk.Entry(root)
year_range_end_entry.grid(row=6, column=1, sticky="we", padx=10, pady=5)
year_range_end_entry.insert(tk.END, "1912")

ttk.Label(root, text="Replace Words:", background=root_bg).grid(row=7, column=0, sticky="nw")
replace_words_text = scrolledtext.ScrolledText(root, height=4, width=50, font=textFont)
replace_words_text.grid(row=7, column=1, sticky="we", padx=10, pady=5)
replace_words_text.insert(tk.END, '{"长江水师": ""}') 

# Run button
run_button = ttk.Button(root, text="Run Geocoder", command=start_geocoder_thread)
run_button.grid(row=8, column=0, columnspan=3, pady=10)

# Output Text Box
output_text = scrolledtext.ScrolledText(root, height=10, font=textFont)
output_text.grid(row=9, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
sys.stdout = TextRedirector(output_text)

root.mainloop()

sys.stdout = sys.__stdout__
