SELECT TRUE
FROM dev_stg_adls.app_files.tb_controle
WHERE file_name = '<nome_arquivo>';

SELEC *
FROM clientes
WHERE idade > 18
ORDER BY nome



SELECT id nome email
FROM usuarios
WHERE ativo = 1
ORDER BY nome


SELECT *
FROM produtoss
WHERE preco > 10
ORDER BY preco


SELECT *
FROM vendas
WHERE data_venda >
ORDER BY data_venda


SELECT *
FROM dev_stg_raw.tabela_clientes
WHERE data_cadastro > '2024-01-01';



CREATE TABLE refined.tblClie (
    id INT,
    nome STRING,
    idade STRING,
    dtCad STRING
);



UPDATE t1
SET col1 = 'x'
WHERE col2 = 10;


CREATE TABLE producao_x.tabela_y AS
SELECT id, valor
FROM bronze_x.tabela_origem;


CREATE OR REPLACE TABLE refined.transacoes_limpo AS
SELECT
    user_id,
    valor,
    status
FROM bronze.transacoes; 


SELECT c.nome, t.valor
FROM clientes c
LEFT JOIN transacoes t ON c.id LIKE t.user_id;



CREATE TABLE refined.temp_abc123 AS
SELECT
    a,
    b,
    c
FROM trusted.base_eventos;



SELECT *
FROM trusted.clientes
WHERE idade > '18';


INSERT INTO refined.clientes_final
VALUES (1, 'João', 22, '2024-10-10');


CREATE TABLE refined.pedidos_brutos AS
SELECT *
FROM bronze.pedidos;


SELECT *
FROM (
    SELECT *
    FROM (
        SELECT *
        FROM trusted.eventos
    ) x
) y
WHERE tipo = 'A';


CREATE TABLE refined.relatorio_final AS
SELECT id, nome, CAST(valor AS STRING), CAST(data AS STRING)
FROM trusted.transacoes;



DELETE FROM refined.tabela_critica;


SELECT id, nome, RAND() AS score
FROM trusted.usuarios;


CREATE TABLE tabelaXYZ AS
SELECT * FROM refined.usuarios;


