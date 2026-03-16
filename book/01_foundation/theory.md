# Layer 1: Foundation — DeFi, AMMs, Liquidity Pools

---

## 1. What is DeFi?

DeFi (Decentralized Finance) is financial services built on public blockchains — no banks, no brokers, no custodians. Anyone with a wallet can access them.

**Key differences from traditional finance:**

| Traditional Finance | DeFi |
|---|---|
| Intermediaries (banks, brokers) | Smart contracts replace intermediaries |
| Permissioned (KYC, credit checks) | Permissionless — any wallet can interact |
| Closed source, opaque | Open source, fully transparent |
| Business hours, settlement days | 24/7, settlement in seconds |
| Custodial (bank holds your money) | Non-custodial (you hold your keys) |

The tradeoff: DeFi removes counterparty risk from institutions but introduces smart contract risk (bugs, exploits).

---

## 2. Components of a DeFi Ecosystem

- **Wallets** — user interface to sign transactions (MetaMask, etc.)
- **DEXs** (Decentralized Exchanges) — swap tokens without a counterparty (Uniswap, Curve)
- **Lending protocols** — borrow/lend assets (Aave, Compound)
- **Stablecoins** — price-stable assets needed for everyday use (USDC, DAI)
- **Oracles** — bring real-world price data on-chain (Chainlink)
- **Bridges** — move assets between blockchains
- **Aggregators** — route trades across DEXs for best price (1inch)
- **Governance** — token holders vote on protocol changes

These compose together. A lending protocol uses an oracle for prices, a DEX for liquidations, a stablecoin for collateral. This is "money legos."

---

## 3. Smart Contracts

A smart contract is code deployed on a blockchain that executes automatically when conditions are met. No one can stop it, alter it mid-execution, or censor it.

**Why critical for DeFi:**
- They replace the trusted third party. Instead of trusting a bank to process your loan, you trust audited, open-source code.
- Execution is deterministic — same inputs always produce the same outputs.
- Assets are held in the contract, not by a company.

**The risk:** bugs in the code are permanent (unless the contract has an upgrade mechanism). If a bug exists, funds can be drained. This is why audits matter.

---

## 4. Layer 1 vs Layer 2 Blockchains

**Layer 1 (L1):** The base blockchain. Handles its own consensus, security, and data availability.
- Examples: Ethereum, Bitcoin, Solana
- Slow and expensive when congested (Ethereum can cost $50+ per tx during peaks)

**Layer 2 (L2):** A system built on top of L1 that processes transactions off-chain, then posts compressed results back to L1.
- Examples: Arbitrum, Optimism, Base (Optimistic rollups); zkSync, Starknet (ZK rollups)
- Inherits L1 security but offers 10–100x cheaper transactions

**How L2s work (simplified):**
1. Users transact on L2
2. A sequencer batches hundreds of txs together
3. The batch is posted to L1 as a single transaction
4. Cost is amortized across all users in the batch

**Optimistic rollups** assume txs are valid, allow a challenge window (~7 days) to dispute fraud.
**ZK rollups** generate a cryptographic proof that all txs are valid — no challenge window needed.

---

## 5. How Automated Market Makers (AMMs) Work

A traditional exchange uses an order book — buyers and sellers post bids/asks and orders match. An AMM replaces this with a **liquidity pool** and a **pricing formula**.

**Core idea:**
- A pool holds two tokens (e.g., ETH and USDC)
- The price is determined algorithmically from the ratio of tokens in the pool
- Anyone can trade against the pool at any time — no counterparty needed
- Anyone can deposit tokens to become a liquidity provider and earn fees

**Flow of a swap:**
1. User sends token A to the pool
2. The AMM formula determines how much token B to return
3. Token B is sent to the user
4. The pool now has more A and less B — price of A drops, price of B rises

---

## 6. The Constant Product Formula (x * y = k)

The formula used by Uniswap V2 (and most AMMs):

```
x * y = k
```

Where:
- `x` = reserve of token A
- `y` = reserve of token B
- `k` = constant (never changes, except when liquidity is added/removed)

**Example:**
Pool starts with: 10 ETH and 10,000 USDC → k = 100,000

A user wants to buy ETH with USDC. They send 1,000 USDC.

New USDC reserve: 10,000 + 1,000 = 11,000
New ETH reserve must satisfy: x * 11,000 = 100,000 → x = 9.09 ETH
ETH sent to user: 10 - 9.09 = **0.91 ETH**

Note: the user "paid" 1,000 USDC for 0.91 ETH = ~1,099 USDC/ETH (actual market price was 1,000). The difference is **slippage** caused by moving the pool ratio.

**The curve visualized:**
```
y
|  *
|    *
|      *
|         *
|              *
+---------------------- x
```
Moving along this curve always keeps x*y=k. Large trades move the price more (steeper curve region).

---

## 7. Slippage

Slippage is the difference between the expected price and the actual price received in a trade.

**Why it happens:** Each token you buy removes it from the pool, making the next token more expensive (the curve bends upward). Large trades relative to pool size cause large slippage.

**Example:**
- Small pool: 10 ETH / 10,000 USDC. Buying 3 ETH causes massive slippage (~43%).
- Large pool: 1,000 ETH / 1,000,000 USDC. Buying 3 ETH causes ~0.6% slippage.

**Price impact formula (approximate):** slippage ≈ trade size / pool size

Users set a **slippage tolerance** (e.g., 0.5%) — if the price moves more than that before the tx executes, it reverts. High slippage tolerance = vulnerable to sandwich attacks.

---

## 8. Liquidity Pools — Structure

A pool is a smart contract holding two token reserves. Key state it tracks:
- `reserve0` — amount of token 0
- `reserve1` — amount of token 1
- `totalSupply` — total LP tokens issued

**LP tokens:** When you deposit, you receive LP tokens representing your share of the pool. They are fungible (Uniswap V2) and can be redeemed later for your share of whatever is in the pool at that time.

**Example:**
Pool: 10 ETH + 10,000 USDC. You deposit 1 ETH + 1,000 USDC → you own 10% of the pool → receive 10% of LP tokens.

If the pool grows to 12 ETH + 12,000 USDC (from fees), your 10% is now worth 1.2 ETH + 1,200 USDC.

---

## 9. How a Token Swap Occurs — Step by Step

1. User approves the router contract to spend their tokens
2. User calls `swap()` on the router with: token in, amount in, min amount out, deadline
3. Router calls the pool contract
4. Pool checks the constant product formula to calculate amount out
5. Pool sends token out to the user
6. Pool receives token in from the user
7. Pool verifies `new_x * new_y >= k` (it's actually `>` k by the fee amount)
8. Event emitted, swap complete

**The fee (0.3% in V2):** On each swap, 0.3% of the input stays in the pool. This means k actually grows slightly after each trade — this is how LPs earn.

---

## 10. CEX vs DEX

| | CEX (Centralized Exchange) | DEX (Decentralized Exchange) |
|---|---|---|
| Order matching | Order book, off-chain | AMM formula, on-chain |
| Custody | Exchange holds your funds | You hold your funds |
| KYC | Required | Not required |
| Speed | Milliseconds | Block time (~12s on Ethereum) |
| Liquidity source | Market makers, order book | Liquidity providers in pools |
| MEV exposure | None (centralized matching) | High (public mempool) |
| Downtime risk | Yes (exchange goes down) | No (blockchain always runs) |
| Counterparty risk | Exchange can be hacked/insolvent | Smart contract bugs only |

CEXs are faster and have better UX. DEXs are trustless and always available, but slower and expose users to MEV.
