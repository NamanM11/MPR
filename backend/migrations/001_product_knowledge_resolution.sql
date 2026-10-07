BEGIN;

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    brand TEXT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    attributes TEXT NOT NULL DEFAULT '{}',
    valid_variants TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE catalogs ADD COLUMN existing_product INTEGER NOT NULL DEFAULT 0;
ALTER TABLE catalogs ADD COLUMN matched_product_id TEXT;
ALTER TABLE catalogs ADD COLUMN variant_match INTEGER;
ALTER TABLE catalogs ADD COLUMN product_resolution_confidence REAL NOT NULL DEFAULT 0;
ALTER TABLE catalogs ADD COLUMN matched_variant TEXT;
ALTER TABLE catalogs ADD COLUMN requested_variant TEXT NOT NULL DEFAULT '{}';
ALTER TABLE catalogs ADD COLUMN resolution_reasons TEXT NOT NULL DEFAULT '[]';
ALTER TABLE catalogs ADD COLUMN resolution_method TEXT NOT NULL DEFAULT 'new_product';
ALTER TABLE catalogs ADD COLUMN seller_decision TEXT;

INSERT OR IGNORE INTO products (
    product_id, brand, product_name, category, subcategory, attributes, valid_variants
) VALUES (
    'IPHONE15',
    'Apple',
    'iPhone 15',
    'Electronics',
    'Mobile Phones',
    '{"model":"iPhone 15"}',
    '[{"storage":"128GB","color":"Black"},{"storage":"128GB","color":"Blue"},{"storage":"256GB","color":"Black"},{"storage":"512GB","color":"Pink"}]'
);

COMMIT;
