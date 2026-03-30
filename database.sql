-- 1. CRIAÇÃO DO BANCO DE DADOS (Nome exato usado no seu Python)
CREATE DATABASE IF NOT EXISTS sistema_estoque_pro 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_general_ci;

USE sistema_estoque_pro;

-- 2. TABELA DE CATEGORIAS
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Garante que o ID 1 seja sempre 'Geral'
INSERT INTO categorias (id, nome) VALUES (1, 'Geral') 
ON DUPLICATE KEY UPDATE nome='Geral';

-- 3. TABELA DE FORNECEDORES
CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_empresa VARCHAR(150) NOT NULL,
    contato VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB;

-- Garante um fornecedor padrão para evitar erros de FK
INSERT INTO fornecedores (id, nome_empresa) VALUES (1, 'Fornecedor Geral')
ON DUPLICATE KEY UPDATE nome_empresa='Fornecedor Geral';

-- 4. TABELA DE PRODUTOS
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    preco_venda DECIMAL(10, 2) NOT NULL,
    quantidade_atual INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 5,
    categoria_id INT DEFAULT 1,
    fornecedor_id INT DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Configuração de integridade: se deletar a categoria, o produto vira 'Geral' (via Python) ou NULL
    CONSTRAINT fk_categoria FOREIGN KEY (categoria_id) 
        REFERENCES categorias(id) ON DELETE SET NULL,
        
    CONSTRAINT fk_fornecedor FOREIGN KEY (fornecedor_id) 
        REFERENCES fornecedores(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5. VIEW DE CONSULTA PARA A TREEVIEW
-- Esta View facilita muito a vida no Python, pois já traz os nomes em vez de IDs
CREATE OR REPLACE VIEW v_estoque_detalhado AS
SELECT 
    p.id, 
    p.nome, 
    COALESCE(c.nome, 'Sem Categoria') AS categoria, 
    COALESCE(f.nome_empresa, 'Sem Fornecedor') AS fornecedor, 
    p.preco_venda, 
    p.quantidade_atual, 
    p.estoque_minimo,
    CASE 
        WHEN p.quantidade_atual <= p.estoque_minimo THEN 'BAIXO'
        ELSE 'OK'
    END AS status
FROM produtos p
LEFT JOIN categorias c ON p.categoria_id = c.id
LEFT JOIN fornecedores f ON p.fornecedor_id = f.id;