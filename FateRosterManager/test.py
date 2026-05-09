import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x200")

label = ctk.CTkLabel(app, text="GUI Works")
label.pack(pady=50)

app.mainloop()