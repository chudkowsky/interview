# Layer 6: MEV Strategies — Sandwich, Arbitrage, Liquidation

---

## 1. The MEV Ecosystem — Searchers, Builders, Validators

Three specialized roles have emerged:

**Searchers:**
- Off-chain bots that continuously monitor the mempool and on-chain state
- Identify profitable MEV opportunities (arbitrage, sandwich, liquidation)
- Construct transactions to capture these opportunities
- Submit transactions (or bundles) to block builders
- Compete with other searchers for the same opportunities

**Builders:**
- Specialize in constructing the most profitable possible block
- Receive bundles from many searchers and simulate them
- Select and order txs to maximize total block value (base fees + tips + MEV)
- Submit blocks to validators via a relay

**Validators (Proposers):**
- Randomly selected to propose the next block
- Instead of building the block themselves, they request blocks from builders via MEV-Boost
- Choose the most profitable block offered
- Sign and propose it
- Receive payment from the builder (via the relay)

**Flow:**
```
Searcher finds opportunity
→ submits bundle to Builder
→ Builder constructs optimal block
→ submits to Relay
→ Validator selects highest-paying block
→ block proposed to network
```

---

## 2. Ethereum PoS and Its Effect on MEV

**Before the Merge (PoW):**
- Miners built their own blocks
- They could extract MEV directly
- Priority Gas Auctions: bots bid up gas prices, wasting money on failed txs
- Mining pools with high hash rate had a significant advantage

**After the Merge (PoS, September 2022):**
- Validators replaced miners
- Validators are chosen randomly per slot (12 seconds)
- Any validator with 32 ETH can participate — much lower barrier than mining
- MEV is now democratized through MEV-Boost: even small validators get their fair share of MEV payments
- Builder-proposer separation is now the norm (see Layer 7)

**Key change:** In PoW, a miner could attempt "selfish mining" — try to re-mine a block to reorder txs if they found a big MEV opportunity after the fact ("time-bandit attacks"). In PoS, this is much harder due to finality and attestation rules.

**New PoS-specific risk:** "Proposer withholding" — a validator could delay their block proposal to see one more block of transactions, getting better information about MEV opportunities. This is constrained by slashing risks for missing slots.

---

## 3. Most Common MEV Strategy Types

In rough order of prevalence and profit:

1. **Arbitrage** — most common, generally beneficial to the ecosystem
2. **Sandwich attacks** — harmful to users, purely extractive
3. **Liquidations** — necessary for protocol health, competitive
4. **Long-tail MEV** — novel, protocol-specific opportunities (NFT mints, governance manipulation, etc.)
5. **JIT (Just-In-Time) liquidity** — advanced Uniswap V3 strategy (see Layer 8)

---

## 4. Sandwich Attack — Full Mechanics

A sandwich attack "sandwiches" a victim's large swap between two attacker transactions.

**Setup:** Victim wants to swap 50 ETH for USDC. Pool: 1,000 ETH / 2,000,000 USDC. Victim's slippage tolerance: 1%.

**Step 1 — Frontrun (buy ETH before victim):**
Attacker buys ETH first. Say they buy 100 ETH.
- Pool becomes ~900 ETH / 2,222,222 USDC (price of ETH rises ~23%)
- Attacker received 100 ETH for ~$200,000

**Step 2 — Victim's tx executes:**
Victim's 50 ETH swap now gets a terrible price because the pool is already imbalanced:
- Before attacker: would have gotten ~$98,500 for 50 ETH
- After attacker's frontrun: victim gets much less USDC (near their 1% slippage tolerance)

**Step 3 — Backrun (sell ETH after victim):**
Victim buying ETH further moved the price up. Attacker now sells their 100 ETH at the new elevated price.
- Attacker sells 100 ETH for more USDC than they paid

**Attacker's profit = selling price - buying price - gas costs**

**How it's executed:**
- Attacker submits a bundle: [frontrun tx, victim tx (unchanged), backrun tx]
- Bundles are atomic — either all execute in order or none do
- The frontrun tx has slightly higher gas price than the victim
- The backrun tx has slightly lower gas price (must execute after victim)

**What protects users:**
- Lower slippage tolerance (1% → 0.1%) reduces the attack window but may cause frequent reverts
- Private mempool / Flashbots Protect (victim tx never reaches public mempool)
- Minimum viable slippage: set it as low as possible while still allowing the tx to succeed

---

## 5. Front-Running vs Back-Running

**Front-running:** Execute your transaction BEFORE the target transaction.
- Goal: benefit from the price change the target will cause
- Example: buy ETH before a large ETH purchase (as in sandwich frontrun)
- You need higher gas price to get ahead

**Back-running:** Execute your transaction IMMEDIATELY AFTER the target transaction.
- Goal: profit from the state change the target created
- Example: after a large ETH purchase moves the price up on Uniswap, immediately arbitrage against Sushiswap (which still has the old price)
- You need to be in the same block, right after the target tx

**Key difference:**
- Front-running requires predicting impact and acting before
- Back-running requires reacting to impact and acting after
- Sandwich is a combination: frontrun + [victim tx] + backrun

**Pure back-running is generally considered neutral/beneficial** (it restores price equilibrium). Pure front-running and sandwich attacks are harmful.

---

## 6. Arbitrage MEV

Arbitrage = exploit price discrepancies between two or more pools/exchanges for risk-free profit.

**How price discrepancies arise:**
- Uniswap and Sushiswap both have ETH/USDC pools
- A large trade on Uniswap moves the ETH price there
- Sushiswap's pool hasn't been touched — still has the old price
- A price gap now exists between the two

**The arbitrage:**
1. Bot detects: Uniswap ETH = $2,100, Sushiswap ETH = $2,000
2. Buy ETH on Sushiswap for $2,000
3. Sell ETH on Uniswap for $2,100
4. Profit: $100 per ETH (minus fees and gas)
5. Both pools are now at the same price (bot's trades equalized them)

**Why this is beneficial:** Arbitrage keeps prices consistent across all DEXs, benefiting users who always get a price close to the "true" market price.

**Multi-hop arbitrage:** ETH → USDC on pool A, USDC → DAI on pool B, DAI → ETH on pool C. A cycle that returns more ETH than started. These are harder to find but exist.

**Atomic arbitrage:** All steps in one tx. If the arbitrage fails (someone else got there first), the tx reverts. No risk of partial execution.

**Competition:** Arbitrage bots are extremely competitive. Opportunities are tiny and last milliseconds. Bots compete on speed (co-location near node infrastructure) and algorithm quality. Margins are thin; most profit goes to gas.

---

## 7. Liquidation MEV

Liquidation MEV = profit from triggering liquidations in lending protocols.

**Recall from Layer 3:** When a borrower's health factor drops below 1, any external actor can liquidate them, repay their debt, and receive their collateral at a discount (e.g., 5–10%).

**The MEV angle:**
- Multiple bots watch all borrowing positions on-chain continuously
- When a price drop triggers a health factor < 1, many bots detect it simultaneously
- They race to submit a liquidation transaction first
- The first one to get included earns the liquidation bonus

**Competitive dynamics:**
- Gas auctions: bots bid up gas prices to ensure they get in first
- Bundles via Flashbots: bots submit bundles to builders, bidding on inclusion priority
- Speed matters: bots with faster connections to nodes and better infrastructure win more liquidations

**Why it's important for the ecosystem:** Without liquidation bots, lending protocols would accumulate bad debt (uncollateralized loans), eventually becoming insolvent. The liquidation bonus is the incentive that keeps the ecosystem functioning.

**Risk for liquidation bots:** If they're not careful, they can be sandwiched themselves (attacker front-runs the liquidation or manipulates the collateral price to make the liquidation less profitable).

---

## 8. Why DEXs Are the Largest Source of MEV

DEXs generate MEV for three reasons:

1. **Every trade is public and predictable:** Before a swap executes, its inputs are known. You can calculate exactly what price impact it will have, making sandwich attacks trivially computable.

2. **Trades move prices:** AMM price is mechanically determined by trade size. This creates arbitrage opportunities after every significant trade.

3. **Price differences across pools:** Each DEX maintains its own separate pools. Prices diverge constantly, creating continuous arbitrage opportunities.

**By contrast:**
- Lending protocol interactions are less predictable (when exactly does a price drop cause a liquidation?)
- NFT markets are less liquid and harder to arbitrage
- Derivatives have more complex payoff structures

**The feedback loop:**
Large trade on DEX → price moves → creates arbitrage opportunity → arbitrageur restores price → generates MEV → attracts more searchers → cycle continues

Every block on Ethereum contains hundreds of arbitrage transactions. It's a constant machine.

---

## 9. How Arbitrage Bots Operate Across Multiple DEXs

**Infrastructure:**
- Run full Ethereum nodes (or subscribe to fast block data services)
- Maintain local state: current reserves of every major pool
- Subscribe to pending tx events in the mempool

**Algorithm (simplified):**
1. On every new pending tx or block: update local pool states
2. Compute all possible arbitrage cycles (ETH → USDC → ETH, ETH → DAI → USDC → ETH, etc.)
3. For each cycle, compute profit = output - input - gas costs
4. If profit > threshold: construct an arbitrage transaction
5. Submit via Flashbots bundle or with high gas price
6. Monitor: if someone else gets it, abort; if it lands, collect profit

**Key challenges:**
- **Speed:** The window between a trade creating an opportunity and another bot closing it is milliseconds
- **Gas estimation:** If you underprice gas, your tx fails. If you overprice, you eat profit.
- **Sandwich detection:** Bots have to avoid getting sandwiched themselves
- **Simulation accuracy:** Must simulate the exact on-chain state to avoid failed txs

**Flash loan arbitrage:** If you don't have capital, use a flash loan. Borrow the full amount needed, execute the arbitrage cycle, repay the loan + fee, keep the rest. No capital required, just algorithm + gas.
