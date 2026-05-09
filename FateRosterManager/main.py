import customtkinter as ctk
            self,
            width=600,
            height=300,
            font=("Consolas", 14)
        )
        self.textbox.pack(pady=10)

    def log(self, message):
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        self.update()

    def run_scan(self):
        self.textbox.delete("1.0", "end")

        self.names = scan_team(self.log)

        self.member_count.configure(
            text=f"Members: {len(self.names)}"
        )

        self.log("\n=== FINAL ROSTER ===")

        for name in self.names:
            self.log(name)

        self.log("\nScan complete.")

    def export_txt_gui(self):
        if not self.names:
            self.log("No data to export.")
            return

        export_txt(self.names)

        self.log(f"Saved TXT: {OUTPUT_TXT}")

    def export_csv_gui(self):
        if not self.names:
            self.log("No data to export.")
            return

        export_csv(self.names)

        self.log(f"Saved CSV: {OUTPUT_CSV}")


# =====================================
# MAIN
# =====================================


if __name__ == '__main__':
    app = App()
    app.mainloop()