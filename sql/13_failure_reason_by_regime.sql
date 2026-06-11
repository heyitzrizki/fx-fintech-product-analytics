SELECT
    market_regime_at_transaction,
    failure_reason,
    COUNT(*) AS failed_transactions,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (
            PARTITION BY market_regime_at_transaction
        ),
        2
    ) AS share_within_regime

FROM transactions

WHERE transaction_type = 'exchange'
  AND transaction_status = 'failed'

GROUP BY
    market_regime_at_transaction,
    failure_reason

ORDER BY
    CASE market_regime_at_transaction
        WHEN 'low' THEN 1
        WHEN 'normal' THEN 2
        WHEN 'high' THEN 3
    END,
    failed_transactions DESC;









