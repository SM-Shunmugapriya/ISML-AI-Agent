ALTER TABLE resources
ADD COLUMN IF NOT EXISTS review_status VARCHAR(20)
NOT NULL DEFAULT 'APPROVED';

ALTER TABLE resources
ADD COLUMN IF NOT EXISTS review_confidence FLOAT;

ALTER TABLE resources
ADD COLUMN IF NOT EXISTS review_comment TEXT;

ALTER TABLE resources
ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(100);

ALTER TABLE resources
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_resources_review_queue
ON resources (review_status, id);
