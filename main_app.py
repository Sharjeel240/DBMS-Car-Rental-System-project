import csv
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CarRentalFullGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Car Rental & Return Management System - Professional Edition")
        self.geometry("1200x800")

        # Main Tab Container
        self.tabview = ctk.CTkTabview(self, width=1160, height=760)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_fleet = self.tabview.add("Fleet Management (CRUD)")
        self.tab_issue = self.tabview.add("Issue Vehicle")
        self.tab_return = self.tabview.add("Return & Billing")
        self.tab_reports = self.tabview.add("Executive Dashboard & Reports")
        self.tab_db_inspector = self.tabview.add("Live MySQL Inspector")

        self.build_fleet_tab()
        self.build_issue_tab()
        self.build_return_tab()
        self.build_reports_tab()
        self.build_db_inspector_tab()

    # ==========================================
    # TAB 1: FLEET MANAGEMENT (CRUD + SEARCH)
    # ==========================================
    def build_fleet_tab(self):
        # Entry Form
        form = ctk.CTkFrame(self.tab_fleet)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Make:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_make = ctk.CTkEntry(form, placeholder_text="e.g. Honda")
        self.ent_make.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Model:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_model = ctk.CTkEntry(form, placeholder_text="e.g. Civic")
        self.ent_model.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(form, text="Plate:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_plate = ctk.CTkEntry(form, placeholder_text="e.g. ABC-123")
        self.ent_plate.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Odometer:").grid(row=1, column=2, padx=5, pady=5)
        self.ent_odo = ctk.CTkEntry(form, placeholder_text="e.g. 12000")
        self.ent_odo.grid(row=1, column=3, padx=5, pady=5)

        btn_add = ctk.CTkButton(form, text="Insert Vehicle", command=self.add_vehicle)
        btn_add.grid(row=0, column=4, rowspan=2, padx=15, pady=5)

        # Quick Search Bar & Double-Click Hint
        search_bar = ctk.CTkFrame(self.tab_fleet)
        search_bar.pack(fill="x", padx=10, pady=(5, 0))

        ctk.CTkLabel(search_bar, text="Search Fleet:").pack(side="left", padx=10)
        self.ent_search = ctk.CTkEntry(search_bar, placeholder_text="Type make, model, or plate...")
        self.ent_search.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.ent_search.bind("<KeyRelease>", self.filter_fleet)

        ctk.CTkLabel(search_bar, text="💡 Tip: Double-click a row to auto-select for rental", font=("Arial", 11, "italic")).pack(side="right", padx=10)

        # Fleet Treeview Table
        self.tree_fleet = ttk.Treeview(
            self.tab_fleet, 
            columns=("ID", "Make", "Model", "Plate", "Status", "Odometer", "Category"), 
            show="headings"
        )
        for col in ("ID", "Make", "Model", "Plate", "Status", "Odometer", "Category"):
            self.tree_fleet.heading(col, text=col)
            self.tree_fleet.column(col, width=130, anchor="center")

        # Color Tags Setup
        self.tree_fleet.tag_configure("AVAILABLE", foreground="#2ecc71")
        self.tree_fleet.tag_configure("RENTED", foreground="#e67e22")
        self.tree_fleet.tag_configure("MAINTENANCE", foreground="#e74c3c")

        self.tree_fleet.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_fleet.bind("<Double-1>", self.on_vehicle_double_click)

        btn_del = ctk.CTkButton(
            self.tab_fleet, 
            text="Delete Selected Vehicle", 
            fg_color="#e74c3c", 
            hover_color="#c0392b", 
            command=self.delete_vehicle
        )
        btn_del.pack(anchor="e", padx=10, pady=5)

        self.load_fleet()

    def load_fleet(self):
        for row in self.tree_fleet.get_children():
            self.tree_fleet.delete(row)
        q = """
            SELECT v.vehicle_id, v.make, v.model, v.license_plate, v.status, v.odometer, c.category_name
            FROM vehicles v
            JOIN vehicle_categories c ON v.category_id = c.category_id
            ORDER BY v.vehicle_id DESC
        """
        rows = database.fetch_all(q)
        for r in rows:
            status = r['status']
            self.tree_fleet.insert("", "end", values=(
                r['vehicle_id'], r['make'], r['model'], r['license_plate'], status, r['odometer'], r['category_name']
            ), tags=(status,))

    def filter_fleet(self, event=None):
        term = self.ent_search.get().lower()
        for row_id in self.tree_fleet.get_children():
            vals = [str(v).lower() for v in self.tree_fleet.item(row_id)['values']]
            if any(term in v for v in vals):
                self.tree_fleet.reattach(row_id, '', 'end')
            else:
                self.tree_fleet.detach(row_id)

    def on_vehicle_double_click(self, event):
        selected = self.tree_fleet.selection()
        if selected:
            v_id = self.tree_fleet.item(selected[0])['values'][0]
            self.ent_veh_id.delete(0, 'end')
            self.ent_veh_id.insert(0, str(v_id))
            self.tabview.set("Issue Vehicle")
            messagebox.showinfo("Selected", f"Vehicle ID {v_id} set in Issue Vehicle tab!")

    def add_vehicle(self):
        make, model, plate, odo_str = self.ent_make.get().strip(), self.ent_model.get().strip(), self.ent_plate.get().strip(), self.ent_odo.get().strip()

        if not (make and model and plate and odo_str):
            messagebox.showerror("Error", "All vehicle fields are required.")
            return

        try:
            odo = int(odo_str)
        except ValueError:
            messagebox.showerror("Error", "Odometer must be a valid integer.")
            return

        vin = f"VIN-{plate}"
        q = """
            INSERT INTO vehicles (vin, make, model, year, license_plate, status, odometer, category_id, branch_id)
            VALUES (%s, %s, %s, 2024, %s, 'AVAILABLE', %s, 1, 1)
        """
        try:
            database.execute_query(q, (vin, make, model, plate, odo))
            messagebox.showinfo("Success", f"Vehicle {plate} inserted successfully!")
            self.load_fleet()
            self.refresh_inspector()
            self.update_dashboard_kpis()
            self.ent_make.delete(0, 'end')
            self.ent_model.delete(0, 'end')
            self.ent_plate.delete(0, 'end')
            self.ent_odo.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_vehicle(self):
        selected = self.tree_fleet.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a vehicle row to delete.")
            return
        v_id = self.tree_fleet.item(selected[0])['values'][0]
        try:
            database.execute_query("DELETE FROM vehicles WHERE vehicle_id = %s", (v_id,))
            self.load_fleet()
            self.refresh_inspector()
            self.update_dashboard_kpis()
            messagebox.showinfo("Deleted", f"Vehicle ID {v_id} removed from database.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete vehicle: {e}")

    # ==========================================
    # TAB 2: ISSUE VEHICLE
    # ==========================================
    def build_issue_tab(self):
        frame = ctk.CTkFrame(self.tab_issue)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Customer ID:").grid(row=0, column=0, padx=10, pady=10)
        self.ent_cust_id = ctk.CTkEntry(frame, placeholder_text="1")
        self.ent_cust_id.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Vehicle ID:").grid(row=1, column=0, padx=10, pady=10)
        self.ent_veh_id = ctk.CTkEntry(frame, placeholder_text="1")
        self.ent_veh_id.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Rental Duration (Days):").grid(row=2, column=0, padx=10, pady=10)
        self.ent_days = ctk.CTkEntry(frame, placeholder_text="3")
        self.ent_days.grid(row=2, column=1, padx=10, pady=10)

        btn_issue = ctk.CTkButton(frame, text="Issue Vehicle & Check Out", command=self.issue_vehicle)
        btn_issue.grid(row=3, column=0, columnspan=2, pady=20)

    def issue_vehicle(self):
        try:
            cust_id = int(self.ent_cust_id.get().strip())
            veh_id = int(self.ent_veh_id.get().strip())
            days = int(self.ent_days.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Customer ID, Vehicle ID, and Duration must be valid numbers.")
            return

        veh = database.fetch_all("SELECT status, odometer FROM vehicles WHERE vehicle_id = %s", (veh_id,))
        if not veh:
            messagebox.showerror("Error", f"Vehicle ID {veh_id} does not exist.")
            return
        if veh[0]['status'] != 'AVAILABLE':
            messagebox.showerror("Unavailable", f"Vehicle ID {veh_id} is currently '{veh[0]['status']}'.")
            return

        odo = veh[0]['odometer']
        q = """
            INSERT INTO rentals (customer_id, vehicle_id, pickup_date, expected_return_date, days_rented, pickup_odometer, pickup_fuel, status)
            VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL %s DAY), %s, %s, 100.0, 'ACTIVE')
        """
        database.execute_query(q, (cust_id, veh_id, days, days, odo))
        database.execute_query("UPDATE vehicles SET status = 'RENTED' WHERE vehicle_id = %s", (veh_id,))
        
        messagebox.showinfo("Success", f"Vehicle {veh_id} issued successfully!")
        self.load_fleet()
        self.refresh_inspector()
        self.update_dashboard_kpis()
    # ==========================================
    # TAB 3: RETURN & BILLING
    # ==========================================
    def build_return_tab(self):
        frame = ctk.CTkFrame(self.tab_return)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Rental ID:").grid(row=0, column=0, padx=10, pady=10)
        self.ent_ret_id = ctk.CTkEntry(frame, placeholder_text="1")
        self.ent_ret_id.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Return Odometer:").grid(row=1, column=0, padx=10, pady=10)
        self.ent_ret_odo = ctk.CTkEntry(frame, placeholder_text="15500")
        self.ent_ret_odo.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Damage Charge ($):").grid(row=2, column=0, padx=10, pady=10)
        self.ent_damage_cost = ctk.CTkEntry(frame, placeholder_text="0.00")
        self.ent_damage_cost.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Damage Notes:").grid(row=3, column=0, padx=10, pady=10)
        self.ent_damage_desc = ctk.CTkEntry(frame, placeholder_text="e.g. Scratched Door")
        self.ent_damage_desc.grid(row=3, column=1, padx=10, pady=10)

        btn_return = ctk.CTkButton(frame, text="Process Return & Calculate Charge", command=self.process_return)
        btn_return.grid(row=4, column=0, columnspan=2, pady=20)

        self.lbl_bill = ctk.CTkLabel(frame, text="Calculated Invoice Total: $0.00", font=("Arial", 16, "bold"))
        self.lbl_bill.grid(row=5, column=0, columnspan=2, pady=10)

    def process_return(self):
        try:
            r_id = int(self.ent_ret_id.get().strip())
            ret_odo = int(self.ent_ret_odo.get().strip())
            damage = float(self.ent_damage_cost.get().strip() or 0.0)
            desc = self.ent_damage_desc.get().strip() or "No description"
        except ValueError:
            messagebox.showerror("Input Error", "Rental ID, Return Odometer, and Damage Fee must be valid numbers.")
            return

        q = """
            SELECT r.vehicle_id, r.days_rented, c.daily_rate
            FROM rentals r
            JOIN vehicles v ON r.vehicle_id = v.vehicle_id
            JOIN vehicle_categories c ON v.category_id = c.category_id
            WHERE r.rental_id = %s AND r.status = 'ACTIVE'
        """
        rental = database.fetch_all(q, (r_id,))
        if not rental:
            messagebox.showerror("Error", f"No ACTIVE rental found for Rental ID {r_id}.")
            return

        v_id = rental[0]['vehicle_id']
        days = int(rental[0]['days_rented'])
        daily_rate = float(rental[0]['daily_rate'])
        
        base_cost = days * daily_rate
        total = base_cost + damage

        database.execute_query(
            "UPDATE rentals SET actual_return_date = NOW(), return_odometer = %s, status = 'RETURNED' WHERE rental_id = %s",
            (ret_odo, r_id)
        )
        database.execute_query(
            "UPDATE vehicles SET status = 'AVAILABLE', odometer = %s WHERE vehicle_id = %s",
            (ret_odo, v_id)
        )

        if damage > 0:
            database.execute_query(
                "INSERT INTO damages (rental_id, description, repair_cost) VALUES (%s, %s, %s)",
                (r_id, desc, damage)
            )

        database.execute_query(
            "INSERT INTO invoices (rental_id, base_cost, damage_fee, total_amount, payment_status) VALUES (%s, %s, %s, %s, 'PAID')",
            (r_id, base_cost, damage, total)
        )

        self.lbl_bill.configure(text=f"Calculated Invoice Total: ${total:.2f}")
        messagebox.showinfo("Success", f"Return processed successfully!\nTotal Charge: ${total:.2f}")

        self.load_fleet()
        self.load_reports()
        self.refresh_inspector()
        self.update_dashboard_kpis()

    # ==========================================
    # TAB 4: EXECUTIVE DASHBOARD & REPORTS
    # ==========================================
    def build_reports_tab(self):
        # KPI Cards Frame
        kpi_frame = ctk.CTkFrame(self.tab_reports)
        kpi_frame.pack(fill="x", padx=10, pady=10)

        self.card_revenue = ctk.CTkLabel(kpi_frame, text="Total Revenue\n$0.00", font=("Arial", 16, "bold"), fg_color="#1e272c", corner_radius=8, width=220, height=60)
        self.card_revenue.grid(row=0, column=0, padx=10, pady=10)

        self.card_rentals = ctk.CTkLabel(kpi_frame, text="Active Rentals\n0", font=("Arial", 16, "bold"), fg_color="#1e272c", corner_radius=8, width=220, height=60)
        self.card_rentals.grid(row=0, column=1, padx=10, pady=10)

        self.card_fleet = ctk.CTkLabel(kpi_frame, text="Fleet Size\n0", font=("Arial", 16, "bold"), fg_color="#1e272c", corner_radius=8, width=220, height=60)
        self.card_fleet.grid(row=0, column=2, padx=10, pady=10)

        self.card_damages = ctk.CTkLabel(kpi_frame, text="Total Damage Fees\n$0.00", font=("Arial", 16, "bold"), fg_color="#1e272c", corner_radius=8, width=220, height=60)
        self.card_damages.grid(row=0, column=3, padx=10, pady=10)

        # Action Bar
        action_bar = ctk.CTkFrame(self.tab_reports)
        action_bar.pack(fill="x", padx=10, pady=5)

        btn_refresh = ctk.CTkButton(action_bar, text="Refresh Reports & KPIs", command=self.load_reports)
        btn_refresh.pack(side="left", padx=10, pady=5)

        btn_export = ctk.CTkButton(action_bar, text="Export Audit to CSV", fg_color="#27ae60", hover_color="#219150", command=self.export_csv)
        btn_export.pack(side="right", padx=10, pady=5)

        # Reports Table
        self.tree_reports = ttk.Treeview(
            self.tab_reports, 
            columns=("Rental ID", "Customer", "Vehicle", "Total Amount", "Payment Status"), 
            show="headings"
        )
        for col in ("Rental ID", "Customer", "Vehicle", "Total Amount", "Payment Status"):
            self.tree_reports.heading(col, text=col)
            self.tree_reports.column(col, width=150, anchor="center")

        self.tree_reports.tag_configure("PAID", foreground="#2ecc71")
        self.tree_reports.tag_configure("UNPAID", foreground="#e74c3c")

        self.tree_reports.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_reports()

    def update_dashboard_kpis(self):
        rev_res = database.fetch_all("SELECT SUM(total_amount) AS rev FROM invoices")
        rev = rev_res[0]['rev'] if rev_res and rev_res[0]['rev'] else 0.0

        rent_res = database.fetch_all("SELECT COUNT(*) AS active FROM rentals WHERE status = 'ACTIVE'")
        active_rentals = rent_res[0]['active'] if rent_res else 0

        fleet_res = database.fetch_all("SELECT COUNT(*) AS total FROM vehicles")
        fleet_size = fleet_res[0]['total'] if fleet_res else 0

        dmg_res = database.fetch_all("SELECT SUM(repair_cost) AS dmg FROM damages")
        dmg_cost = dmg_res[0]['dmg'] if dmg_res and dmg_res[0]['dmg'] else 0.0

        self.card_revenue.configure(text=f"Total Revenue\n${rev:.2f}")
        self.card_rentals.configure(text=f"Active Rentals\n{active_rentals}")
        self.card_fleet.configure(text=f"Fleet Size\n{fleet_size}")
        self.card_damages.configure(text=f"Total Damage Fees\n${dmg_cost:.2f}")

    def load_reports(self):
        for r in self.tree_reports.get_children():
            self.tree_reports.delete(r)

        q = """
            SELECT i.rental_id, c.full_name, CONCAT(v.make, ' ', v.model) AS vehicle, i.total_amount, i.payment_status
            FROM invoices i
            JOIN rentals r ON i.rental_id = r.rental_id
            JOIN customers c ON r.customer_id = c.customer_id
            JOIN vehicles v ON r.vehicle_id = v.vehicle_id
            ORDER BY i.invoice_id DESC
        """
        rows = database.fetch_all(q)
        if rows:
            for row in rows:
                amount = float(row['total_amount']) if row['total_amount'] is not None else 0.0
                status = row['payment_status']
                self.tree_reports.insert("", "end", values=(
                    row['rental_id'],
                    row['full_name'],
                    row['vehicle'],
                    f"${amount:.2f}",
                    status
                ), tags=(status,))

        self.update_dashboard_kpis()

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        q = """
            SELECT i.invoice_id, i.rental_id, c.full_name AS customer, CONCAT(v.make, ' ', v.model) AS vehicle,
                   i.base_cost, i.damage_fee, i.total_amount, i.payment_status, i.issue_date
            FROM invoices i
            JOIN rentals r ON i.rental_id = r.rental_id
            JOIN customers c ON r.customer_id = c.customer_id
            JOIN vehicles v ON r.vehicle_id = v.vehicle_id
        """
        rows = database.fetch_all(q)
        if not rows:
            messagebox.showwarning("Warning", "No invoice records available to export.")
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Audit report exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save CSV file: {e}")

    # ==========================================
    # TAB 5: LIVE MYSQL DATABASE INSPECTOR
    # ==========================================
    def build_db_inspector_tab(self):
        top_bar = ctk.CTkFrame(self.tab_db_inspector)
        top_bar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_bar, text="Select MySQL Table:").pack(side="left", padx=10)
        self.combo_tables = ctk.CTkComboBox(
            top_bar, 
            values=["vehicles", "customers", "rentals", "damages", "invoices", "vehicle_categories", "branches"], 
            command=self.on_table_select
        )
        self.combo_tables.pack(side="left", padx=10)
        self.combo_tables.set("vehicles")

        btn_ref = ctk.CTkButton(top_bar, text="Fetch Latest Database State", command=self.refresh_inspector)
        btn_ref.pack(side="left", padx=10)

        self.tree_inspector = ttk.Treeview(self.tab_db_inspector, show="headings")
        self.tree_inspector.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_inspector()

    def on_table_select(self, choice):
        self.refresh_inspector()

    def refresh_inspector(self):
        table_name = self.combo_tables.get().strip()
        query = f"SELECT * FROM `{table_name}`;"
        cols, rows = database.fetch_raw_query(query)

        self.tree_inspector.delete(*self.tree_inspector.get_children())
        self.tree_inspector["columns"] = cols

        if cols:
            for c in cols:
                self.tree_inspector.heading(c, text=c)
                self.tree_inspector.column(c, width=130, anchor="center")

            for r in rows:
                formatted_row = [str(val) if val is not None else "NULL" for val in r]
                self.tree_inspector.insert("", "end", values=formatted_row)

if __name__ == "__main__":
    app = CarRentalFullGUI()
    app.mainloop()