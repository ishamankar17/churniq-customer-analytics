SELECT current_database();

CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen INTEGER,
    partner VARCHAR(5),
    dependents VARCHAR(5),
    tenure INTEGER,
    phone_service VARCHAR(20),
    multiple_lines VARCHAR(30),
    internet_service VARCHAR(30),
    online_security VARCHAR(30),
    online_backup VARCHAR(30),
    device_protection VARCHAR(30),
    tech_support VARCHAR(30),
    streaming_tv VARCHAR(30),
    streaming_movies VARCHAR(30),
    contract VARCHAR(30),
    paperless_billing VARCHAR(5),
    payment_method VARCHAR(50),
    monthly_charges NUMERIC(10,2),
    total_charges NUMERIC(12,2),
    churn VARCHAR(5)
);

SELECT COUNT(*) FROM customers;

SELECT COUNT(*) AS total_customers
FROM customers;

SELECT *
FROM customers
LIMIT 5;

SELECT
    MIN(tenure) AS min_tenure,
    MAX(tenure) AS max_tenure,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(total_charges), 2) AS avg_total_charges
FROM customers;

-- 01. Overall customer churn rate

SELECT
    churn,
    COUNT(*) AS customers,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM customers
GROUP BY churn
ORDER BY customers DESC;

-- 02. Churn rate by contract type

SELECT
    contract,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate
FROM customers
GROUP BY contract
ORDER BY churn_rate DESC;

-- 03. Churn rate by tenure group

SELECT
    CASE
        WHEN tenure <= 12 THEN '0-1 Year'
        WHEN tenure <= 24 THEN '1-2 Years'
        WHEN tenure <= 48 THEN '2-4 Years'
        ELSE '4+ Years'
    END AS tenure_group,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate

FROM customers

GROUP BY
    CASE
        WHEN tenure <= 12 THEN '0-1 Year'
        WHEN tenure <= 24 THEN '1-2 Years'
        WHEN tenure <= 48 THEN '2-4 Years'
        ELSE '4+ Years'
    END

ORDER BY churn_rate DESC;

-- 05. Churn rate by payment method

SELECT
    payment_method,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate
FROM customers
GROUP BY payment_method
ORDER BY churn_rate DESC;

-- 06. Churn rate by senior citizen status

SELECT
    CASE
        WHEN senior_citizen = 1 THEN 'Senior Citizen'
        ELSE 'Non-Senior Citizen'
    END AS customer_group,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate

FROM customers

GROUP BY senior_citizen

ORDER BY churn_rate DESC;

-- 07. Churn rate by tech support

SELECT
    tech_support,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate
FROM customers
GROUP BY tech_support
ORDER BY churn_rate DESC;

-- 08. Churn rate by online security

SELECT
    online_security,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate
FROM customers
GROUP BY online_security
ORDER BY churn_rate DESC;

-- 09. Revenue comparison by churn status

SELECT
    churn,
    COUNT(*) AS customers,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(total_charges), 2) AS avg_total_charges,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue
FROM customers
GROUP BY churn;

-- 10. Churn rate by gender

SELECT
    gender,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE churn = 'Yes') / COUNT(*),
        2
    ) AS churn_rate
FROM customers
GROUP BY gender
ORDER BY churn_rate DESC;

-- 11. High-value customers who churned

SELECT
    customer_id,
    tenure,
    contract,
    monthly_charges,
    total_charges,
    internet_service,
    tech_support,
    payment_method
FROM customers
WHERE churn = 'Yes'
  AND monthly_charges >= 80
ORDER BY monthly_charges DESC;

-- 12. High-risk customer segment

SELECT
    customer_id,
    tenure,
    contract,
    monthly_charges,
    internet_service,
    online_security,
    tech_support,
    payment_method,
    churn
FROM customers
WHERE tenure <= 12
  AND contract = 'Month-to-month'
  AND churn = 'Yes'
ORDER BY monthly_charges DESC;

-- 13. Average tenure by churn status

SELECT
    churn,
    COUNT(*) AS customers,
    ROUND(AVG(tenure), 2) AS avg_tenure
FROM customers
GROUP BY churn;

