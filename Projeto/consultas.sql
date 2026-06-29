-- 1. Ver todos os usuários
SELECT * FROM usuarios;

-- 2. Ver todas as quadras
SELECT * FROM quadras;

-- 3. Ver todos os agendamentos
SELECT * FROM agendamentos;

-- 4. Agendamentos com nome do usuário (JOIN)
SELECT u.nome, u.email, a.data, a.horario, a.quadra_nome
FROM agendamentos a
JOIN usuarios u ON a.usuario_id = u.id;

-- 5. Quantos agendamentos cada usuário fez
SELECT u.nome, COUNT(a.id) as total_agendamentos
FROM usuarios u
LEFT JOIN agendamentos a ON u.id = a.usuario_id
GROUP BY u.id;

-- 6. Quadras mais populares
SELECT quadra_nome, COUNT(*) as reservas
FROM agendamentos
GROUP BY quadra_nome
ORDER BY reservas DESC;

-- 7. Faturamento total por quadra
SELECT quadra_nome, SUM(valor_total) as faturamento
FROM agendamentos
GROUP BY quadra_nome;