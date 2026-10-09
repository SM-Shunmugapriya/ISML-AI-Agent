ALTER TABLE resources
ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'DISCOVERED';

CREATE TABLE IF NOT EXISTS resource_lifecycle_events (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT
);

CREATE INDEX IF NOT EXISTS ix_resource_lifecycle_events_resource_id
ON resource_lifecycle_events (resource_id);
