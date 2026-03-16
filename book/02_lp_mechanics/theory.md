# Layer 2: LP Mechanics — Impermanent Loss, Fees, Yield

---

## 1. Impermanent Loss — What It Is and When It Occurs

Impermanent loss (IL) is the difference in value between holding tokens in an AMM pool vs holding them in your wallet.

It occurs whenever the price of the pooled tokens changes relative to when you deposited. The more the price diverges, the greater the loss.

**Why it happens:** The AMM rebalances the pool automatically as price changes. When ETH goes up, arbitrageurs buy ETH from the pool (cheap relative to market), leaving the pool with less ETH and more USDC. You end up with less of the appreciating asset than if you had just held.

**Numeric example:**

You deposit: 1 ETH + 1,000 USDC into a pool (ETH price = $1,000). k = 1 * 1,000 = 1,000. Your deposit value = $2,000.

ETH price doubles to $2,000. Arbitrageurs rebalance the pool.

New pool state (derived from x*y=k and new price ratio):
- New ETH reserve: √(k / new_price) = √(1,000 / 2,000) = 0.707 ETH
- New USDC reserve: √(k * new_price) = √(1,000 * 2,000) = 1,414 USDC

Your pool value: 0.707 × $2,000 + $1,414 = $1,414 + $1,414 = **$2,828**

If you had just held: 1 ETH × $2,000 + $1,000 USDC = **$3,000**

**IL = $3,000 - $2,828 = $172 (5.7% loss)**

**IL by price change magnitude:**
| Price change | IL |
|---|---|
| 1.25x | 0.6% |
| 1.5x | 2.0% |
| 2x | 5.7% |
| 4x | 20.0% |
| 10x | 42.5% |

**Why "impermanent":** If price returns to the original ratio, IL disappears. It only becomes permanent when you withdraw at a different price ratio than deposit.

IL is not a cash loss — it's an opportunity cost. You still made money if fees > IL.

---

## 2. How LPs Earn Fees

Every swap in the pool charges a fee (0.3% in Uniswap V2, various tiers in V3). This fee stays in the pool, increasing the reserves — meaning k grows slightly after every trade.

**How you receive fees:** You don't get paid out directly. Your LP tokens represent a % share of the pool. As the pool's reserves grow from fees, your share is worth more. When you withdraw, you get your % of the now-larger pool.

**Example:**
Pool: 10 ETH + 10,000 USDC. You own 10% (1 ETH + 1,000 USDC worth).
After a day of trading, pool accumulates $50 in fees → pool grows.
Your 10% is now worth slightly more than 1 ETH + 1,000 USDC.

**Profitability = fees earned - impermanent loss**
- High-volume, low-volatility pools (e.g., USDC/USDT): lots of fees, almost zero IL → great
- Low-volume, high-volatility pools (e.g., new token/ETH): little fees, large IL → often unprofitable

---

## 3. Main Risks for Liquidity Providers

1. **Impermanent loss** — the primary economic risk, explained above
2. **Smart contract bugs** — the pool contract could be exploited, draining funds
3. **Admin key risk** — if the protocol has an owner key that can drain the pool or change fees
4. **Token risk** — if one of the pooled tokens goes to zero, you're left with only the worthless token
5. **Oracle manipulation** — some protocols use pool prices as oracles; manipulating the pool can break other protocols
6. **Rug pulls** — malicious projects that provide initial liquidity then drain it

**The biggest day-to-day risk is IL**, especially in volatile markets. Smart contract risk is rare but catastrophic when it happens.

---

## 4. Yield Farming

Yield farming is the practice of moving capital across DeFi protocols to maximize returns.

Protocols often need liquidity to bootstrap. They incentivize LPs with extra token rewards on top of trading fees. Yield farmers chase these incentives.

**Typical flow:**
1. Protocol launches a new pool and offers high token rewards to attract liquidity
2. Farmers deposit funds, earn both trading fees and governance tokens
3. Farmers sell the governance tokens immediately (often), creating sell pressure
4. Rewards decrease over time as more capital enters (dilution) or the protocol reduces emissions

**The APY problem:** Advertised yields are often not sustainable. A 1,000% APY in governance tokens is worth something today but depends entirely on the token price holding up.

---

## 5. APR vs APY

**APR (Annual Percentage Rate):** Simple interest, no compounding.
- If you earn 1% per month: APR = 12%

**APY (Annual Percentage Yield):** Compound interest — you reinvest earnings.
- If you earn 1% per month and compound: APY = (1 + 0.01)^12 - 1 = 12.68%

**In DeFi:**
- Protocols often display APY to make yields look higher
- Manual compounding (harvesting and re-depositing) costs gas — you have to weigh gas cost vs compounding benefit
- "Auto-compounding vaults" (like Yearn) do this automatically

The difference matters most at high rates: 100% APR = 172% APY if compounded daily.

---

## 6. Staking vs Yield Farming

| | Staking | Yield Farming |
|---|---|---|
| What you do | Lock tokens for a specific protocol function | Provide liquidity / lend / borrow to earn rewards |
| Purpose | Network security (PoS) or governance | Bootstrap protocol liquidity |
| Risk | Slashing (PoS), lock-up periods | IL, smart contract risk, token depreciation |
| Returns | Relatively stable, predictable | Highly variable, often unsustainable |
| Complexity | Low | High (chasing yields across protocols) |

**PoS staking** (e.g., ETH staking): you lock ETH to run a validator or delegate to one. You secure the network and earn ~3-4% APR in ETH rewards. No IL because you're not in a pool.

**Protocol staking** (e.g., staking AAVE in the safety module): you lock governance tokens as insurance against the protocol's shortfall events. Riskier — you can lose tokens if the protocol is exploited.

---

## 7. Liquidity Mining Incentives

Liquidity mining = a protocol distributing its own governance tokens to LPs as an additional reward on top of trading fees.

**Why protocols do it:** Cold-start problem. A new DEX or lending protocol needs liquidity to function. Without liquidity, swaps are expensive (high slippage) and the protocol is useless. Token rewards attract early liquidity.

**Example:** Compound launched "COMP" token distribution in 2020. Users supplying or borrowing assets earned COMP tokens. This triggered the "DeFi Summer" — TVL across DeFi exploded.

**Mechanics:**
- Protocol allocates a fixed number of tokens per block to a pool
- Tokens are distributed proportionally to LPs by their share
- As more capital enters, rewards per dollar dilute
- The emission schedule usually decreases over time

**Mercenary liquidity:** Farmers who leave the moment better rewards appear elsewhere. Protocols that rely solely on liquidity mining often see TVL collapse when emissions drop.
