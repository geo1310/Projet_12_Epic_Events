CREATE EXTENSION IF NOT EXISTS pgcrypto; -- Assurez-vous que l'extension pgcrypto est activée
-- 'bf' est utilisé pour l'algorithme Blowfish, qui est une méthode de hachage sécurisée
-- 'crypt' : Utilise la fonction de hachage cryptographique native du système d'exploitation.
-- 'xdes' : Utilise l'algorithme de hachage cryptographique XDES (DES étendu).
-- 'sha1', 'sha224', 'sha256', 'sha384', 'sha512' : Utilise les algorithmes de hachage SHA-1, SHA-224, SHA-256, SHA-384 et SHA-512, respectivement.

CREATE TABLE Employee (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('commercial', 'support', 'management')) NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des données dans la table Employee
INSERT INTO Employee (first_name, last_name, email, password_hash, type) VALUES
('Commercial_1', '', 'commercial_1@email.com', crypt('password123', gen_salt('bf')), 'commercial'),
('Support_1', '', 'support_1@email.com', crypt('password123', gen_salt('bf')), 'support'),
('Support_2', '', 'support_2@email.com', crypt('password123', gen_salt('bf')), 'support'),
('Management_1', '', 'management_1@email.com', crypt('password123', gen_salt('bf')), 'management');