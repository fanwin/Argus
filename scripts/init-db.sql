-- 初始化数据库脚本
-- 用于创建测试所需的数据库表和初始数据

-- 创建测试用户表
CREATE TABLE IF NOT EXISTS test_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建测试产品表
CREATE TABLE IF NOT EXISTS test_products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    category VARCHAR(100),
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建测试订单表
CREATE TABLE IF NOT EXISTS test_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES test_users(id),
    total_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipping_address TEXT,
    notes TEXT
);

-- 创建测试订单项表
CREATE TABLE IF NOT EXISTS test_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES test_orders(id),
    product_id INTEGER REFERENCES test_products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2)
);

-- 创建测试日志表
CREATE TABLE IF NOT EXISTS test_logs (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255),
    test_status VARCHAR(50),
    execution_time DECIMAL(10, 3),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试用户数据
INSERT INTO test_users (username, email, password_hash, first_name, last_name, role) VALUES
('admin', 'admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Admin', 'User', 'admin'),
('testuser1', 'user1@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Test', 'User1', 'user'),
('testuser2', 'user2@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Test', 'User2', 'user'),
('manager', 'manager@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Test', 'Manager', 'manager')
ON CONFLICT (username) DO NOTHING;

-- 插入测试产品数据
INSERT INTO test_products (name, description, price, category, stock_quantity) VALUES
('测试产品1', '这是一个测试产品的描述', 99.99, '电子产品', 100),
('测试产品2', '另一个测试产品', 149.99, '家居用品', 50),
('测试产品3', '第三个测试产品', 79.99, '服装', 200),
('测试产品4', '第四个测试产品', 199.99, '电子产品', 30),
('测试产品5', '第五个测试产品', 59.99, '图书', 150)
ON CONFLICT DO NOTHING;

-- 插入测试订单数据
INSERT INTO test_orders (user_id, total_amount, status, shipping_address) VALUES
(2, 99.99, 'completed', '测试地址1号'),
(3, 229.98, 'pending', '测试地址2号'),
(2, 79.99, 'shipped', '测试地址3号'),
(4, 259.98, 'completed', '测试地址4号')
ON CONFLICT DO NOTHING;

-- 插入测试订单项数据
INSERT INTO test_order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 99.99, 99.99),
(2, 1, 1, 99.99, 99.99),
(2, 2, 1, 149.99, 149.99),
(3, 3, 1, 79.99, 79.99),
(4, 4, 1, 199.99, 199.99),
(4, 5, 1, 59.99, 59.99)
ON CONFLICT DO NOTHING;

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_test_users_email ON test_users(email);
CREATE INDEX IF NOT EXISTS idx_test_users_username ON test_users(username);
CREATE INDEX IF NOT EXISTS idx_test_products_category ON test_products(category);
CREATE INDEX IF NOT EXISTS idx_test_orders_user_id ON test_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_test_orders_status ON test_orders(status);
CREATE INDEX IF NOT EXISTS idx_test_order_items_order_id ON test_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_test_order_items_product_id ON test_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_test_logs_test_name ON test_logs(test_name);
CREATE INDEX IF NOT EXISTS idx_test_logs_created_at ON test_logs(created_at);

-- 创建视图用于测试查询
CREATE OR REPLACE VIEW user_order_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    COUNT(o.id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_spent,
    MAX(o.order_date) as last_order_date
FROM test_users u
LEFT JOIN test_orders o ON u.id = o.user_id
GROUP BY u.id, u.username, u.email;

-- 创建存储过程用于测试
CREATE OR REPLACE FUNCTION get_user_orders(user_id_param INTEGER)
RETURNS TABLE(
    order_id INTEGER,
    total_amount DECIMAL(10,2),
    status VARCHAR(50),
    order_date TIMESTAMP,
    product_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.id,
        o.total_amount,
        o.status,
        o.order_date,
        COUNT(oi.id) as product_count
    FROM test_orders o
    LEFT JOIN test_order_items oi ON o.id = oi.order_id
    WHERE o.user_id = user_id_param
    GROUP BY o.id, o.total_amount, o.status, o.order_date
    ORDER BY o.order_date DESC;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器用于更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为用户表添加更新时间戳触发器
DROP TRIGGER IF EXISTS update_test_users_updated_at ON test_users;
CREATE TRIGGER update_test_users_updated_at
    BEFORE UPDATE ON test_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为产品表添加更新时间戳触发器
DROP TRIGGER IF EXISTS update_test_products_updated_at ON test_products;
CREATE TRIGGER update_test_products_updated_at
    BEFORE UPDATE ON test_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 输出初始化完成信息
DO $$
BEGIN
    RAISE NOTICE '数据库初始化完成！';
    RAISE NOTICE '创建了 % 个用户', (SELECT COUNT(*) FROM test_users);
    RAISE NOTICE '创建了 % 个产品', (SELECT COUNT(*) FROM test_products);
    RAISE NOTICE '创建了 % 个订单', (SELECT COUNT(*) FROM test_orders);
END $$;
