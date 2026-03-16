# Layer 5: Mempool & MEV Basics — Public Ordering, Front-Running

---

## 1. What is the Mempool and Why is it Public?

The **mempool** (memory pool) is a holding area for transactions that have been broadcast to the network but not yet included in a block.

When you submit a transaction:
1. Your wallet signs it and broadcasts it to Ethereum nodes
2. Nodes validate the tx and store it in their local mempool
3. The tx is gossiped across the peer-to-peer network — **every node gets a copy**
4. A block builder selects txs from the mempool and includes them in a block
5. Once included, the tx is removed from all mempools

**Why it's public:** The P2P gossip protocol is open. Any node can connect to the Ethereum network and see all pending transactions. You can also query mempools via public RPC endpoints. There is no access control — it's a global broadcast.

**What's visible:** From a pending tx you can see:
- Sender and recipient addresses
- Input data (which function is being called, with what parameters — e.g., "swap 10 ETH for USDC with 1% slippage tolerance")
- Gas price (how much the sender is willing to pay)
- Value

This transparency is what creates MEV opportunities.

---

## 2. Transaction Ordering — Who Decides?

In Ethereum post-Merge (PoS), the process is:

1. A **validator** is randomly selected to propose the next block (proportional to their stake)
2. The validator (or a block builder on their behalf) selects which transactions to include and in what order
3. The block is proposed, attested to by other validators, and finalized

**There are no rules about ordering.** A validator can include any subset of mempool txs in any order. The only constraint is block gas limit.

**Traditional approach (pre-MEV):** Validators ordered txs by gas price (highest first). Users who needed priority would bid higher gas.

**Priority Gas Auctions (PGAs):** MEV searchers would detect a profitable opportunity and submit competing transactions, bidding up gas price until one wins. This was wasteful and clogged the network.

**Post-Flashbots:** Most block building is now off-chain. Searchers send bundles directly to builders, who construct the most profitable block (not just highest gas price).

---

## 3. Front-Running — How It Occurs on Blockchains

Front-running is placing a transaction ahead of a known pending transaction to profit from the price impact it will cause.

**Classic sequence:**
1. Victim submits a large buy order for ETH (visible in mempool)
2. Attacker sees it, submits an identical buy with higher gas price
3. Attacker's buy executes first → price of ETH rises
4. Victim's buy executes at a worse price
5. Attacker immediately sells at the inflated price

This is "generalized front-running." It's possible because:
- Txs are public before execution
- Miners/validators can reorder transactions
- Gas price determines priority (or used to)

**Front-running in traditional finance:** Also illegal in traditional markets (e.g., a broker front-running client orders). In DeFi, it's technically allowed because the blockchain is permissionless — there's no rule against it.

---

## 4. MEV (Maximal Extractable Value) — Definition

**MEV** is the maximum value that can be extracted from block production beyond the standard block reward and gas fees, by including, excluding, or reordering transactions in a block.

Originally called **Miner Extractable Value** (when Ethereum used Proof of Work). After the Merge to Proof of Stake, "Miner" was replaced with "Maximal" — but the concept is the same.

**Three primitives of MEV:**
1. **Include** a transaction — add a tx that wouldn't normally be included (e.g., your own arbitrage tx)
2. **Exclude** a transaction — censor a tx (rare, risky for validators)
3. **Reorder** transactions — change the sequence of existing txs to benefit yourself

**MEV sources:**
- Arbitrage between DEX pools
- Sandwich attacks on large DEX swaps
- Liquidations in lending protocols
- Long-tail / novel opportunities

**MEV is not always harmful.** Arbitrage MEV brings prices across pools into alignment — this is a public good. Liquidation MEV keeps lending protocols solvent. Sandwich attacks, however, are pure extraction from users.

---

## 5. MEV vs Miner Extractable Value — The Distinction

**Miner Extractable Value (old term):** When Ethereum used Proof of Work, miners had full control over block construction. They could directly extract MEV themselves by reordering txs in the blocks they mined.

**Maximal Extractable Value (new term):** After the Merge to Proof of Stake:
- Validators replaced miners
- Validators don't necessarily construct blocks themselves anymore
- A specialized ecosystem emerged: **searchers** find MEV opportunities, **builders** construct optimal blocks, **validators/proposers** choose which block to include
- The "maximal" framing acknowledges that the total extractable value is a property of the network state, not just what validators capture

**Key difference:** In PoW, miners were vertically integrated (find opportunities + build blocks + mine). In PoS + PBS, these roles are separated. Validators just propose blocks; builders specialize in optimization; searchers specialize in finding opportunities.

**Also:** "Maximal" rather than "miner" because non-miner actors (searchers, builders) now extract most of the value. Validators receive their share through MEV-Boost payments.

---

## 6. Why Public Mempool Transparency Creates MEV Opportunities

The mempool is essentially a **live feed of users' intentions** before they execute. This creates information asymmetry:

- **You can see what will happen:** A pending tx that says "buy 100 ETH with 2% slippage tolerance" tells you exactly how much the price will move and what the price range is.
- **You can act on it before it does:** Submit a tx with higher gas to execute before the victim's tx.
- **You know the outcome in advance:** You can calculate the exact profit of a sandwich attack before sending a single transaction.

**Analogy:** Imagine if in a stock exchange, every order was publicly broadcast 10 seconds before it executed. Front-running would be trivial.

**The information flow:**
```
User submits tx → gossips across network → visible to anyone running a node
→ MEV bots analyze every pending tx → detect profitable opportunities
→ submit competing/surrounding txs → profit
```

---

## 7. Risks MEV Poses to Normal Users

1. **Sandwich attacks:** Users pay more for DEX trades than they should. Large trades with high slippage tolerance are especially vulnerable. The difference is pure extraction.

2. **Failed transactions with paid gas:** Users who try to compete with bots lose races and pay gas for reverted txs.

3. **Worse prices:** Even without explicit attacks, the reordering of txs can result in users getting worse prices than expected.

4. **Unpredictability:** Users can't know exactly what price they'll get, just an upper bound (their slippage tolerance).

5. **Network congestion:** Gas wars between bots historically clogged the network and raised gas prices for everyone.

**Estimated losses:** Researchers estimate hundreds of millions of dollars per year are extracted from ordinary users via sandwich attacks alone.

---

## 8. Why MEV Exists — Root Causes

MEV is an emergent property of three features of public blockchains:

1. **Public mempool:** All pending txs are visible to everyone.
2. **Block producer discretion:** The entity creating the block can order txs however they want.
3. **On-chain state changes have value:** Changing the order of txs changes who profits from arbitrage, liquidations, and price impacts.

**MEV cannot be eliminated without:**
- Removing block producer discretion (but then who decides order? another centralization vector)
- Encrypting the mempool (possible with cryptography, but complex and introduces latency)
- Moving to off-chain order matching (but then you have centralization)

**The fundamental tension:** Decentralized blockchains need someone to order transactions, and whoever does that ordering has power to extract value from the ordering.

Flashbots and PBS are attempts to manage and redistribute MEV rather than eliminate it.
