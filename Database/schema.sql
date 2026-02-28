
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_name TEXT NOT NULL,
    whatsapp_number TEXT NOT NULL UNIQUE,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    address TEXT,
    store_type TEXT DEFAULT 'kirana',
    monthly_sales_volume TEXT,
    num_shelves INTEGER,
    primary_language TEXT DEFAULT 'hindi',
    product_categories TEXT,
    gst_number TEXT,
    referral_code TEXT,
    status TEXT DEFAULT 'active',
    total_scans INTEGER DEFAULT 0,
    shelf_health_score INTEGER DEFAULT 0,
    last_scan_at TIMESTAMPTZ,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stores_whatsapp ON stores(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_stores_pincode ON stores(pincode);
CREATE INDEX IF NOT EXISTS idx_stores_city ON stores(city);
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    status TEXT DEFAULT 'processing', -- processing, completed, failed
    shelf_health_score INTEGER,
    products_detected INTEGER DEFAULT 0,
    critical_items INTEGER DEFAULT 0,
    vision_summary JSONB,
    final_recommendation TEXT,
    voice_note_url TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_scans_store_id ON scans(store_id);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE TABLE IF NOT EXISTS detected_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    stock_level TEXT NOT NULL,
    quantity_estimate INTEGER,
    facing_correct BOOLEAN DEFAULT true,
    shelf_position TEXT,
    price_visible TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_scan_id ON detected_products(scan_id);
CREATE INDEX IF NOT EXISTS idx_products_store_id ON detected_products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_stock_level ON detected_products(stock_level);
CREATE INDEX IF NOT EXISTS idx_products_category ON detected_products(category);
CREATE TABLE IF NOT EXISTS debate_rounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT,
    confidence_score INTEGER,
    model_used TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_debates_scan_id ON debate_rounds(scan_id);
CREATE TABLE IF NOT EXISTS voice_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    audio_url TEXT,
    duration_seconds INTEGER,
    language TEXT DEFAULT 'hindi',
    text_content TEXT,
    delivered_via TEXT DEFAULT 'web', 
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_voice_scan_id ON voice_notes(scan_id);
CREATE INDEX IF NOT EXISTS idx_voice_store_id ON voice_notes(store_id);
CREATE TABLE IF NOT EXISTS product_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_name TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    subcategory TEXT,
    typical_mrp DECIMAL(10,2),
    barcode TEXT,
    is_fmcg BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS neighborhood_demand (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pincode TEXT NOT NULL,
    city TEXT,
    week_start DATE,
    total_stores_scanned INTEGER DEFAULT 0,
    top_categories JSONB DEFAULT '[]',
    stockout_products JSONB DEFAULT '[]',
    demand_signals JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_neighborhood_pincode ON neighborhood_demand(pincode);
CREATE INDEX IF NOT EXISTS idx_neighborhood_week ON neighborhood_demand(week_start DESC);
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID REFERENCES stores(id),
    whatsapp_number TEXT,
    direction TEXT NOT NULL,
    message_type TEXT,
    message_content TEXT,
    media_url TEXT,
    twilio_sid TEXT,
    status TEXT DEFAULT 'received',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wa_store_id ON whatsapp_messages(store_id);
CREATE INDEX IF NOT EXISTS idx_wa_created ON whatsapp_messages(created_at DESC);
ALTER TABLE stores ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE detected_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE debate_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE neighborhood_demand ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all for anon" ON stores FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON scans FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON detected_products FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON debate_rounds FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON voice_notes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON neighborhood_demand FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON product_catalog FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON whatsapp_messages FOR ALL USING (true) WITH CHECK (true);

INSERT INTO product_catalog (product_name, brand, category, typical_mrp) VALUES
('Parle-G Biscuits', 'Parle', 'Biscuits', 10),
('Maggi 2-Minute Noodles', 'Nestle', 'Instant Food', 14),
('Tata Salt', 'Tata', 'Staples', 24),
('Dettol Soap', 'Reckitt', 'Personal Care', 46),
('Colgate Max Fresh', 'Colgate', 'Personal Care', 89),
('Surf Excel', 'HUL', 'Cleaning', 45),
('Amul Butter', 'Amul', 'Dairy', 55),
('Kissan Jam', 'HUL', 'Spreads', 99),
('Haldiram Namkeen', 'Haldiram', 'Snacks', 30),
('Frooti', 'Parle Agro', 'Beverages', 15),
('Sunfeast Biscuits', 'ITC', 'Biscuits', 30),
('Britannia Bread', 'Britannia', 'Bakery', 45),
('Dove Soap', 'HUL', 'Personal Care', 80),
('Lay''s Chips', 'PepsiCo', 'Snacks', 20),
('Coca-Cola 500ml', 'Coca-Cola', 'Beverages', 40)
ON CONFLICT DO NOTHING;
