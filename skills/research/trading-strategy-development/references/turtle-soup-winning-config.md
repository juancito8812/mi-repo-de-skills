# Turtle Soup + Breaker — Configuración Ganadora

Optimizada para NASDAQ (QQQ) en timeframe 1h.

## Parámetros

| Parámetro | Valor | Explicación |
|---|---|---|
| Timeframe | **1h** | Suficientes señales, buena estructura |
| Lookback | **20 velas** | ~20h de contexto para el swing |
| Mecha mínima | **0.5** (50% del body) | Filtra velas sin barrido real |
| Filtro tendencia (EMA20/50) | **OFF** | Destruye señales. Sin él: 20 trades vs 6 avg |
| TP | **ATR × 3.0** | Más amplio que el típico 1.5-2.0 |
| SL máximo | **3%** del precio de entrada | Protege capital |
| Hold máximo | **12h** (12 velas 1h) | Time exit si no se define |
| RR mínimo | **1.2** | Solo trades con reward decente |
| Riesgo por trade | **2%** de la cuenta | Gestión de capital |

## Resultados (QQQ 1h, Jul 2024 → May 2025)

| Métrica | Valor |
|---|---|
| Trades | 22 (~2/mes) |
| Win Rate | 41% (9W / 13L) |
| Profit Factor | 1.20 |
| P&L | +4.4% |
| Max DD | 9.6% |
| Avg Win | +$29.09 |
| Avg Loss | -$16.78 |
| BE rate | 50% (11/22) |
| LONG WR | 57% (+$60.06) |
| SHORT WR | 33% (-$16.37) |

## Por qué funciona

1. **Sin filtro EMA20/50**: el Turtle Soup es un patrón de reversión que no necesita confirmación de tendencia. El EMA filtra ~60% de señales y las que pasan tienen peor WR.
2. **ATR × 3.0**: el mercado necesita espacio para el movimiento post-breaker. TPs ajustados (×1.0-1.5) se comen el SL antes de llegar al target.
3. **Mecha 0.5**: garantiza que el barrido fue genuino, no una vela cuerpo-pequeño con sombra normal.
4. **Largos > Cortos**: NASDAQ tiene sesgo alcista estructural. Considerar solo señales LONG.

## Adaptación a crypto

No funcionó directamente en SPX/USDC:USDC de Hyperliquid (solo 17 días de datos 5m disponibles). La estrategia original depende de la sesión 9-10 AM NY que no existe en crypto 24/7. Para crypto:
- Usar Binance para datos históricos (precio IDEM)
- Timeframe 4H en BTC
- Sesiones clave como filtro (London Open 08:00 UTC, NY Open 13:00 UTC)

## Referencia: grid de optimización

```
product(
    [20, 30, 40, 60],     # lookback
    [2.0, 3.0, 4.0, 5.0], # atr_mult
    [1.0, 1.2],            # rr_min
    [2.0, 3.0],            # risk_max
    [72, 144],             # hold
)
```
