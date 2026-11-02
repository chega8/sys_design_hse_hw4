CREATE DATABASE IF NOT EXISTS transactions_db;

CREATE TABLE IF NOT EXISTS transactions_db.transactions
(
    source_file LowCardinality(String),
    source_row UInt64,
    transaction_time DateTime('UTC'),
    merch LowCardinality(String),
    cat_id LowCardinality(String),
    amount Decimal(18, 2),
    name_1 String,
    name_2 String,
    gender LowCardinality(String),
    street String,
    one_city LowCardinality(String),
    us_state LowCardinality(String),
    post_code String,
    lat Float64,
    lon Float64,
    population_city UInt32,
    jobs LowCardinality(String),
    merchant_lat Float64,
    merchant_lon Float64,
    target Nullable(UInt8)
)
ENGINE = MergeTree
ORDER BY (us_state, transaction_time);

