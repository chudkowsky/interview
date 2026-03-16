# Layer 9: Synthesis — MEV in Uniswap V3, Sandwich Protection

## What to cover in this layer
How everything connects. This layer is about reasoning across systems, not new concepts.

---

## 1. How Concentrated Liquidity Affects MEV Opportunities

<!-- your notes: does tighter liquidity increase or decrease sandwich profitability? -->

---

## 2. How a Large Swap Creates a Sandwich Opportunity — End to End

<!-- your notes: trace the full flow from user submitting tx to attacker profit -->

---

## 3. Private Transaction Relays as Sandwich Protection

<!-- your notes: connect to Flashbots from Layer 7 -->

---

## 4. Sandwich Attack — Mempool and Block Level Detail

<!-- your notes: write out every step including gas price bidding -->

---

## Connections to draw explicitly

- Layer 1 (x*y=k) → why large swaps have high slippage → sandwich opportunity
- Layer 5 (mempool) → why the attacker can see the victim tx
- Layer 7 (Flashbots relay) → how private order flow prevents the attack
- Layer 8 (ticks, concentrated liquidity) → how V3 changes the attack surface
