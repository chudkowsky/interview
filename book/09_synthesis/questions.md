# Layer 9: Questions

These are the hardest questions. They expect you to connect multiple layers.

---

**Q98.** How does concentrated liquidity affect MEV opportunities?

Concentrated liquidity in Uniswap V3 creates more MEV opportunities in some ways and fewer in others. **More MEV**: Narrow liquidity ranges mean much higher price impact per dollar of swap volume when liquidity is thin — a large swap through a lightly-concentrated range creates more slippage, making sandwich attacks more profitable. Out-of-range positions create sudden liquidity cliffs where price can move sharply, amplifying arbitrage MEV. **Less MEV**: When liquidity is highly concentrated around the current price, depth is deeper and slippage lower for normal-sized trades — sandwiching small swaps becomes unprofitable. V3 also enables **JIT (Just-In-Time) liquidity** — a builder-level MEV strategy where a searcher provides massive concentrated liquidity in the block just before a large swap (to collect the fees), then removes it immediately after. JIT is a unique V3 MEV vector with no V2 equivalent.

**Q99.** How could a large swap create a sandwich opportunity?

A large pending swap in the public mempool broadcasts its price impact before execution. For example: user A submits a swap of 100 ETH → USDC on Uniswap (moving the ETH/USDC price significantly). A sandwich bot: (1) **Front-runs**: submits a USDC→ETH buy at higher gas, executing just before user A — buying ETH cheap before the user's sell pressure. (2) User A's swap executes, pushing the ETH price down in the pool. (3) **Back-runs**: the bot immediately sells ETH→USDC at the new (higher USDC / lower ETH) pool price. The bot's profit equals roughly the price impact A caused (the ETH/USDC spread between the two bot trades), minus gas. User A receives fewer USDC than expected — up to their slippage tolerance. The larger the swap relative to pool liquidity, the more profitable the sandwich.

**Q100.** How can private transaction relays help protect users from sandwich attacks?

Private transaction relays (MEV Blocker, Flashbots Protect, 1inch Fusion) route user transactions directly to block builders without broadcasting to the public mempool. Since sandwich bots can only see transactions in the public mempool, a privately-submitted transaction is invisible to them — no front-run or back-run is possible. The transaction lands in the builder's private queue and is included in the next block the builder constructs. Additionally, some relays use "backrun-only" matching: they share the transaction with a vetted set of searchers who may only back-run (capture price discrepancies created by the transaction) but not front-run, and the backrun profit is rebated to the user. The limitation is trust: users must trust the relay/builder not to leak their transaction or sandwich it themselves.

**Q101.** Explain a sandwich attack step-by-step at the mempool and block level.

**Mempool phase**: User submits `swap(100 ETH → USDC, slippage=1%)` — this transaction enters the public mempool. A MEV bot detects it: parses the calldata, simulates the price impact (100 ETH moves the pool price from $2,000 to ~$1,980), calculates the sandwich profit, and constructs a bundle: [front-run, victim, back-run]. The front-run is `swap(USDC → ETH)` with a higher gas tip. The back-run is `swap(ETH → USDC)` with a lower gas tip. The bundle is submitted to a builder via Flashbots relay. **Block construction phase**: The builder receives the bundle, simulates it, and includes it in the block with the victim's transaction sandwiched between the bot's two trades. **Execution**: Front-run executes — bot buys ETH at $2,000, pool price moves to ~$1,990. Victim executes — buys 100 ETH, pool moves to ~$1,970, user gets fewer USDC (within their 1% tolerance). Back-run executes — bot sells ETH at ~$1,970 into the now-depleted USDC side, recouping profit. Bot profits ~$20–30/ETH from the spread; user loses that same amount relative to fair execution.
