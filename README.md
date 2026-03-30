# 📦 Sistema de Estoque Pro

Sistema de gerenciamento de inventário desktop feito em Python com interface gráfica Tkinter e banco de dados MySQL. O objetivo é facilitar o controle de produtos em pequenos negócios, permitindo cadastrar itens, organizar por categorias e fornecedores, e monitorar o nível de estoque de forma simples e visual.

## Tecnologias

Python, Tkinter, MySQL, mysql-connector-python e python-dotenv.

## Como rodar

Clone o repositório e instale as dependências:

```bash
pip install mysql-connector-python python-dotenv
```

Crie um arquivo `.env` na raiz do projeto com as credenciais do seu banco de dados:

```env
DB_HOST=localhost
DB_USER=root
DB_PASS=sua_senha
DB_NAME=sistema_estoque_pro
```

Execute o `schema.sql` no MySQL para criar o banco e as tabelas:

```bash
mysql -u root -p < schema.sql
```

Depois é só rodar a aplicação:

```bash
python main.py
```

## Funcionalidades

Cadastro, edição e exclusão de produtos com nome, categoria, preço de venda e quantidade em estoque. Produtos com estoque igual ou abaixo do mínimo são destacados em vermelho automaticamente. Gerenciamento de categorias em janela separada, com a categoria "Geral" protegida contra exclusão. Ao remover uma categoria, os produtos vinculados são movidos automaticamente para "Geral". O sistema também possui tabela de fornecedores e uma view `v_estoque_detalhado` que exibe o status de cada produto (`OK` ou `BAIXO`). Aceita preço com vírgula ou ponto como separador decimal.

<img width="1638" height="884" alt="Image" src="https://github.com/user-attachments/assets/f6957a4d-a55e-4f56-8077-5e1e56d88c68" />

## Banco de Dados

O projeto possui três tabelas principais: `categorias`, `fornecedores` e `produtos`. A tabela de produtos se relaciona com as duas anteriores via chave estrangeira. Ao excluir uma categoria ou fornecedor, o campo correspondente no produto é definido como nulo automaticamente pelo banco.

## Observação

O arquivo `.env` contém dados sensíveis e não deve ser enviado ao repositório. Certifique-se de que ele está listado no `.gitignore`.
