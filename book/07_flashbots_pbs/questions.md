# Layer 7: Questions

---

**Q60.** What is a bundle in MEV systems?

A bundle is a set of transactions submitted together to be included in a block atomically — all or nothing, in the exact specified order, at a specific block number. Searchers construct bundles to capture MEV: for example, [their front-run tx, victim tx, their back-run tx] for a sandwich attack, or [flash loan tx, arbitrage tx, repay tx] for an atomic arbitrage. Bundles are submitted to block builders (via Flashbots or other private relays) rather than the public mempool, preventing other bots from seeing and countering the strategy. Bundles may also include a "direct payment" to the builder/validator via a smart contract call (coinbase.transfer) to maximize inclusion probability.

**Q63.** How can protocols try to mitigate MEV?

Protocols use several approaches: (1) **Private order flow** — integrating MEV-protected RPC endpoints (MEV Blocker, Flashbots Protect) that route transactions privately, bypassing the public mempool; (2) **Batch auctions** — protocols like CoW Protocol collect orders over a time window and settle them at a single clearing price, eliminating front-running; (3) **Commit-reveal schemes** — users commit to an encrypted order first, reveal later, preventing front-running during the commitment phase; (4) **TWAP oracles** — harder to manipulate than spot prices; (5) **Slippage limits** — users set tight slippage to reduce sandwich profitability; (6) **On-chain randomness** for order selection. No approach eliminates MEV entirely — each trades off latency, UX, or decentralization.

**Q64.** What is private order flow?

Private order flow refers to transactions that are submitted directly to block builders or via private relays rather than the public mempool. When you use Flashbots Protect, MEV Blocker, or similar RPCs, your transaction is sent to a set of trusted builders without being broadcast publicly — other MEV bots cannot see it and front-run it. Searchers and market makers also route their own transactions privately to avoid being copied or countered. Private order flow reduces sandwich attacks and front-running for users, but has a centralizing effect: builders who receive more exclusive private flow construct better blocks and win the builder auction more often, concentrating power at a few dominant builders.

**Q65.** What is MEV smoothing?

MEV smoothing is the concept of distributing MEV revenue more evenly across validators over time, rather than having MEV accrue only to the validator who happens to propose a high-MEV block. In standard PoS, the proposer of the block with the most MEV wins a huge reward while others get nothing — creating a "lottery" that incentivizes sophisticated pools over solo validators. MEV smoothing proposals (like MEV-Burn, MEV redistribution pools, or execution tickets) aim to either burn the MEV (returning it to all ETH holders via deflation) or pool it and share it proportionally across all active validators. This would reduce the variance of validator rewards and level the playing field between large staking pools and solo stakers.

**Q66.** What problem does Flashbots attempt to solve?

Flashbots was created to address the "MEV crisis" where competitive MEV extraction was: (1) causing gas price wars that congested Ethereum and raised costs for all users; (2) incentivizing miners to fork the chain to steal high-value transactions (a consensus-level threat); (3) opaque and undemocratic — only sophisticated miners could capture MEV. Flashbots introduced a private auction marketplace (MEV-Geth, then MEV-Boost) where searchers submit bundles directly to miners/builders via a private relay, eliminating gas wars. This moved MEV competition off-chain, reduced on-chain congestion, and democratized access to MEV infrastructure. Flashbots also aims for MEV transparency through research and public tooling.

**Q67.** What is MEV-Geth?

MEV-Geth was Flashbots' modified Ethereum client (Geth fork) that enabled miners to receive and process bundle submissions from searchers. Before PBS and MEV-Boost, miners ran MEV-Geth to participate in the Flashbots auction: searchers submitted bundles with bids directly to miners running MEV-Geth, bypassing the public mempool. Miners would include the highest-bid valid bundles in their blocks. MEV-Geth ran from early 2021 until The Merge (September 2022), at peak handling ~90% of Ethereum blocks. It was superseded by MEV-Boost, which implements the same idea for the post-Merge proof-of-stake architecture with formal block builder auctions.

**Q68.** What is the role of a searcher in the Flashbots architecture?

Searchers are the MEV hunters — they run bots that continuously monitor the mempool and on-chain state to identify profitable MEV opportunities (arbitrage price gaps, liquidatable positions, large pending swaps to sandwich). When an opportunity is found, the searcher constructs one or more transactions that capture the profit, wraps them in a bundle with a bid (how much ETH they'll pay to the builder/validator for inclusion), and submits the bundle to Flashbots or other private relays. Searchers compete with each other: the highest bid that's valid wins inclusion. Searchers absorb the cost of opportunity analysis, bundle construction, and bid computation — builders don't need to do this work.

**Q69.** What is the role of a block builder?

Block builders receive bundles from searchers (via private relay), plus regular transactions from the public mempool, and assemble the most profitable possible block. They optimize the transaction ordering to maximize total fees (base fees + priority fees + MEV bundle bids). Builders compete with each other: each submits their completed block to validators (via MEV-Boost relay) with a bid — the validator picks the highest-bidding builder. Major builders like Beaverbuild and Titan Builder have significant advantages: access to private order flow, sophisticated simulation infrastructure, and economies of scale. Builders currently capture only a small fraction of MEV — most flows to validators via competitive bidding and to searchers as net profit.

**Q70.** What is Proposer Builder Separation (PBS)?

Proposer Builder Separation (PBS) is an architectural design where the role of choosing which transactions go in a block (building) is separated from the role of proposing that block to the network (proposing). Without PBS, validators do both: they select transactions and propose blocks. With PBS: specialized builders compete to construct the most profitable block, and the elected validator (proposer) simply chooses the highest bid from builders without seeing the block contents (to prevent stealing MEV). PBS is currently implemented via MEV-Boost (off-protocol) and is planned to be enshrined into the Ethereum protocol (ePBS). It reduces centralization pressure on validators while concentrating sophistication at the builder layer.

**Q71.** Why was PBS introduced in Ethereum?

PBS was introduced to address a critical centralization problem: if validators must search for MEV to be competitive, only large, sophisticated staking pools can afford the infrastructure — solo validators lose out. This pressure would concentrate stake among a few sophisticated entities, undermining Ethereum's decentralization. By separating building from proposing, validators can stay simple (just pick the highest bid block) while builders compete to find MEV. This allows solo validators to earn MEV revenue without any MEV-searching capability. PBS also limits validators' ability to censor transactions, since they can't see block contents before committing to include them (with proper implementation like "no peek" designs).

**Q72.** What is a Flashbots bundle and how is it structured?

A Flashbots bundle is a JSON object submitted to the Flashbots relay containing: an ordered array of signed transaction objects (raw or pre-signed), a target `blockNumber` (the bundle should be included at exactly this block), optional `minTimestamp`/`maxTimestamp` for time constraints, and a `revertingTxHashes` list specifying which transactions are allowed to revert without the whole bundle reverting. The bundle includes an implicit or explicit ETH payment to the block coinbase (builder/validator) via a smart contract call — this is the "bid." Bundles are atomic: if any non-whitelisted transaction reverts, the entire bundle is excluded. This atomicity guarantee is what enables safe multi-step MEV strategies.

**Q73.** How do bundles ensure atomic execution?

Bundles achieve atomicity through the Flashbots relay and builder infrastructure: the builder simulates the entire bundle as a unit before including it in a block. If any non-whitelisted transaction in the bundle would revert, the entire bundle is dropped. Since the block contains either all bundle transactions in order, or none of them, there's no risk of partial execution — the front-run succeeding but the back-run failing, for example. This is critical for MEV strategies that depend on a specific sequence: an arbitrage won't be included if the arbitrage itself would fail (e.g., insufficient liquidity). The atomic guarantee also means searchers don't lose gas on failed strategies since failed bundles aren't broadcast to the chain.

**Q74.** What happens if one transaction in a bundle fails?

By default, if any transaction in a Flashbots bundle reverts, the entire bundle is excluded from the block — it's as if it never existed and no gas is consumed. This is the "revert-protection" property of bundles. Searchers can optionally mark specific transactions as "allowed to revert" using the `revertingTxHashes` field, meaning those transactions can fail without invalidating the rest of the bundle. This is useful for "backrun-only" strategies where the searcher wants to execute even if a victim transaction (which they don't control) fails. Without this protection, a searcher would pay gas on every failed bundle execution — bundles make MEV strategies gas-efficient by only paying when the strategy succeeds.

**Q75.** What is MEV-Boost?

MEV-Boost is an open-source middleware developed by Flashbots that allows Ethereum validators (proposers) to outsource block construction to specialized builders via a relay network. When a validator is elected to propose a block, instead of building it themselves, they query MEV-Boost, which contacts multiple relays and builders, collects their best block bids, and selects the highest-value block header. The validator signs the header (committing to include that block), and the full block is then revealed and published. MEV-Boost implements "out-of-protocol PBS" — it achieves the same separation of proposing and building as ePBS but through external software rather than Ethereum protocol rules. Over 90% of Ethereum validators use MEV-Boost.

**Q76.** How does MEV-Boost interact with validators?

When a validator's slot approaches, their Ethereum consensus client queries the MEV-Boost sidecar software for the best available block header. MEV-Boost contacts all registered relays simultaneously, collects the highest-bid `ExecutionPayloadHeader` from each, and returns the highest-value header to the consensus client. The validator signs this header (blinded — they can't see the full transaction list) and sends it back to MEV-Boost, which forwards it to the winning relay. The relay then releases the full block to the validator to broadcast. The validator earns the builder's bid (paid directly to the fee recipient) plus the block reward. If no relay responds or bids are too low, the validator falls back to building their own block locally.

**Q77.** What advantages do builders have over validators in block construction?

Builders have: (1) **Sophisticated simulation infrastructure** — they simulate millions of bundle combinations per second to find the optimal ordering; (2) **Private order flow** — exclusive access to high-value transactions from integrated wallets, DEXs, and market makers that never appear in the public mempool; (3) **Searcher relationships** — they receive bundles from many competing searchers, selecting the most profitable; (4) **Statistical edge** — they observe patterns across millions of transactions to price opportunities more accurately; (5) **Economies of scale** — fixed infrastructure costs spread across many blocks. Validators who try to build blocks themselves can't access private order flow and lack simulation scale, so they earn significantly less MEV revenue than by outsourcing to builders.

**Q78.** What is the difference between sending a transaction to the public mempool vs Flashbots relay?

**Public mempool**: Your transaction is broadcast to all Ethereum nodes, visible to anyone within seconds. MEV bots scan it, may front-run or sandwich it, and gas price competition for inclusion is public. Your transaction may fail (reverts cost gas). **Flashbots relay**: Your transaction (or bundle) is sent privately to trusted builders/validators only, never broadcast publicly. MEV bots cannot see it and cannot front-run it. Bundles are atomic and revert-protected (no gas wasted on failures). However, you trust the relay not to censor or leak your transaction, and your transaction depends on builders' willingness to include it (rather than pure gas price competition). Most MEV-sensitive transactions (searcher bundles, large swaps) use private submission.

**Q79.** What are Flashbots relays?

Relays are trusted intermediaries in the PBS architecture that sit between searchers/builders and validators. They receive full blocks from builders, simulate and validate them (ensuring blocks are valid and bids are real), store the blocks, and provide header+bid information to validators. When a validator commits to a block header, the relay reveals the full block. Relays prevent both builders (from sending invalid blocks to validators) and validators (from stealing the MEV by peeking at the block before committing). Multiple independent relays exist (Flashbots, BloXroute, Agnostic Gnosis, Ultra Sound) to reduce single-point-of-failure risk. Relay operators can be censored or coerced, making relay diversity critical to Ethereum's censorship resistance.

**Q80.** What security risks exist in relay-based block building?

Key risks: (1) **Relay centralization** — if a few relays process most blocks, they can censor transactions (OFAC-compliant relays do this already); (2) **Relay failures** — a relay going down during a validator's slot means the validator must fall back to local block building, losing MEV revenue; (3) **Data availability attacks** — a relay can commit to a block header but withhold the full block, causing missed slots; (4) **Trust assumptions** — validators trust relays not to reveal builder strategies; builders trust relays not to steal profitable blocks; (5) **Relay equivocation** — a relay could send different block headers to different validators; (6) **Censorship via private order flow** — builders with exclusive deal flow can systematically exclude competitors' transactions. These risks motivate work on ePBS and SGX-based trusted execution.

**Q110.** Explain how a Flashbots bundle works and why atomic execution is important.

A Flashbots bundle is a signed list of transactions submitted to a builder with a target block number and a bid. The builder includes all transactions in the exact specified order at that exact block height, or excludes them entirely. Atomic execution means all-or-nothing: if any transaction fails, the whole bundle is discarded and no gas is consumed. This matters enormously for MEV strategies because: (1) a sandwich attack only makes money if front-run, victim, and back-run all execute in sequence — partial execution (front-run succeeds, back-run fails) would leave the attacker exposed; (2) arbitrage transactions that depend on a specific pool state at a specific block height are worthless if that state doesn't exist; (3) searchers can bid aggressively knowing they won't lose gas on failures. Atomicity transforms risky multi-step strategies into safe, deterministic profit extraction.
