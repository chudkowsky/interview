# Layer 9: Synthesis — MEV in Uniswap V3, Sandwich Protection

This layer has no new concepts. It's about connecting everything from the previous layers.

---

## 1. How Concentrated Liquidity Affects MEV Opportunities

**Recall:** In V3, liquidity is concentrated in ranges. The active liquidity at the current price depends on which positions have ranges covering that price. At tick boundaries, the active liquidity can change sharply.

**Effect on sandwich attacks:**

Concentrated liquidity generally makes the price more sensitive to large trades — but only within heavily concentrated ranges.

**Scenario A — deeply concentrated range (stablecoin pool):**
- The ETH/USDC pool has most liquidity concentrated in [$1,990, $2,010]
- Enormous liquidity in a tiny range → very low slippage within that range → sandwich attack is less profitable (small price impact = small profit)
- But: if the trade is large enough to cross the entire range, the impact on the other side is severe → sandwich is very profitable at tick boundaries

**Scenario B — sparse liquidity (exotic token):**
- Thin liquidity across wide ranges → each dollar of trade causes large price movement
- Sandwich attacks are more profitable
- But fewer users trade exotic pairs

**JIT liquidity as a form of MEV in V3:**
1. A large swap comes into the mempool
2. MEV bot provides a huge position in the tick range around the current price (same block, before the swap)
3. The swap executes → bot earns most of the swap's fees
4. Bot removes liquidity in the same block, after the swap
5. Net effect: bot "stole" the fee income from that swap from passive LPs

JIT is unique to V3's concentrated liquidity model. It's debated whether it's harmful — it does improve price execution for the user (more liquidity = less slippage), but it extracts fees from passive LPs.

**Tick boundary MEV:**
When a large trade crosses a tick boundary, the pool's liquidity changes. Bots can:
- Predict exactly when a trade will cross a boundary
- Position themselves to capture the price impact on either side
- Arbitrage the state change at the boundary itself

---

## 2. How a Large Swap Creates a Sandwich Opportunity — End to End

Let's trace it completely.

**Setup:** User wants to swap 100 ETH for USDC on Uniswap V3. Pool: heavy liquidity around current price of $2,000. User sets 1% slippage tolerance → they'll accept as low as $1,980 per ETH.

**Step 1 — User broadcasts tx:**
User submits tx to the public mempool. The tx is a call to the Uniswap V3 router:
```
swap(
  tokenIn: ETH,
  tokenOut: USDC,
  amountIn: 100 ETH,
  amountOutMinimum: 198,000 USDC,  // 1% slippage
  sqrtPriceLimitX96: ...,
)
```

**Step 2 — MEV bot detects it:**
Bot's mempool monitor picks up the tx in milliseconds. Bot simulates it:
- Calculates the price impact: 100 ETH sell will move price from $2,000 to ~$1,985
- Calculates the sandwich profit window: user accepts anything above $1,980 → 0.25% spread to exploit
- Determines max frontrun size that keeps victim's tx above their slippage floor

**Step 3 — Bot constructs a bundle:**
```
Bundle: [
  tx1: Bot sells ETH → USDC (frontrun) — moves price down to $1,986
  tx2: User's swap tx (unchanged)       — user gets $1,981/ETH (within tolerance)
  tx3: Bot buys ETH ← USDC (backrun)   — buys at depressed price
]
```

**Step 4 — Bot submits bundle to Flashbots:**
Bundle targets blocks N, N+1, N+2. Includes a payment to the builder via `block.coinbase.transfer`.

**Step 5 — Builder includes the bundle:**
Builder simulates the bundle, verifies profitability, includes it in the block.

**Step 6 — Block proposed:**
All three txs land in order. Bot profits from the spread.

**User's experience:** They submitted a swap at $2,000 and got $1,981 per ETH instead of $1,993 (without the sandwich). They lost ~$1,200 compared to no attack.

---

## 3. Private Transaction Relays as Sandwich Protection

**The core fix:** If the user's tx never hits the public mempool, MEV bots never see it, so they cannot front-run it.

**Flashbots Protect:**
- A free RPC endpoint: `https://rpc.flashbots.net`
- User's wallet sends txs here instead of the public mempool
- Flashbots forwards the tx directly to builders
- Builders include it in the next available block without exposing it publicly
- MEV bots watching the public mempool see nothing

**What this guarantees:**
- No sandwich attacks (tx is invisible until it's in a block)
- No failed tx gas waste (if the tx can't be included, it's silently dropped)

**What it doesn't guarantee:**
- The builder still sees the tx. A malicious builder could theoretically extract MEV. In practice, major builders don't sandwich individual user txs (reputation cost).
- The tx might wait slightly longer for inclusion if the current block producer isn't using the Flashbots relay.

**MEV Blocker, 1inch Fusion, CoW Protocol:**
Alternative approaches that also protect users — often using batch auctions or solver-based matching instead of just private channels.

**CoW Protocol (batch auctions):**
- All orders submitted within a time window are batched
- An off-chain "solver" finds the optimal settlement for the entire batch at a uniform clearing price
- All users in the batch get the same price — there's no ordering to exploit
- Structural protection: even if a solver could reorder within a batch, everyone gets the same price anyway

---

## 4. Sandwich Attack — Mempool and Block Level Detail

This is the advanced version — combine everything from Layers 5, 6, 7.

**At the mempool level:**

```
T=0ms: User signs and broadcasts tx to Ethereum P2P network
T=1ms: Tx propagates to MEV bot's mempool monitor (co-located node)
T=2ms: Bot decodes calldata → identifies it's a large Uniswap swap
T=3ms: Bot simulates tx against current chain state → calculates price impact
T=4ms: Bot determines sandwich parameters:
         - optimal frontrun size
         - expected victim execution price
         - expected backrun profit
         - gas cost of entire bundle
         - builder payment (bid)
T=5ms: Bot constructs and signs 3 transactions
T=6ms: Bot submits bundle to Flashbots relay
```

**At the builder level:**

```
Builder receives bundle from bot
Builder simulates bundle against mempool state
Builder checks: is the victim tx in the public mempool? Will it land?
Builder calculates: what's the total block value if I include this bundle?
Builder compares against all other bundles and mempool txs
Builder decides: include the sandwich bundle → it's profitable
Builder constructs block: [...other txs..., frontrun, victim_tx, backrun, ...]
Builder submits to relay with bid
```

**At the block/validator level:**

```
Validator's MEV-Boost receives block header + bid from relay
Validator signs the header (commits to this block)
Relay releases full block to validator
Validator broadcasts block to network
Block finalized
```

**In the block itself:**

```
Block N:
  tx_index 41: [bot] buy ETH on V3 (frontrun)
    - Gas price: higher than victim
    - Result: ETH price moves from $2,000 to $1,986
  tx_index 42: [victim] sell 100 ETH for USDC
    - Gas price: original (lower than bot)
    - Result: victim gets $1,981/ETH (within 1% slippage tolerance ✓)
    - ETH price now at $1,979 (further depressed by victim's sale)
  tx_index 43: [bot] sell USDC for ETH (backrun)
    - Gas price: just slightly lower than victim (to land after)
    - Result: bot buys ETH at $1,979 → price recovers toward $1,993
    - Bot profit: (sell price - buy price) × ETH amount - gas - builder payment
```

**Why the bundle must be atomic:**
If any other tx slips between index 41 and 42 (someone else front-runs the frontrun), the victim's tx might get a better price than the bot anticipated, making the backrun unprofitable or causing a loss. The bundle atomicity guarantees the 3 txs are consecutive.

**Failure modes the bot must account for:**
- Victim's tx reverts (low slippage, price already moved): bot loses gas if victim tx not in `revertingTxHashes`
- Another bot submitted the same sandwich first: builder picks only one → bot's bundle is discarded silently
- Price moved between bundle submission and block landing: victim's new effective price might be outside slippage → victim tx reverts → sandwich collapses

---

## Connecting the Layers

| Concept | Layer | How it connects |
|---|---|---|
| x*y=k | 1 | Why large swaps move price → creates sandwich profit window |
| Slippage tolerance | 1 | Defines the exploit window for sandwich attackers |
| LP impermanent loss | 2 | Arbitrage MEV is the mechanism that causes IL in AMMs |
| Flash loans | 3 | Amplify capital for both arbitrage and attacks |
| TWAP oracle | 3 | Resists flash loan manipulation; used as a V3 built-in |
| Public mempool | 5 | Root cause of sandwich visibility |
| Sandwich attack | 6 | Combines mempool visibility + x*y=k price mechanics |
| Flashbots bundles | 7 | The mechanism that makes sandwich attacks atomic and gas-efficient |
| PBS | 7 | Separates block building; enables specialized attack execution |
| Private relay | 7 | The fix for sandwich: remove mempool visibility |
| Concentrated liquidity | 8 | Changes sandwich profitability by changing price impact profiles |
| Ticks | 8 | Tick crossings create additional MEV opportunities |
| JIT liquidity | 8+9 | V3-specific MEV that uses concentrated liquidity mechanics |
