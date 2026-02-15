"""Minimal GUI test to diagnose rendering issues."""

import sys
sys.path.insert(0, 'src')

import customtkinter as ctk

print("CustomTkinter version:", ctk.__version__)
print("Creating minimal test window...")

# Test 1: Absolute minimal CustomTkinter app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Test Window")
app.geometry("400x300")

# Add some widgets
label = ctk.CTkLabel(app, text="Test Label", font=("Arial", 20))
label.pack(pady=20)

button = ctk.CTkButton(app, text="Test Button")
button.pack(pady=20)

# Bring to front
app.lift()
app.attributes('-topmost', True)
app.after(100, lambda: app.attributes('-topmost', False))

print("Window created. If you can see a label and button, CustomTkinter works.")
print("If the window is blank, there's a CustomTkinter/Tcl issue.")

app.mainloop()
