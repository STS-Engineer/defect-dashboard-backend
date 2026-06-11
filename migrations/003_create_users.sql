CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  display_name VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (username, password, role, display_name) VALUES
('superviseur1', 'sup1pass', 'Superviseur', 'Superviseur_1'),
('superviseur2', 'sup2pass', 'Superviseur', 'Superviseur_2'),
('superviseur3', 'sup3pass', 'Superviseur', 'Superviseur_3'),
('superviseur4', 'sup4pass', 'Superviseur', 'Superviseur_4'),
('dataentry1', 'entry1pass', 'Data Entry', 'DataEntry_1'),
('dataentry2', 'entry2pass', 'Data Entry', 'DataEntry_2'),
('resp.prod', 'prodpass', 'Responsable Production', 'Resp. Production'),
('resp.qualite', 'qualpass', 'Responsable Qualite', 'Resp. Qualité')
ON CONFLICT (username) DO UPDATE SET
  password = EXCLUDED.password,
  role = EXCLUDED.role,
  display_name = EXCLUDED.display_name,
  is_active = true;
