WITH regime_hours AS (
    SELECT
        market_regime,
        COUNT(*) AS regime_hour_rows
    FROM fx_rates_hourly
    GROUP BY market_regime
),

transaction_regime AS (
    SELECT
        market_regime_at_transaction AS market_regime,
        COUNT(*) AS transaction_attempts,
        SUM(
            CASE
                WHEN transaction_status = 'completed' THEN 1
                ELSE 0
            END
        ) AS successful_transactions
    FROM transactions
    WHERE transaction_type = 'exchange'
    GROUP BY market_regime_at_transaction
)

SELECT
    tr.market_regime,
    rh.regime_hour_rows,
    tr.transaction_attempts,
    tr.successful_transactions,

    ROUND(
        1.0 * tr.transaction_attempts / rh.regime_hour_rows,
        2
    ) AS attempts_per_regime_hour,

    ROUND(
        1.0 * tr.successful_transactions / rh.regime_hour_rows,
        2
    ) AS successful_transactions_per_regime_hour

FROM transaction_regime tr

JOIN regime_hours rh
    ON tr.market_regime = rh.market_regime

ORDER BY
    CASE tr.market_regime
        WHEN 'low' THEN 1
        WHEN 'normal' THEN 2
        WHEN 'high' THEN 3
    END;









