CREATE DATABASE IF NOT EXISTS homework;

CREATE TABLE IF NOT EXISTS homework.transactions
(
    source_file LowCardinality(String),
    source_row UInt64 CODEC(Delta, ZSTD(1)),
    transaction_time DateTime('UTC') CODEC(Delta, ZSTD(1)),
    merch LowCardinality(String),
    cat_id LowCardinality(String),
    amount Decimal(18, 2) CODEC(ZSTD(1)),
    name_1 String CODEC(ZSTD(1)),
    name_2 String CODEC(ZSTD(1)),
    gender LowCardinality(String),
    street String CODEC(ZSTD(1)),
    one_city LowCardinality(String),
    us_state LowCardinality(String),
    post_code String CODEC(ZSTD(1)),
    lat Float64,
    lon Float64,
    population_city UInt32,
    jobs LowCardinality(String),
    merchant_lat Float64,
    merchant_lon Float64,
    target Nullable(UInt8),
    PROJECTION state_max
    (
        SELECT us_state, argMax(cat_id, tuple(amount, cat_id)), max(amount)
        GROUP BY us_state
    )
)
ENGINE = MergeTree
ORDER BY (us_state, transaction_time);

