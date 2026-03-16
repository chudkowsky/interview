# Layer 8: Uniswap V3 — Concentrated Liquidity, Ticks, NFT Positions

---

## 1. Main Innovation in Uniswap V3 (vs V2)

The core innovation is **concentrated liquidity** — allowing LPs to provide liquidity within a specific price range, rather than across the entire price curve from 0 to ∞.

**V2 problem:** In Uniswap V2, your liquidity is spread uniformly across the entire x*y=k curve. In reality, most trading happens in a narrow price range around the current price. The vast majority of deposited capital is never used — it sits at extreme prices that are rarely reached. Capital efficiency is very low.

**V3 solution:** Let LPs choose a price range [Pa, Pb]. Their capital only participates in swaps when the current price is within that range. When the price is in range, they act like an extremely concentrated V2 pool — earning much higher fees per dollar deposited.

**Capital efficiency gain:** A V3 LP providing liquidity in the range [$1,900, $2,100] (a ±5% range around $2,000 ETH) can achieve the same depth as a V2 LP with ~20x more capital. The narrower the range, the greater the efficiency gain.

---

## 2. Concentrated Liquidity — What It Is

Instead of the full x*y=k curve, V3 uses a "virtual" version where your liquidity only covers a range.

**Visualization:**

```
Price
 ↑
 |        [====LP position====]
 |   ·····|                   |·····
 |         Pa                Pb
 +----------------------------------→ Price
           Current price range
```

- Below Pa: LP position is 100% in token A (e.g., all USDC). Earns no fees.
- Between Pa and Pb: LP position is a mix of A and B. Earns fees on every swap.
- Above Pb: LP position is 100% in token B (e.g., all ETH). Earns no fees.

**Why this matters:**
- Within the range, every dollar works as if it were in a much deeper pool
- Fees per dollar deposited are much higher
- But: if the price leaves your range, you earn nothing and must manually rebalance

---

## 3. Why Concentrated Liquidity Improves Capital Efficiency

**Intuition:** In V2, your $2,000 deposit earns fees on every trade from $0 to ∞. But 99% of trades happen between $1,000 and $3,000. Your capital sitting at extreme prices is wasted.

**V3:** Put all $2,000 in the range [$1,900, $2,100]. Now 100% of your capital earns fees on trades in that range. For trades in that range, your $2,000 behaves like $40,000 in V2 (rough 20x).

**Formula for capital efficiency gain:**
For a range [Pa, Pb] around current price P:
```
Efficiency multiplier ≈ sqrt(P) / (sqrt(P) - sqrt(Pa))   (simplified)
```

Narrow range = higher multiplier = higher fee earnings per dollar = higher risk of going out of range.

**Real-world example:** USDC/USDT (stablecoin pair) is often within ±0.1% of $1. A V3 LP can concentrate in [$0.999, $1.001] and achieve 1000x+ capital efficiency vs V2. This is why stablecoin DEX volume migrated heavily to V3.

---

## 4. Price Range Positions

When you provide liquidity to V3, you specify:
- **Token pair** (e.g., ETH/USDC)
- **Fee tier** (0.05%, 0.3%, or 1%)
- **Lower tick** (lower bound of price range)
- **Upper tick** (upper bound of price range)
- **Amount of tokens** to deposit

The pool calculates how much of each token to accept based on:
- Current price
- Your specified range
- Amount you want to deposit

**If current price is in the middle of your range:**
You deposit both tokens in the ratio that matches the current price.

**If current price is below your range (below Pa):**
You deposit 100% token A (e.g., USDC). The position acts as a limit buy order for token B.

**If current price is above your range (above Pb):**
You deposit 100% token B (e.g., ETH). The position acts as a limit sell order.

---

## 5. What Happens When Price Moves Outside a Range

**Below Pa:** The LP's position has been fully converted to token A (e.g., USDC). The LP now holds all USDC and no ETH. This is the maximum impermanent loss for V3 — you've been "sold out" of ETH as it fell through your range. Earning zero fees.

**Above Pb:** The LP's position has been fully converted to token B (e.g., ETH). The LP now holds all ETH and no USDC. You've been "bought out" of USDC as ETH rose through your range. Earning zero fees.

**Implication:** V3 positions are essentially **conditional limit orders** that convert from one token to another as price moves through the range. This is fundamentally different from V2 where you always hold a mix.

**Active management requirement:** V3 LPs must monitor positions and rebalance when price goes out of range. Otherwise, capital sits idle earning nothing. This is the main operational burden of V3 vs V2.

**JIT (Just-In-Time) liquidity:** A V3 MEV strategy where a bot adds a very narrow liquidity position in the same block as a large incoming swap, earns the fees from that single swap, then immediately removes liquidity. The bot "steals" fees from passive LPs for that trade.

---

## 6. Ticks — What They Are

Ticks are discrete price points that divide the price space into steps.

**Why discrete?** Real number prices would require infinite precision and infinite possible positions. Ticks discretize the price space into manageable increments.

**How ticks work:**
- Each tick corresponds to a price: `price = 1.0001^tick`
- Tick 0 = price 1.0
- Tick 1 = price 1.0001 (0.01% higher)
- Tick 100 = price ~1.01005 (1% higher)
- Tick -100 = price ~0.99005 (1% lower)

**Base:** 1.0001. Each tick is a 0.01% price increment. This gives fine-grained control — you can set ranges as narrow as 0.01%.

**Tick spacing:** Different fee tiers use different tick spacings to avoid unnecessary granularity:
- 0.05% pool: tick spacing = 10 (price steps of ~0.1%)
- 0.3% pool: tick spacing = 60 (price steps of ~0.6%)
- 1% pool: tick spacing = 200 (price steps of ~2%)

You can only set range boundaries at multiples of the tick spacing.

---

## 7. How Ticks Determine Price Ranges

When you create a V3 position, you specify a lower tick and upper tick. These translate to prices:

```
lower_price = 1.0001^lower_tick
upper_price = 1.0001^upper_tick
```

**Example:**
- You want to provide liquidity for ETH in the range $1,900–$2,100
- Current ETH price: $2,000. In the pool, ETH/USDC price is expressed as USDC per ETH.
- Lower tick for $1,900 ≈ tick -25,261 (math: log(1900) / log(1.0001))
- Upper tick for $2,100 ≈ tick -20,701

The pool stores your position as (lower_tick, upper_tick, liquidity_amount).

**The tick bitmap:** V3 maintains a bitmap of which ticks are "initialized" (have active liquidity). During a swap, the pool jumps from one initialized tick to the next, updating the active liquidity level as positions come in and out of range.

---

## 8. Why Discrete Ticks Are Necessary

**Mathematical reason:** The AMM formula in V3 is:
```
L = liquidity (constant within a range)
x = L / sqrt(P)
y = L * sqrt(P)
```

To transition between price ranges, the pool needs well-defined boundaries where liquidity changes. Continuous prices would make this computationally impossible.

**Gas efficiency:** The tick system lets the pool update only when a swap crosses a tick boundary. Within a range, the math is simple. At a boundary, the pool fetches the next active tick and adjusts liquidity accordingly.

**Practical reason:** Having a minimum price increment (0.01%) prevents the creation of dust positions at prices that differ by infinitesimal amounts, which would be exploitable.

**The sqrt(P) representation:** V3 stores prices as `sqrtPriceX96` — the square root of the price, scaled by 2^96 for precision. The square root is used because the liquidity math involves sqrt throughout, and it avoids square root computation during each swap step.

---

## 9. Fee Tiers in Uniswap V3 — Which Pool Uses Which

Three fee tiers exist (a fourth 0.01% was added later):

| Fee tier | Tick spacing | Best for |
|---|---|---|
| 0.05% (5 bps) | 10 | Stable pairs (USDC/USDT, WBTC/TBTC) |
| 0.3% (30 bps) | 60 | Standard volatile pairs (ETH/USDC) |
| 1% (100 bps) | 200 | Highly exotic / low-liquidity pairs |

**Why different tiers?**

- **Stable pairs:** Very little price movement → LPs have minimal IL risk → can afford to charge less to attract volume. Lower fee = more volume = more fee income for LPs even at lower rate.

- **Volatile pairs:** High price movement → more IL risk for LPs → need higher fee to compensate. A 0.05% fee on ETH/USDC would attract all the volume but LPs would lose money on IL.

- **Exotic pairs:** Very thin liquidity, high risk, wide spreads. 1% covers the risk premium and wide bid-ask spread.

**Multiple pools per pair:** Any pair can have multiple V3 pools at different fee tiers. Usually one tier dominates and attracts most of the volume (network effect). Aggregators route to whichever has the best price.

---

## 10. NFT Liquidity Positions

In Uniswap V2, LP tokens were fungible ERC-20 tokens. Every LP in a pool held the same type of token; positions were indistinguishable.

In V3, every LP position is unique (different price range, different liquidity amount, different tokens owed). **Fungible tokens can't represent this — so positions are represented as NFTs (ERC-721 tokens).**

Each NFT is a unique on-chain record encoding:
- The pool (token pair + fee tier)
- The lower and upper tick
- The liquidity amount
- Accumulated fees owed (tracked separately for each position)

---

## 11. Why LP Positions Are NFTs

**V2:** All LPs in a pool have identical positions (spread across the full curve). The LP token is fungible — 1 LP token = 1/N share of the entire pool. Simple.

**V3:** Two LPs in the same pool with different ranges have fundamentally different positions. LP Alice [1900, 2100] and LP Bob [1800, 2200] are not the same thing — they earn fees at different times, have different IL profiles, different amounts of each token.

**Why NFT:**
- Each position needs unique data storage (ticks, liquidity amount, fees owed per token)
- NFTs allow positions to be transferred, sold, or used as collateral in other protocols
- You can have multiple positions in the same pool — each is a separate NFT

**Trade-off:** NFT positions are less composable than fungible tokens. V2 LP tokens could easily be deposited into yield farming contracts that accepted any amount of the same token. V3 NFTs require specialized integrations.

---

## 12. Uniswap V3 vs V2: Impermanent Loss

**V3 IL is more severe within range but bounded by the range:**

- **V2:** IL is spread across the full price range. A 2x price move = 5.7% IL (same as Layer 2 example).
- **V3 (in range):** A 2x price move within a narrow range can completely convert your position to the underperforming asset. Within range, IL is amplified by the concentration factor.
- **V3 (out of range):** Once price exits the range, your position is fully converted and doesn't change further. You hold 100% of the worse-performing asset at that moment. IL is "locked in" until you rebalance.

**Practical implication:** V3 LPs bear more risk of concentrated IL in exchange for higher fee income. Active management (adjusting ranges as price moves) is the only mitigation.

**V3 can reduce IL compared to V2 if:**
- You set a very wide range (approaches V2 behavior)
- The price stays in your range
- High fee income offsets the amplified IL

---

## 13. Why V3 Requires Active Liquidity Management

**In V2:** Set and forget. Your liquidity always earns fees regardless of price. Capital efficiency is low but management effort is zero.

**In V3:** If price exits your range:
- You earn zero fees
- Your capital is idle
- You're fully exposed to the underperforming asset
- You must manually remove liquidity, rebalance tokens, and create a new position — paying gas each time

**The management loop:**
1. Set range (e.g., ±10% around current price)
2. Price moves, approaches edge of range
3. Decide: wait for reversion, or rebalance now?
4. Remove liquidity (gas), swap to rebalance token ratio (gas + slippage), add new position (gas)
5. Repeat

**Gas costs of rebalancing:** On Ethereum mainnet, each rebalance costs ~$30–100 in gas. For small positions, rebalancing may not be profitable. This is why V3 is dominated by large players and automated strategies.

**Automated vault strategies (Gamma, Arrakis, Sommelier):** Protocols that automatically manage V3 positions for users, handling rebalancing and compounding in exchange for a management fee.

---

## 14. How Arbitrageurs Keep Pool Prices Aligned

**The mechanism:** When a large trade on V3 moves the pool price away from the broader market price, arbitrageurs immediately trade in the opposite direction to capture the price difference. This restores the pool price.

**Example:**
- V3 pool: ETH/USDC at $2,000
- A whale sells 500 ETH in the pool → price moves down to $1,950
- Arbitrageur sees: V3 ETH is $1,950, but Binance has ETH at $2,000
- Arbitrageur buys ETH on V3 ($1,950) and sells on Binance ($2,000)
- Each buy pushes the V3 price back up
- Arbitrage continues until V3 ≈ Binance price

**This is beneficial:** Without arbitrageurs, V3 pools would drift from market prices after every significant trade. Users would get systematically worse prices.

**MEV connection:** In V3 specifically, arbitrage is often captured by MEV bots back-running large swaps in the same block. They add their arbitrage tx immediately after the trade tx, restoring the price within the same block.

**Tick crossings during arbitrage:** If a large arbitrage trade crosses multiple tick boundaries, the pool's active liquidity changes at each crossing. The bot must simulate these tick transitions to calculate the exact profit.
