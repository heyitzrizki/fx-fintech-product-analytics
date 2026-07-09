# Model Card: FX Volatility Readiness

## Purpose

Classify the next day's USD/KRW absolute-return regime as low, normal, or high to support staffing, transaction monitoring, rate-change messaging, and lifecycle campaign timing.

## Method

Daily lagged volatility and momentum features are derived from Yahoo Finance observations for `USDKRW=X`, `JPYKRW=X`, `EURKRW=X`, and `SGDKRW=X`. A fixed local cache makes the run reproducible. Regime thresholds or clusters are fitted on the training period only. The first 80% of dates train the model and the final 20% validate it.

## Interpretation

This is an operational readiness signal, not an exchange-rate, profit, or trading forecast. Macro F1 and balanced accuracy matter because the three regimes may not be equally common.

## Limitations

Yahoo Finance provides historical market observations, but data availability and adjustments depend on the provider. Operating outcomes in this project remain synthetic and are not causally linked to the predicted signal. Production evaluation should measure whether alerts improve staffing, support response, execution reliability, or communication timing.
