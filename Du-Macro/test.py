import tkinter as tk
from tkinter import ttk

# ======= FUNÇÃO PARA JANELA DE CAPTURA =======
def abrir_janela_captura():
    captura = tk.Toplevel(root)
    captura.title("Selecionar região")
    captura.geometry("300x200+200+200")
    captura.configure(bg='#000000')
    captura.attributes('-alpha', 0.3)
    captura.overrideredirect(True)
    captura.lift()

    # Fechar ao pressionar ESC
    captura.bind("<Escape>", lambda e: captura.destroy())

    # ========== ARRASTE MANUAL ==========
    def iniciar_arraste(event):
        captura.x = event.x
        captura.y = event.y

    def durante_arraste(event):
        x = captura.winfo_pointerx() - captura.x
        y = captura.winfo_pointery() - captura.y
        captura.geometry(f"+{x}+{y}")

    captura.bind("<Button-1>", iniciar_arraste)
    captura.bind("<B1-Motion>", durante_arraste)

    # ===== QUADRO PRINCIPAL =====
    borda = tk.Frame(captura, bg="gray", bd=2)
    borda.pack(expand=True, fill="both")

    # ========== REDIMENSIONAMENTO ==========
    def iniciar_resize(event):
        captura.start_width = captura.winfo_width()
        captura.start_height = captura.winfo_height()
        captura.start_x = event.x_root
        captura.start_y = event.y_root

    def durante_resize(event):
        delta_x = event.x_root - captura.start_x
        delta_y = event.y_root - captura.start_y

        new_width = max(100, captura.start_width + delta_x)
        new_height = max(100, captura.start_height + delta_y)

        captura.geometry(f"{new_width}x{new_height}")

    resize_grip = tk.Frame(captura, bg="white", cursor="bottom_right_corner")
    resize_grip.place(relx=1.0, rely=1.0, anchor="se", width=15, height=15)
    resize_grip.bind("<Button-1>", iniciar_resize)
    resize_grip.bind("<B1-Motion>", durante_resize)


# ======= FUNÇÃO PARA ADICIONAR CONDIÇÃO =======
def adicionar_condicao():
    valor_spin = condition_spin.get()
    texto_entry = condition_entry.get()
    print(f"Condição adicionada: {valor_spin}x {texto_entry}")


# ======= JANELA PRINCIPAL =======
root = tk.Tk()
root.title("Macro OverLord")
root.geometry("950x400")
root.configure(bg='#1a1a1a')
root.resizable(False, False)

# ======= FRAME PRINCIPAL ESQUERDA =======
frame_left = tk.Frame(root, bg="#1a1a1a", bd=1, relief="flat")
frame_left.place(x=10, y=10, width=600, height=380)

# Título
title = tk.Label(frame_left, text="Macro OverLord", font=("Segoe UI", 14, "bold"), fg="white", bg="#1a1a1a")
title.place(x=0, y=0)

# Seletor de condição
condition_label = tk.Label(frame_left, text="[Condition List]", fg="#808080", bg="#1a1a1a", font=("Segoe UI", 9))
condition_label.place(x=130, y=2)

for i in range(6):
    rb = tk.Radiobutton(frame_left, text=str(i), value=i, bg="#1a1a1a", fg="white",
                        activebackground="#1a1a1a", selectcolor="#1a1a1a")
    rb.place(x=240 + i * 30, y=2)

# ======= REGIÃO DE CAPTURA =======
capture_region = tk.LabelFrame(frame_left, text="( Regioão de captura )", fg="gray", bg="#1a1a1a",
                               font=("Segoe UI", 8))
capture_region.place(x=0, y=250, width=320, height=100)

btn_captura = tk.Button(frame_left, text="Selecionar região", command=abrir_janela_captura,
                        bg="#2e2e2e", fg="white", font=("Segoe UI", 8))
btn_captura.place(x=100, y=230)

for i in range(3):
    cb = tk.Checkbutton(capture_region, bg="#1a1a1a", activebackground="#1a1a1a")
    cb.place(x=40 + i * 60, y=30)

# ======= EQUIPAMENTO =======
equipment_frame = tk.LabelFrame(frame_left, text="Equipment must have :", fg="white", bg="#1a1a1a",
                                font=("Segoe UI", 9, "bold"))
equipment_frame.place(x=330, y=30, width=260, height=320)

error_label = tk.Label(equipment_frame, text="Add at least one condition to be matched:", fg="red",
                       bg="#1a1a1a", font=("Segoe UI", 9))
error_label.place(x=5, y=10)

condition_spin = tk.Spinbox(equipment_frame, from_=1, to=10, width=3)
condition_spin.place(x=10, y=40)

condition_entry = ttk.Entry(equipment_frame, width=20)
condition_entry.place(x=50, y=40)

add_button = tk.Button(equipment_frame, text="+", width=2, command=adicionar_condicao)
add_button.place(x=210, y=38)

# ======= FRAME DIREITA =======
frame_right = tk.Frame(root, bg="#101010")
frame_right.place(x=620, y=10, width=320, height=380)

logo = tk.Label(frame_right, text="OverLord", font=("Segoe UI", 20, "bold"), fg="white", bg="#101010")
logo.place(x=130, y=50)

preview_var = tk.BooleanVar()
preview_check = tk.Checkbutton(frame_right, text="Preview (no rolls | OCR only)", variable=preview_var,
                               fg="white", bg="#101010", selectcolor="#101010", activebackground="#101010")
preview_check.place(x=60, y=250)

start_button = tk.Button(frame_right, text="Start", bg="#1a1a1a", fg="white", font=("Segoe UI", 10, "bold"),
                         width=10)
start_button.place(x=110, y=300)

# ======= LOOP PRINCIPAL =======
root.mainloop()
