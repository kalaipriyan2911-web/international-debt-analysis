-- International Debt Analysis
-- Database: international_debt_db

-- 1. Total records and missing values in 2024
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN `2024` IS NULL THEN 1 ELSE 0 END) AS missing_2024
FROM debt_data;

-- 2. Top 10 countries by record count
SELECT
    country_name,
    COUNT(*) AS record_count
FROM debt_data
GROUP BY country_name
ORDER BY record_count DESC
LIMIT 10;

-- 3. Number of unique debt indicators
SELECT
    COUNT(DISTINCT series_name) AS unique_indicators
FROM debt_data;
