-- Migration 009: Corrige constraint UNIQUE para incluir o campo status
-- Permite ter o mesmo dia/estabelecimento com status diferentes (projetado e recebido)

-- Remove a constraint antiga
ALTER TABLE dbo.recebiveis_cartao
DROP CONSTRAINT UQ_recebiveis_cartao_data_mes_estab;

-- Cria nova constraint incluindo o status
ALTER TABLE dbo.recebiveis_cartao
ADD CONSTRAINT UQ_recebiveis_cartao_data_mes_estab_status
UNIQUE (data_recebimento, mes_referencia, estabelecimento, status);
