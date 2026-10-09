ALTER TABLE resources
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

ALTER TABLE resources
ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMP;

ALTER TABLE resources
ADD COLUMN IF NOT EXISTS availability_status VARCHAR(20)
NOT NULL DEFAULT 'unknown';

UPDATE resources
SET updated_at = created_at
WHERE updated_at IS NULL;

ALTER TABLE resources
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE resources
ALTER COLUMN updated_at SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_resources_freshness
ON resources (last_verified_at, id);
