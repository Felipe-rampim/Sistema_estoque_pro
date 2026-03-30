import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Database:
    def __init__(self):
        # Configurações básicas pegas do .env
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.database = os.getenv('DB_NAME')

        # Garante que o banco de dados exista antes de conectar totalmente
        self._verificar_banco()

        self.config = {
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'database': self.database
        }

    def _verificar_banco(self):
        """Tenta criar o banco de dados caso ele não exista no MySQL"""
        try:
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} DEFAULT CHARACTER SET utf8mb4")
            temp_conn.close()
        except mysql.connector.Error as err:
            print(f"Erro ao criar/verificar banco: {err}")

    def executar(self, query, params=None, fetch=False):
        try:
            conexao = mysql.connector.connect(**self.config)
            cursor = conexao.cursor(dictionary=True) 
            try:
                cursor.execute(query, params or ())
                resultado = cursor.fetchall() if fetch else None
                conexao.commit()
                return resultado
            finally:
                cursor.close()
                conexao.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro de Banco de Dados", f"Falha na conexão: {err}")
            return [] if fetch else None

class JanelaCategorias(tk.Toplevel):
    def __init__(self, parent, db, callback_ao_fechar):
        super().__init__(parent)
        self.db = db
        self.callback = callback_ao_fechar
        self.title("Gerenciar Categorias")
        self.geometry("400x450")
        self.configure(bg="#f0f2f5")
        self.grab_set() 

        tk.Label(self, text="Nova Categoria:", bg="#f0f2f5", font=("Arial", 10, "bold")).pack(pady=10)
        self.ent_categoria = tk.Entry(self, width=30)
        self.ent_categoria.pack(pady=5)

        tk.Button(self, text="➕ Adicionar Categoria", bg="#28a745", fg="white", 
                  font=("Arial", 9, "bold"), command=self.adicionar_categoria).pack(pady=10)

        colunas = ("ID", "Nome")
        self.tree_cat = ttk.Treeview(self, columns=colunas, show="headings", height=10)
        self.tree_cat.heading("ID", text="ID")
        self.tree_cat.heading("Nome", text="Nome")
        self.tree_cat.column("ID", width=50, anchor="center")
        self.tree_cat.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Button(self, text="🗑️ Excluir Selecionada", bg="#dc3545", fg="white", 
                  command=self.excluir_categoria).pack(pady=10)

        self.listar_categorias()

    def listar_categorias(self):
        for i in self.tree_cat.get_children(): self.tree_cat.delete(i)
        res = self.db.executar("SELECT * FROM categorias", fetch=True)
        if res:
            for r in res: self.tree_cat.insert("", "end", values=(r['id'], r['nome']))

    def adicionar_categoria(self):
        nome = self.ent_categoria.get().strip()
        if nome:
            self.db.executar("INSERT INTO categorias (nome) VALUES (%s)", (nome,))
            self.ent_categoria.delete(0, tk.END)
            self.listar_categorias()
            self.callback() 
        else:
            messagebox.showwarning("Aviso", "Digite o nome da categoria!")

    def excluir_categoria(self):
        sel = self.tree_cat.selection()
        if not sel: 
            messagebox.showwarning("Aviso", "Selecione uma categoria!")
            return
        
        dados = self.tree_cat.item(sel[0])['values']
        id_cat_excluir = dados[0]
        
        if id_cat_excluir == 1:
            messagebox.showwarning("Aviso", "A categoria 'Geral' é protegida!")
            return

        if messagebox.askyesno("Confirmar", "Excluir categoria? Produtos serão movidos para 'Geral'."):
            self.db.executar("UPDATE produtos SET categoria_id = 1 WHERE categoria_id = %s", (id_cat_excluir,))
            self.db.executar("DELETE FROM categorias WHERE id = %s", (id_cat_excluir,))
            self.listar_categorias()
            self.callback()

class EstoqueApp:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("Sistema de Estoque Pro v2.0")
        self.root.geometry("850x600")
        self.root.configure(bg="#f0f2f5")
        
        self.id_selecionado = None
        self.mapa_categorias = {}
        
        self.setup_ui()
        self.carregar_categorias()
        self.atualizar_tabela()

    def setup_ui(self):
        # Cabeçalho
        header = tk.Frame(self.root, bg="#1a73e8", height=60)
        header.pack(fill="x")
        tk.Label(header, text="GERENCIAMENTO DE INVENTÁRIO", fg="white", 
                 bg="#1a73e8", font=("Segoe UI", 14, "bold")).pack(pady=15)

        # Formulário
        frame_corpo = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        frame_corpo.pack(fill="x")

        tk.Label(frame_corpo, text="Produto:", bg="#f0f2f5").grid(row=0, column=0, sticky="w")
        self.ent_nome = tk.Entry(frame_corpo, width=30)
        self.ent_nome.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(frame_corpo, text="Categoria:", bg="#f0f2f5").grid(row=0, column=1, sticky="w")
        self.cb_categoria = ttk.Combobox(frame_corpo, state="readonly", width=20)
        self.cb_categoria.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_corpo, text="Preço (R$):", bg="#f0f2f5").grid(row=0, column=2, sticky="w")
        self.ent_preco = tk.Entry(frame_corpo, width=15)
        self.ent_preco.grid(row=1, column=2, padx=5, pady=5)

        tk.Label(frame_corpo, text="Qtd Atual:", bg="#f0f2f5").grid(row=0, column=3, sticky="w")
        self.ent_qtd = tk.Entry(frame_corpo, width=10)
        self.ent_qtd.grid(row=1, column=3, padx=5, pady=5)

        # Botões
        btn_frame = tk.Frame(self.root, bg="#f0f2f5")
        btn_frame.pack(pady=10)

        self.btn_salvar = tk.Button(btn_frame, text="💾 Salvar Produto", bg="#28a745", fg="white", 
                                    font=("Arial", 10, "bold"), padx=15, command=self.salvar)
        self.btn_salvar.pack(side="left", padx=5)

        tk.Button(btn_frame, text="✏️ Editar", bg="#ffc107", command=self.preparar_edicao).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ Excluir", bg="#dc3545", fg="white", command=self.deletar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🧹 Limpar", bg="#6c757d", fg="white", command=self.limpar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📁 Categorias", bg="#17a2b8", fg="white", command=self.abrir_categorias).pack(side="left", padx=5)

        # Tabela (Treeview)
        colunas = ("ID", "Nome", "Categoria", "Preço", "Estoque")
        self.tree = ttk.Treeview(self.root, columns=colunas, show="headings")
        
        larguras = {"ID": 50, "Nome": 250, "Categoria": 150, "Preço": 100, "Estoque": 80}
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=larguras.get(col, 100), anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)
        self.tree.tag_configure('alerta', background='#ffcccc', foreground='red')

    def carregar_categorias(self):
        res = self.db.executar("SELECT id, nome FROM categorias", fetch=True)
        self.mapa_categorias = {r['nome']: r['id'] for r in res} if res else {}
        self.cb_categoria['values'] = list(self.mapa_categorias.keys())

    def atualizar_tabela(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = """
            SELECT p.id, p.nome, COALESCE(c.nome, 'Geral') as cat, p.preco_venda, p.quantidade_atual 
            FROM produtos p 
            LEFT JOIN categorias c ON p.categoria_id = c.id
        """
        produtos = self.db.executar(query, fetch=True)
        if produtos:
            for p in produtos:
                tag = 'alerta' if p['quantidade_atual'] <= 5 else 'normal'
                preco = f"R$ {float(p['preco_venda']):.2f}"
                self.tree.insert("", "end", values=(p['id'], p['nome'], p['cat'], preco, p['quantidade_atual']), tags=(tag,))

    def salvar(self):
        try:
            nome = self.ent_nome.get()
            cat_id = self.mapa_categorias.get(self.cb_categoria.get(), 1)
            # Aceita ponto ou vírgula no preço
            preco = float(self.ent_preco.get().replace(',', '.'))
            qtd = int(self.ent_qtd.get())

            if self.id_selecionado:
                sql = "UPDATE produtos SET nome=%s, categoria_id=%s, preco_venda=%s, quantidade_atual=%s WHERE id=%s"
                self.db.executar(sql, (nome, cat_id, preco, qtd, self.id_selecionado))
            else:
                sql = "INSERT INTO produtos (nome, categoria_id, preco_venda, quantidade_atual) VALUES (%s, %s, %s, %s)"
                self.db.executar(sql, (nome, cat_id, preco, qtd))

            self.limpar()
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        except ValueError:
            messagebox.showerror("Erro", "Preço ou Quantidade inválidos!")

    def preparar_edicao(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])['values']
        self.limpar()
        self.id_selecionado = v[0]
        self.ent_nome.insert(0, v[1])
        self.cb_categoria.set(v[2])
        self.ent_preco.insert(0, str(v[3]).replace("R$ ", "").replace(",", "."))
        self.ent_qtd.insert(0, v[4])
        self.btn_salvar.config(text="✅ Atualizar Produto", bg="#007bff")

    def deletar(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "Deseja excluir este item?"):
            id_prod = self.tree.item(sel[0])['values'][0]
            self.db.executar("DELETE FROM produtos WHERE id=%s", (id_prod,))
            self.atualizar_tabela()

    def limpar(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_preco.delete(0, tk.END)
        self.ent_qtd.delete(0, tk.END)
        self.cb_categoria.set('')
        self.id_selecionado = None
        self.btn_salvar.config(text="💾 Salvar Produto", bg="#28a745")

    def abrir_categorias(self):
        JanelaCategorias(self.root, self.db, self.carregar_categorias)

if __name__ == "__main__":
    app_root = tk.Tk()
    EstoqueApp(app_root)
    app_root.mainloop()