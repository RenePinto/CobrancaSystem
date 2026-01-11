-- Schema PostgreSQL para consolidação e envio de cobranças
-- Requisitos: auditoria, reenvio, integridade referencial e suporte a integrações futuras.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Roles de acesso (admin, operadora etc.)
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE roles IS 'Perfis de acesso para usuários da aplicação.';

-- Usuários do sistema
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON UPDATE CASCADE,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    password_hash VARCHAR(255) NOT NULL,
    totp_secret VARCHAR(32),
    is_2fa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'Usuários autenticados no sistema de cobranças.';

-- Vendedores
CREATE TABLE vendors (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name)
);

COMMENT ON TABLE vendors IS 'Vendedores responsáveis por clientes.';

-- Diretoria (destinatários agregados)
CREATE TABLE directors (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name)
);

COMMENT ON TABLE directors IS 'Diretores/gestores que recebem relatórios consolidados.';

-- Clientes
CREATE TABLE clients (
    id BIGSERIAL PRIMARY KEY,
    legal_name VARCHAR(200) NOT NULL,
    trade_name VARCHAR(200),
    document VARCHAR(30),
    email VARCHAR(150),
    phone VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE clients IS 'Clientes finais com títulos a receber.';

-- Relacionamento cliente-vendedor (mapeamento N:N)
CREATE TABLE client_vendor_map (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    vendor_id BIGINT NOT NULL REFERENCES vendors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by BIGINT REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    UNIQUE (client_id, vendor_id)
);

COMMENT ON TABLE client_vendor_map IS 'Histórico de associação entre clientes e vendedores.';

-- Lotes de importação (Itaú, Conta Azul etc.)
CREATE TABLE import_batches (
    id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    source_reference VARCHAR(100),
    file_name VARCHAR(255),
    file_checksum VARCHAR(64),
    imported_by BIGINT REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_rows INTEGER NOT NULL DEFAULT 0,
    inserted_rows INTEGER NOT NULL DEFAULT 0,
    skipped_rows INTEGER NOT NULL DEFAULT 0
);

COMMENT ON TABLE import_batches IS 'Metadados dos lotes importados de planilhas ou APIs.';

-- Recebíveis consolidados
CREATE TABLE receivables (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    vendor_id BIGINT REFERENCES vendors(id) ON UPDATE CASCADE ON DELETE SET NULL,
    import_batch_id BIGINT REFERENCES import_batches(id) ON UPDATE CASCADE ON DELETE SET NULL,
    external_source VARCHAR(50) NOT NULL,
    external_id VARCHAR(100),
    title_number VARCHAR(100),
    description VARCHAR(255) NOT NULL,
    due_date DATE NOT NULL,
    amount_original NUMERIC(12, 2) NOT NULL,
    amount_open NUMERIC(12, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    issued_at DATE,
    paid_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (amount_original > 0),
    CHECK (amount_open >= 0)
);

COMMENT ON TABLE receivables IS 'Títulos consolidados para cobrança e relatórios.';
COMMENT ON COLUMN receivables.external_source IS 'Origem dos dados: ITAU, CONTA_AZUL etc.';
COMMENT ON COLUMN receivables.external_id IS 'Identificador no sistema externo para integrações futuras.';

-- Snapshots de relatórios (armazenam exatamente o que foi exportado/enviado)
CREATE TABLE report_snapshots (
    id BIGSERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    recipient_type VARCHAR(30) NOT NULL,
    recipient_value VARCHAR(150),
    filters_json JSONB,
    data_json JSONB NOT NULL,
    generated_by BIGINT REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE report_snapshots IS 'Dados congelados enviados em relatórios (snapshot imutável).';
COMMENT ON COLUMN report_snapshots.data_json IS 'Payload completo do relatório exportado/enviado.';

-- Arquivos gerados (CSV, XLSX, PDF etc.)
CREATE TABLE report_files (
    id BIGSERIAL PRIMARY KEY,
    snapshot_id BIGINT NOT NULL REFERENCES report_snapshots(id) ON UPDATE CASCADE ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_checksum VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE report_files IS 'Arquivos exportados para cada snapshot.';

-- Histórico de envios (suporta reenvio ilimitado)
CREATE TABLE delivery_history (
    id BIGSERIAL PRIMARY KEY,
    recipient VARCHAR(150) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    delivery_method VARCHAR(20) NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_by BIGINT REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    snapshot_id BIGINT NOT NULL REFERENCES report_snapshots(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE delivery_history IS 'Registro de envios de relatórios e reenvios.';

-- Índices recomendados
CREATE INDEX idx_clients_legal_name ON clients (legal_name);
CREATE INDEX idx_receivables_client ON receivables (client_id);
CREATE INDEX idx_receivables_vendor ON receivables (vendor_id);
CREATE INDEX idx_receivables_due_date ON receivables (due_date);
CREATE INDEX idx_receivables_source ON receivables (external_source);
CREATE INDEX idx_receivables_origin_title ON receivables (external_source, external_id);

-- Índices adicionais para auditoria/consulta
CREATE INDEX idx_delivery_history_snapshot ON delivery_history (snapshot_id);
CREATE INDEX idx_report_snapshots_created_at ON report_snapshots (created_at);
