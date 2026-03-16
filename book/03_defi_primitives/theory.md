# Layer 3: DeFi Primitives — Lending, Flash Loans, Oracles, Stablecoins

---

## 1. Overcollateralization in DeFi Lending

In traditional finance, lenders assess creditworthiness — they trust you'll repay. In DeFi, there's no identity, no credit score, no legal recourse. The solution: **overcollateralization**.

You must deposit more collateral than you borrow.

**Example (Aave/Compound style):**
- You deposit 1 ETH worth $2,000
- The protocol allows you to borrow up to 80% of collateral value (LTV = 80%)
- You can borrow up to $1,600 USDC
- If ETH price drops, your collateral value drops — at some threshold, you get liquidated

**Why overcollateralize?** The protocol needs a buffer. If ETH drops 30%, your $2,000 collateral is now $1,400 — less than your $1,600 debt. Liquidation is triggered before this happens.

**Who uses it?** People who want liquidity without selling their assets (e.g., hold ETH long-term, borrow USDC to spend now, repay later).

---

## 2. Liquidation Thresholds — How They Are Determined

Each asset has two key parameters:
- **LTV (Loan-to-Value):** Max you can borrow relative to collateral. E.g., 80% for ETH.
- **Liquidation threshold:** The point at which liquidation is triggered. Always > LTV. E.g., 82.5% for ETH.

The gap between LTV and liquidation threshold gives users a small buffer after borrowing.

**Health Factor:**
```
Health Factor = (collateral value × liquidation threshold) / debt value
```
- Health Factor > 1 → safe
- Health Factor ≤ 1 → liquidatable

**Example:**
- ETH collateral: $2,000, liquidation threshold: 82.5%
- Debt: $1,600 USDC
- Health Factor = (2,000 × 0.825) / 1,600 = 1,650 / 1,600 = **1.03** (barely safe)

ETH drops to $1,900:
- Health Factor = (1,900 × 0.825) / 1,600 = 1,567 / 1,600 = **0.98** → liquidatable

---

## 3. A Liquidation Event — Step by Step

1. Health factor drops below 1 (collateral value too close to debt value)
2. A liquidator (bot watching on-chain data) detects the at-risk position
3. Liquidator calls `liquidate()` on the lending protocol
4. Liquidator repays some or all of the debt (using their own funds)
5. Liquidator receives the borrower's collateral at a **discount** (e.g., 5–10% below market price) — this is the liquidation bonus / incentive
6. Borrower's position is reduced or closed; any remaining collateral is returned

**Why liquidators are incentivized:** The 5–10% discount is profit. Bots compete to liquidate first.

**Partial liquidations:** Many protocols only allow liquidating up to 50% of the debt per call — to avoid fully wiping out a borrower when a small liquidation would restore health.

**Cascading liquidations:** If ETH drops sharply, many positions become liquidatable simultaneously. Liquidators sell ETH collateral → ETH price drops further → more liquidations. This is a systemic risk (see Layer 4).

---

## 4. Flash Loans — What Makes Them Unique to DeFi

A flash loan is a loan with no collateral that must be borrowed and repaid within the same transaction.

**The key insight:** In a blockchain transaction, all steps either execute or all revert. If you borrow $1M and don't repay it in the same tx, the entire tx reverts — as if the loan never happened. The protocol takes zero risk.

**What you can do with a flash loan:**
- Borrow a huge amount
- Use it for arbitrage, collateral swaps, liquidations, etc.
- Repay it + a small fee (0.09% on Aave)
- All in one atomic transaction

**Example — arbitrage:**
1. Flash borrow 1,000,000 USDC (no collateral)
2. Buy ETH on DEX A where ETH = $1,990
3. Sell ETH on DEX B where ETH = $2,010
4. Profit = ~$10,000 (minus fees)
5. Repay 1,000,000 USDC + 0.09% fee
6. Net profit: ~$9,100

No upfront capital needed. You're using the protocol's liquidity to capture an opportunity.

---

## 5. Flash Loan Attacks

Flash loans are not inherently malicious — they're a tool. But they amplify the capital available to attackers.

**Classic attack pattern — price oracle manipulation:**
1. Flash borrow a huge amount (e.g., $100M in token A)
2. Dump token A into a DEX pool → crashes the on-chain price of A
3. A lending protocol that uses this DEX pool as a price oracle now sees A as cheap
4. Borrow against the artificially deflated collateral / exploit the mispricing
5. Repay flash loan
6. Walk away with profit

**Example — bZx attack (2020):**
The attacker used flash loans to manipulate the WBTC/ETH price on Uniswap V1 (which bZx used as an oracle), then opened a hugely profitable leveraged position. Drained ~$350K.

**Defense:** Use manipulation-resistant oracles (Chainlink, TWAP with long window) rather than spot prices from a single DEX pool.

---

## 6. Price Oracles — What They Are and Why They Matter

Smart contracts can't access external data (they only see what's on the blockchain). An oracle is a mechanism that brings off-chain data on-chain.

**Most critical data: asset prices.** Lending protocols need prices to:
- Calculate collateral value
- Determine health factors
- Trigger liquidations

**Types of oracles:**
- **Centralized oracle:** A trusted entity pushes prices on-chain. Fast, but single point of failure.
- **Decentralized oracle network (Chainlink):** Many independent node operators fetch prices, aggregate them, and post on-chain. Manipulation requires compromising many nodes simultaneously.
- **On-chain DEX price:** Use the ratio of reserves in a pool as the price. Fast and doesn't rely on any external party, but easily manipulated (see flash loan attacks).
- **TWAP oracle:** On-chain but manipulation-resistant (see below).

---

## 7. Oracle Risks

1. **Price manipulation** — especially with on-chain spot prices (flash loan attacks)
2. **Stale prices** — if the oracle doesn't update frequently, prices lag reality during volatile periods
3. **Centralization** — if a single entity controls the price feed, they can manipulate it
4. **Oracle failure** — if the feed stops updating, the protocol may freeze or behave incorrectly
5. **Front-running oracle updates** — if you know a price update is coming, you can trade ahead of it

**Real incident:** Mango Markets (Solana, 2022) — attacker manipulated the MNGO token price on a thin DEX, then used the inflated price as collateral to borrow $115M from Mango's treasury.

---

## 8. TWAP (Time-Weighted Average Price) Oracle

A TWAP smooths price over time, making flash loan manipulation extremely expensive.

**How it works:** Uniswap V2/V3 tracks cumulative price over time. The TWAP over a window (e.g., 30 minutes) is:
```
TWAP = (cumulative_price_now - cumulative_price_30min_ago) / 30 minutes
```

**Why it resists manipulation:**
- To manipulate a 30-minute TWAP, you'd need to hold the price at a manipulated level for the entire 30-minute window
- That means maintaining a large imbalanced position in the pool for 30 minutes
- Arbitrageurs will immediately trade against you, restoring the price
- The capital cost of holding a manipulated price for 30 minutes is enormous (usually exceeds any profit)

**Tradeoff:** TWAP lags real-time price by its window size. In a fast crash, the TWAP might be $2,000 while ETH is already at $1,500 — protocols may be slow to trigger liquidations.

**Where it's used:** Uniswap V3's built-in TWAP oracle is widely used as a manipulation-resistant on-chain price source.

---

## 9. Stablecoins — Types and Mechanisms

A stablecoin is a token designed to maintain a stable value, usually pegged to $1 USD.

DeFi needs stablecoins because: you can't pay for things with an asset that changes 10% per day. Stablecoins provide a stable unit of account and store of value within the crypto ecosystem.

**Three main types:**

### Fiat-backed (centralized)
- Examples: USDC, USDT, BUSD
- Mechanism: issuer holds $1 in a bank for every token in circulation
- Pros: simple, very stable, redeemable 1:1
- Cons: centralized, can be frozen/blacklisted, requires trust in the issuer, regulatory risk

### Crypto-collateralized (decentralized)
- Examples: DAI (MakerDAO)
- Mechanism: users lock crypto (ETH, WBTC) as collateral (overcollateralized) and mint DAI
- Pros: decentralized, censorship-resistant
- Cons: overcollateralization makes it capital-inefficient; collateral volatility requires active management; undercollateralized in a black swan crash

### Algorithmic (no collateral)
- Examples: UST (Terra/Luna) — now collapsed
- Mechanism: algorithmic supply/demand adjustments, often via a sister token (LUNA burned to mint UST)
- Pros: capital-efficient, no collateral needed
- Cons: **extremely fragile**. The peg relies on market confidence. If confidence breaks, a "death spiral" occurs (UST loses peg → LUNA minted to restore peg → LUNA dumps → confidence collapses further → UST loses peg more → repeat). Terra/Luna collapsed in May 2022, wiping out ~$40B.

---

## 10. How DeFi Protocols Maintain Stablecoin Pegs

**For fiat-backed:** The issuer maintains the peg by honoring redemptions. If USDC trades at $0.99, arbitrageurs buy USDC and redeem for $1 from Circle — this buys pressure restores the peg.

**For crypto-collateralized (DAI):**
- **Stability fee (interest rate):** If DAI is above $1, MakerDAO lowers stability fees → more people borrow DAI → supply increases → price drops back to $1
- **DAI Savings Rate (DSR):** If DAI is below $1, MakerDAO raises DSR → more people lock DAI to earn yield → demand increases → price rises
- **Liquidations:** If ETH crashes, collateral is liquidated and sold → proceeds used to maintain DAI backing

**For algorithmic:** The mechanism relies on arbitrage incentives — if UST < $1, you can burn UST to mint $1 of LUNA (profit). This demand pressure should restore the peg. Works during normal conditions; fails during bank runs when the arbitrage incentive doesn't outweigh the panic.
