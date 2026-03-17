# Layer 6: Questions

---

**Q27.** How do sandwich attacks work?

A sandwich attack has three steps: (1) **Front-run** — the attacker sees a pending large swap (e.g., user buying ETH with USDC) and submits their own buy transaction at a higher gas price, executing just before the victim; (2) **Victim executes** — the victim's swap runs, pushing the ETH price up in the pool; (3) **Back-run** — the attacker immediately sells their ETH back into the now-higher price, capturing the price impact as profit. The victim ends up buying at a worse price (closer to their slippage limit). The attacker's profit equals roughly the price impact the victim causes, minus gas costs. Sandwich attacks are only prevented by submitting to private/encrypted mempools or using aggregators with MEV protection.

**Q52.** What actors participate in the MEV ecosystem (searchers, builders, validators)?

**Searchers** are bots (run by traders or firms) that continuously scan the mempool and blockchain state to identify MEV opportunities. They construct bundles of transactions that capture the opportunity (arbitrage, sandwich, liquidation) and submit them to builders or directly to validators with a bid. **Builders** (post-PBS) construct the full block by assembling transactions and bundles from searchers and the public mempool, optimizing for maximum fees. They submit the completed block to validators with a bid. **Validators** (proposers) select the highest-bidding builder's block to propose, collecting the bid as profit without needing to do any MEV work themselves. This three-tier architecture concentrates sophistication at the builder layer and commoditizes the validator role.

**Q53.** How did Ethereum's move to Proof of Stake change the MEV landscape?

Pre-Merge: miners built blocks themselves and could directly capture MEV. Post-Merge: validators propose blocks but (under MEV-Boost) outsource block construction to specialized builders via relays. PBS separates the role of proposing from building, so validators earn MEV revenue passively through the builder auction rather than actively searching for MEV. This reduced MEV-driven validator centralization pressure but concentrated power at the builder level — a handful of sophisticated builders (Beaverbuild, Titan Builder) now construct the majority of Ethereum blocks. The MEV landscape also shifted from direct miner manipulation to a more formalized marketplace through Flashbots' infrastructure.

**Q55.** What are the most common types of MEV strategies?

The three dominant MEV strategies are: (1) **Arbitrage** — exploiting price discrepancies between DEX pools (e.g., ETH priced differently on Uniswap vs Curve); (2) **Sandwich attacks** — front-running and back-running a large pending AMM swap to profit from the price impact; (3) **Liquidations** — being the first to trigger a liquidation on an undercollateralized lending position to claim the discount. Secondary strategies include: NFT mint sniping, JIT (Just-In-Time) liquidity provision in Uniswap V3, back-running oracle updates, and long-tail arbitrage across obscure token pairs. Arbitrage MEV is generally considered "good" (improves price efficiency) while sandwich attacks are extractive harm to users.

**Q56.** What is a sandwich attack?

A sandwich attack is an MEV strategy where an attacker places one transaction immediately before and one immediately after a victim's pending DEX swap. The attacker's front-run transaction moves the pool price in the same direction as the victim's trade, forcing the victim to execute at a worse price. The attacker's back-run then reverses their position at the new (higher or lower) price, capturing a profit equal to the price impact caused by the victim. The victim pays the attacker's profit as additional price impact, on top of normal pool fees and slippage. Sandwich attacks are uniquely enabled by public mempool visibility and the ability to order transactions within a block.

**Q57.** What is arbitrage MEV?

Arbitrage MEV involves exploiting price differences for the same asset across different DEX pools. For example, if ETH trades at $2,000 on Uniswap and $2,010 on SushiSwap, an arbitrageur can buy on Uniswap and sell on SushiSwap for a ~$10/ETH profit (minus gas and fees). This is MEV because the opportunity only exists transiently — other arbitrage bots compete to capture it, and prices equalize within blocks. Arbitrage is generally considered "good MEV" because it keeps DEX prices aligned with each other and with centralized exchange prices, improving overall price efficiency. However, the competitive nature drives up gas costs and can crowd out regular transactions.

**Q58.** What is liquidation MEV?

When a borrower's position in a lending protocol (Aave, Compound) becomes undercollateralized, any external actor can trigger the liquidation and receive a bonus (typically 5–15% of the liquidated collateral). This liquidation bonus is MEV — multiple bots compete to be the first to submit the liquidation transaction in the same block the position becomes eligible. Flash loans are often used so liquidators don't need upfront capital: borrow the repayment amount, trigger the liquidation (receive discounted collateral), sell the collateral, repay the flash loan — net profit in one transaction. Liquidation MEV benefits the protocol (keeps it solvent) and disadvantages the borrower (who loses collateral at a discount).

**Q59.** How does front-running differ from back-running?

Front-running means executing your transaction BEFORE a known pending transaction to profit from the state change it will cause (e.g., buying an asset before a large purchase drives the price up). Back-running means executing AFTER a known transaction, to profit from a state created by that transaction (e.g., an arbitrage trade that corrects a price imbalance left by the preceding transaction, or a JIT liquidity withdrawal immediately after a large swap). Both exploit transaction ordering but in opposite directions. Sandwich attacks combine both. Back-running is generally considered less harmful than front-running because it doesn't worsen the victim's execution — it just opportunistically profits from the resulting state.

**Q95.** What role does MEV play in Uniswap arbitrage?

Every time an external price moves (e.g., ETH drops on Coinbase), Uniswap's on-chain pools become stale — the pool price is wrong relative to the market. MEV searchers and arbitrage bots monitor this divergence and race to submit the corrective trade: buy cheap ETH from Uniswap before the pool price adjusts. The first arbitrage transaction in the block captures most of the profit; subsequent ones get smaller slices. This competition drives gas costs up but ensures Uniswap prices stay close to market prices. Without arbitrage MEV, Uniswap pools would diverge significantly from real market prices, increasing informed trader losses for LPs.

**Q96.** Why are DEXs major sources of MEV?

DEXs are the primary MEV source because: (1) Every swap creates a price impact that can be front-run or sandwiched; (2) When external prices move, pool prices diverge creating arbitrage opportunities; (3) All pending swaps are public in the mempool, giving MEV bots perfect advance knowledge; (4) AMM pricing is formulaic and predictable — bots can exactly calculate profits before submitting; (5) Large pools hold enormous value with continuous trading activity creating constant MEV opportunities. Uniswap consistently generates the most MEV of any DeFi protocol due to its dominant DEX liquidity. By contrast, order-book exchanges with private order flow naturally reduce these MEV vectors.

**Q97.** How do arbitrage bots exploit price differences between pools?

Arbitrage bots continuously monitor price discrepancies across DEX pools using real-time state reads (eth_call) or by listening to Swap events. When the price of ETH is $2,000 in Uniswap pool A and $2,010 in SushiSwap pool B, the bot calculates the optimal input amount that maximizes profit after gas costs. It then submits a bundle: buy ETH on pool A, sell on pool B, in a single atomic transaction. The bot bids enough gas (or Flashbots tip) to get included ahead of other arbitrageurs. More sophisticated bots use flash loans and multi-hop paths (A→B→C→A) to close circular arbitrage without capital. The competition among bots reduces arbitrage spreads to near-zero, keeping DEX prices efficient.

**Q102.** How do arbitrage bots operate between multiple decentralized exchanges?

Cross-DEX arbitrage bots scan price differences not just between two pools, but across complex graphs of pools and chains. Using graph algorithms (Bellman-Ford for negative cycles), they identify profitable multi-hop paths — e.g., buy USDC→ETH on Uniswap, ETH→WBTC on Curve, WBTC→USDC on SushiSwap — that close at a profit. These "triangular arbitrage" cycles can involve 3–10 hops and dozens of pools simultaneously. All hops execute atomically in one transaction using flash loans if needed. The bots must account for gas costs, price impact of each hop, and competition — submitting via Flashbots private relay to avoid being front-run themselves. Highly competitive: hundreds of bots compete for each opportunity.

**Q104.** Why are decentralized exchanges the largest source of MEV?

DEXs dominate MEV generation because they combine the highest transaction volume, fully public order flow (via mempool), deterministic pricing formulas (enabling exact profit calculation), and constant price divergence from external markets. Every DEX swap is simultaneously: a potential front-run/sandwich target (if large enough), a potential arbitrage trigger (if it creates a cross-pool discrepancy), and a reference price source for downstream MEV (like liquidations). DEXs also generate "reflexive MEV" — each arbitrage trade on a DEX can create new imbalances in connected pools, spawning further arbitrage. No other DeFi protocol category matches this combination of volume, predictability, and public visibility.
