SELECT
    market_regime_at_transaction,

    COUNT(*) AS transaction_attempts,

    SUM(
        CASE
            WHEN transaction_status = 'completed' THEN 1
            ELSE 0
        END
    ) AS successful_transactions,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN transaction_status = 'completed' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS success_rate,

    ROUND(
        AVG(transaction_amount_krw),
        0
    ) AS avg_transaction_amount_krw,

    ROUND(
        SUM(
            CASE
                WHEN transaction_status = 'completed'
                THEN transaction_amount_krw
                ELSE 0
            END
        ),
        0
    ) AS completed_volume_krw

FROM transactions

WHERE transaction_type = 'exchange'

GROUP BY market_regime_at_transaction

ORDER BY
    CASE market_regime_at_transaction
        WHEN 'low' THEN 1
        WHEN 'normal' THEN 2
        WHEN 'high' THEN 3
    END;









