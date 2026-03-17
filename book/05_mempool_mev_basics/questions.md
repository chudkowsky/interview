# Layer 5: Questions

---

**Q25.** What is front-running and how does it occur on blockchains?

Front-running is the act of inserting your transaction ahead of a known pending transaction to profit from the price impact that transaction will cause. On Ethereum, all pending transactions sit in the public mempool before being included in a block. Anyone can see a large DEX trade pending and submit their own transaction with a higher gas price to get executed first — buying before the large trade pushes the price up, then selling into the price increase. Front-running on blockchains is structurally enabled by the visibility of pending transactions and miners'/validators' ability to reorder them for profit.

**Q26.** What is MEV (Maximal Extractable Value)?

MEV (Maximal Extractable Value, formerly Miner Extractable Value) is the total value that can be extracted from a block by optimally ordering, including, or excluding transactions — beyond the standard block reward and gas fees. It represents the profit available to whoever controls transaction ordering: miners (pre-merge) or validators/block builders (post-merge). MEV sources include arbitrage between DEX pools, sandwich attacks on large swaps, liquidation bonuses from lending protocols, and NFT minting opportunities. MEV is a fundamental property of any blockchain where transaction order can be chosen by a profit-maximizing party.

**Q51.** What is MEV (Maximal Extractable Value) and how does it arise in blockchains?

MEV arises from the combination of: (1) a public mempool where pending transactions are visible before execution, (2) block producers who choose which transactions to include and in what order, and (3) financial state transitions (trades, liquidations) whose value depends on their position relative to other transactions. When a large pending swap would move a DEX price, a block producer (or a searcher paying them) can insert their own trade before it to profit. MEV is not a bug — it's an emergent consequence of fee markets, public mempools, and profit-maximizing actors. Estimates suggest MEV exceeds $1B per year on Ethereum alone.

**Q54.** What is the difference between MEV and miner extractable value?

"Miner Extractable Value" was the original term coined by Daian et al. in the Flash Boys 2.0 paper, referring specifically to value that miners could extract by reordering transactions in proof-of-work Ethereum. After Ethereum's transition to Proof of Stake (The Merge, 2022), miners no longer exist — validators propose blocks. Additionally, the Proposer-Builder Separation (PBS) model means that specialized "block builders" construct blocks rather than validators themselves. The term was updated to "Maximal Extractable Value" to reflect that: (1) it's no longer just miners who extract it, and (2) it represents the theoretical maximum extractable from the system, not just what miners actually captured.

**Q61.** Why does public mempool transparency create MEV opportunities?

When a user submits a transaction to Ethereum, it broadcasts to all nodes' mempools and sits there (visible to anyone) until a block producer includes it — typically 1–12 seconds. During this window, any observer can see the transaction's parameters: which DEX, which token pair, the exact input amount, and the slippage tolerance. This is effectively a "tip-off" about the future state change the transaction will cause. MEV searchers use this information to identify profitable opportunities (arbitrage price discrepancies, liquidations, sandwich setups) and submit competing transactions with higher gas to execute first or immediately after the target transaction. Private mempools and encrypted mempools (like MEV Blocker, Shutter Network) are being developed to mitigate this.

**Q62.** What are the risks MEV poses to normal users?

For regular users, MEV manifests as: (1) **Sandwich attacks** — your swap gets sandwiched, meaning you execute at a worse price than expected (your slippage tolerance is consumed); (2) **Failed transactions** — MEV bots outbid you for execution, causing your transaction to fail while still paying gas; (3) **Higher effective costs** — competitive MEV bidding inflates gas prices for everyone during peak activity; (4) **Unfair price discovery** — large traders in AMMs effectively announce their intentions publicly and get exploited; (5) **Centralization pressure** — MEV revenue incentivizes validators to collude or use sophisticated infrastructure, disadvantaging smaller validators. MEV is an invisible tax on retail DeFi users.

**Q103.** Why does MEV exist in blockchains with public mempools?

MEV exists because of three simultaneous conditions: public transaction visibility before inclusion (the mempool), the ability of block producers to freely reorder transactions, and the existence of profitable on-chain state transitions whose value depends on ordering (DEX swaps that move prices, liquidations that pay bonuses, arbitrage opportunities that close price gaps). Remove any one condition and MEV disappears or is dramatically reduced: encrypted mempools eliminate visibility, PBS with commit-reveal separates ordering power from validators, and AMMs with uniform clearing prices (like batch auctions) remove the first-mover advantage. MEV is not a flaw unique to Ethereum — it exists on any blockchain where these three conditions are present.
