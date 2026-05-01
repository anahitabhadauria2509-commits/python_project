import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import matplotlib.pyplot as plt


class CareerPathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 CareerPath: Professional Future Advisor")
        self.root.geometry("1280x780")
        
        # --- UI COLORS ---
        self.bg_dark = "#121212"       
        self.card_bg = "#1e1e1e"       
        self.accent_blue = "#00d2ff"   
        self.accent_green = "#32ff7e"  
        self.text_main = "#ffffff"     
        self.report_paper = "#f8fafc"   
        
        self.root.configure(bg=self.bg_dark)

        # SCHOLARSHIP DATABASE (UNCHANGED)
        self.scholarship_db = {
            'IIT': "• Govt Grant: Full fee waiver for SC/ST/PH\n• MCM: Merit-cum-Means support available.",
            'NLU': "• State Support: Specific grants for law students.\n• Merit-based: Reductions for CLAT top rankers.",
            'CENTRAL': "• Govt Schemes: Post-Matric and Central Sector scholarships.",
            'PRIVATE': "• Entrance Merit: Up to 100% waiver on high scores.",
            'STATE': "• Domicile: 10-25% fee waiver for state residents.",
            'ENGINEERING': "• Technical Grants: AICTE Pragati for girls."
        }

        self.load_dataset()
        self.filtered_data = pd.DataFrame()  # for graph
        self.setup_ui()

    def load_dataset(self):
        path = os.path.join(os.path.expanduser("~"), "Documents", "colleges.csv")
        try:
            df = pd.read_csv(path)
            if 'name' not in df.columns:
                df = pd.read_csv(path, skiprows=1)
            df.columns = [str(c).strip().lower() for c in df.columns]
            self.colleges = df
        except Exception as e:
            messagebox.showerror("File Error", f"Could not load colleges.csv.\nError: {e}")
            self.root.destroy()

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=self.bg_dark)
        header.pack(fill="x", pady=15)
        tk.Label(header, text="CAREER PATH", font=("Impact", 36),
            fg=self.accent_blue, bg=self.bg_dark).pack()

        # CONTROL PANEL
        cp = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=15,
            highlightbackground=self.accent_blue, highlightthickness=1)
        cp.pack(pady=10, padx=40, fill="x")

        tk.Label(cp, text="Filter by Category", bg=self.card_bg, fg="#a0a0a0").grid(row=0, column=0)
        categories = ["All Categories", "Engineering", "Private", "Government", "State University", "Central University", "NLU", "University"]
        self.type_var = tk.StringVar(value="All Categories")
        ttk.Combobox(cp, textvariable=self.type_var, values=categories, state="readonly").grid(row=1, column=0)

        tk.Label(cp, text="Search College Name", bg=self.card_bg, fg="#a0a0a0").grid(row=0, column=1)
        self.name_search_entry = tk.Entry(cp, bg="#2a2a2a", fg="white", insertbackground="white")
        self.name_search_entry.grid(row=1, column=1)

        tk.Label(cp, text="Max Budget (₹)", bg=self.card_bg, fg="#a0a0a0").grid(row=0, column=2)
        self.budget_entry = tk.Entry(cp, bg="#2a2a2a", fg="white", insertbackground="white")
        self.budget_entry.insert(0, "1000000")
        self.budget_entry.grid(row=1, column=2)

        self.search_btn = tk.Label(cp, text="DISCOVER 🔍", bg="#000", fg=self.accent_green, cursor="hand2")
        self.search_btn.grid(row=0, column=3, rowspan=2)
        self.search_btn.bind("<Button-1>", lambda e: self.update_list())

        # GRAPH BUTTON
        tk.Button(self.root, text="📊 Show Fees Graph",
                command=self.show_graph,
                bg="#000", fg=self.accent_green).pack(pady=5)

        # MAIN VIEW
        main_view = tk.Frame(self.root, bg=self.bg_dark)
        main_view.pack(fill="both", expand=True, padx=40, pady=5)

        # LEFT TABLE
        list_frame = tk.Frame(main_view, bg=self.bg_dark)
        list_frame.pack(side="left", fill="both", expand=True)

        cols = ('name', 'city', 'fees_ug_inr', 'rating')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings')

        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.update_formal_report)

        # RIGHT REPORT PANEL
        self.report_panel = tk.Frame(main_view, bg=self.report_paper, width=380)
        self.report_panel.pack(side="right", fill="y", padx=(20, 0))
        self.report_panel.pack_propagate(False)

        tk.Label(self.report_panel, text="FINANCIAL AID REPORT",
            bg="#e2e8f0", fg="#1e293b", pady=10).pack(fill="x")

        self.report_content = tk.Frame(self.report_panel, bg=self.report_paper)
        self.report_content.pack(fill="both", expand=True)

    # FILTER
    def update_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            budget = float(self.budget_entry.get())
            cat = self.type_var.get().lower()
            name = self.name_search_entry.get().lower()

            mask = (self.colleges['fees_ug_inr'] <= budget)

            if cat != "all categories":
                mask &= (self.colleges['type'].str.lower() == cat)

            if name:
                mask &= (self.colleges['name'].str.lower().str.contains(name))

            filtered = self.colleges[mask]
            self.filtered_data = filtered  # for graph

            if filtered.empty:
                messagebox.showinfo("Result", "No colleges found")
                return

            for _, row in filtered.iterrows():
                self.tree.insert("", "end",
                    values=(row['name'], row['city'],
                        row['fees_ug_inr'], row['rating']))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # SCHOLARSHIP (UNCHANGED LOGIC, ONLY UI FIX)
    def update_formal_report(self, event):
        for widget in self.report_content.winfo_children():
            widget.destroy()

        selected = self.tree.selection()
        if not selected:
            return

        college_data = self.tree.item(selected, "values")
        college_name = college_data[0]

        # TITLE
        tk.Label(self.report_content, text=college_name,
                bg=self.report_paper,
                fg="#0f172a",
                font=("Arial", 12, "bold"),
                wraplength=320,
                justify="left").pack(anchor="w", pady=(0, 10))

        # SCHOLARSHIP LOGIC (UNCHANGED)
        info = "Scholarship guidelines available."
        name_upper = college_name.upper()

        if "IIT" in name_upper:
            info = self.scholarship_db['IIT']
        elif "NLU" in name_upper:
            info = self.scholarship_db['NLU']
        elif "PRIVATE" in name_upper:
            info = self.scholarship_db['PRIVATE']

        # TEXT DISPLAY FIXED
        tk.Label(self.report_content, text=info,
                bg=self.report_paper,
                fg="#334155",
                font=("Arial", 10),
                wraplength=320,
                justify="left").pack(anchor="w")

    # GRAPH
    def show_graph(self):
        if self.filtered_data.empty:
            messagebox.showinfo("Info", "Please search first")
            return

        top = self.filtered_data.sort_values(by="fees_ug_inr",
            ascending=False).head(10)

        plt.figure(figsize=(10, 5))
        plt.bar(top['name'], top['fees_ug_inr'], color='skyblue')
        plt.xticks(rotation=45, ha='right')
        plt.title("College Fee Comparison")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = CareerPathApp(root)
    root.mainloop()