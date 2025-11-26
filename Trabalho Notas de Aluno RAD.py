import sqlite3
import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

DB_NAME = "notas1.db"
TABLE_NAME = "notas"


# ---------------- BANCO DE DADOS ---------------- #
def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno TEXT NOT NULL,
            materia TEXT NOT NULL,
            nota REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def inserir_nota(aluno, materia, nota):
    conn = conectar()
    c = conn.cursor()
    c.execute(f"INSERT INTO {TABLE_NAME} (aluno, materia, nota) VALUES (?, ?, ?)", (aluno, materia, nota))
    conn.commit()
    conn.close()


def listar_notas():
    conn = conectar()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {TABLE_NAME}")
    dados = c.fetchall()
    conn.close()
    return dados


def atualizar_nota(id_nota, nova_nota):
    conn = conectar()
    c = conn.cursor()
    c.execute(f"UPDATE {TABLE_NAME} SET nota=? WHERE id=?", (nova_nota, id_nota))
    conn.commit()
    conn.close()


def deletar_nota(id_nota):
    conn = conectar()
    c = conn.cursor()
    c.execute(f"DELETE FROM {TABLE_NAME} WHERE id=?", (id_nota,))
    conn.commit()
    conn.close()


# ---------------- EXPORTAÇÃO / IMPORTAÇÃO ---------------- #
def exportar_csv():
    dados = listar_notas()
    with open("notas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Aluno", "Matéria", "Nota"])
        w.writerows(dados)
    messagebox.showinfo("Sucesso", "Exportado para notas.csv")


def exportar_json():
    dados = listar_notas()
    json_data = [{"id": d[0], "aluno": d[1], "materia": d[2], "nota": d[3]} for d in dados]

    with open("notas.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    messagebox.showinfo("Sucesso", "Exportado para notas.json")


# ---------------- GRÁFICO ---------------- #
def gerar_grafico():
    dados = listar_notas()

    if not dados:
        messagebox.showwarning("Aviso", "Nenhuma nota cadastrada!")
        return

    materias = [d[2] for d in dados]
    notas = [d[3] for d in dados]

    plt.figure(figsize=(8, 4))
    plt.bar(materias, notas)
    plt.title("Notas por Matéria")
    plt.xlabel("Matéria")
    plt.ylabel("Nota")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# ---------------- INTERFACE GRÁFICA ---------------- #
def interface():
    global entry_aluno, entry_materia, entry_nota, tabela

    root = tk.Tk()
    root.title("Sistema de Notas")
    root.geometry("800x600")

    # ------- CAMPOS DE ENTRADA ------- #
    frame_inputs = ttk.LabelFrame(root, text="Inserir Nota")
    frame_inputs.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_inputs, text="Aluno:").grid(row=0, column=0, padx=5, pady=5)
    entry_aluno = ttk.Entry(frame_inputs)
    entry_aluno.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_inputs, text="Matéria:").grid(row=0, column=2, padx=5, pady=5)
    entry_materia = ttk.Entry(frame_inputs)
    entry_materia.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(frame_inputs, text="Nota:").grid(row=0, column=4, padx=5, pady=5)
    entry_nota = ttk.Entry(frame_inputs)
    entry_nota.grid(row=0, column=5, padx=5, pady=5)

    def adicionar():
        aluno = entry_aluno.get()
        materia = entry_materia.get()
        nota = entry_nota.get()

        if aluno == "" or materia == "" or nota == "":
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            nota = float(nota)
        except:
            messagebox.showerror("Erro", "Nota inválida.")
            return

        inserir_nota(aluno, materia, nota)
        atualizar_tabela()

        entry_aluno.delete(0, tk.END)
        entry_materia.delete(0, tk.END)
        entry_nota.delete(0, tk.END)

    ttk.Button(frame_inputs, text="Adicionar", command=adicionar).grid(row=0, column=6, padx=10)

    # ------- TABELA ------- #
    frame_tabela = ttk.LabelFrame(root, text="Notas Cadastradas")
    frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Aluno", "Matéria", "Nota")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, anchor="center", width=150)

    tabela.pack(fill="both", expand=True)

    def on_select(event):
        item = tabela.selection()
        if item:
            valores = tabela.item(item)["values"]
            entry_aluno.delete(0, tk.END)
            entry_materia.delete(0, tk.END)
            entry_nota.delete(0, tk.END)
            entry_aluno.insert(0, valores[1])
            entry_materia.insert(0, valores[2])
            entry_nota.insert(0, valores[3])

    tabela.bind("<<TreeviewSelect>>", on_select)

    def atualizar_item():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma nota.")
            return

        valores = tabela.item(item)["values"]
        id_nota = valores[0]

        try:
            nova_nota = float(entry_nota.get())
        except:
            messagebox.showerror("Erro", "Nota inválida.")
            return

        atualizar_nota(id_nota, nova_nota)
        atualizar_tabela()

    def deletar_item():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma nota.")
            return

        id_nota = tabela.item(item)["values"][0]
        deletar_nota(id_nota)
        atualizar_tabela()

    # ------- BOTÕES ------- #
    frame_botoes = ttk.Frame(root)
    frame_botoes.pack(fill="x", padx=10, pady=5)

    ttk.Button(frame_botoes, text="Atualizar Nota Selecionada", command=atualizar_item).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botoes, text="Deletar Nota Selecionada", command=deletar_item).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botoes, text="Gerar Gráfico", command=gerar_grafico).grid(row=0, column=2, padx=5)

    # ------- ATUALIZAR TABELA ------- #
    def atualizar_tabela():
        tabela.delete(*tabela.get_children())
        for item in listar_notas():
            tabela.insert("", "end", values=item)

    atualizar_tabela()

    root.mainloop()


# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    criar_tabela()
    interface()
