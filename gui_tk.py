#!/usr/bin/env python3
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from convert_confluence_html import convert_directory


class ConverterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Confluence HTML → Markdown Converter")
        self.geometry("720x360")
        self._build_widgets()

    def _build_widgets(self):
        pad = {'padx': 8, 'pady': 6}

        # Input directory
        frm_in = ttk.Frame(self)
        frm_in.pack(fill='x', **pad)
        ttk.Label(frm_in, text="Input (HTML pack directory):").pack(anchor='w')
        in_row = ttk.Frame(frm_in)
        in_row.pack(fill='x')
        self.var_input = tk.StringVar()
        self.ent_input = ttk.Entry(in_row, textvariable=self.var_input)
        self.ent_input.pack(side='left', fill='x', expand=True)
        ttk.Button(in_row, text="Browse…", command=self._browse_input).pack(side='left', padx=6)

        # Output directory
        frm_out = ttk.Frame(self)
        frm_out.pack(fill='x', **pad)
        ttk.Label(frm_out, text="Output (Markdown directory):").pack(anchor='w')
        out_row = ttk.Frame(frm_out)
        out_row.pack(fill='x')
        self.var_output = tk.StringVar()
        self.ent_output = ttk.Entry(out_row, textvariable=self.var_output)
        self.ent_output.pack(side='left', fill='x', expand=True)
        ttk.Button(out_row, text="Browse…", command=self._browse_output).pack(side='left', padx=6)

        # Optional CSS selector
        frm_sel = ttk.Frame(self)
        frm_sel.pack(fill='x', **pad)
        ttk.Label(frm_sel, text="Main content CSS selector (optional):").pack(anchor='w')
        self.var_selector = tk.StringVar()
        ttk.Entry(frm_sel, textvariable=self.var_selector).pack(fill='x')

        # Run button
        frm_run = ttk.Frame(self)
        frm_run.pack(fill='x', **pad)
        self.btn_run = ttk.Button(frm_run, text="Run Conversion", command=self._run_conversion)
        self.btn_run.pack(side='left')

        # Log area
        frm_log = ttk.LabelFrame(self, text="Log")
        frm_log.pack(fill='both', expand=True, **pad)
        self.txt_log = tk.Text(frm_log, height=10)
        self.txt_log.pack(fill='both', expand=True)

    def _browse_input(self):
        path = filedialog.askdirectory(title="Select Confluence HTML export folder")
        if path:
            self.var_input.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select output folder (Markdown)")
        if path:
            self.var_output.set(path)

    def _run_conversion(self):
        in_dir = self.var_input.get().strip()
        out_dir = self.var_output.get().strip()
        selector = self.var_selector.get().strip() or None

        if not in_dir:
            messagebox.showerror("Missing input", "Please select the input HTML export folder.")
            return
        if not out_dir:
            messagebox.showerror("Missing output", "Please select the output folder.")
            return

        self.btn_run.configure(state='disabled')
        self._log(f"Starting conversion…\nInput: {in_dir}\nOutput: {out_dir}\nSelector: {selector or '(auto)'}\n")

        def worker():
            try:
                input_path = Path(in_dir).resolve()
                output_path = Path(out_dir).resolve()
                results = convert_directory(input_path, output_path, selector)
                self._log(f"\nDone. Converted {len(results)} HTML files.\n")
                messagebox.showinfo("Conversion complete", f"Converted {len(results)} HTML files.")
            except Exception as e:
                self._log(f"\nError: {e}\n")
                messagebox.showerror("Conversion failed", str(e))
            finally:
                self.btn_run.configure(state='normal')

        threading.Thread(target=worker, daemon=True).start()

    def _log(self, msg: str):
        self.txt_log.insert('end', msg)
        self.txt_log.see('end')


def main():
    app = ConverterGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
