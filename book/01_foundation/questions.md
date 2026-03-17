# Layer 1: Questions

Answer these after completing the theory. Try without looking at notes first.

---

**Q1.** What is DeFi and how does it differ from traditional finance?

DeFi (Decentralized Finance) refers to financial services built on public blockchains using smart contracts, removing intermediaries like banks, brokers, and clearinghouses. Unlike traditional finance where institutions custody funds, gatekeep access, and operate only during business hours, DeFi protocols are open-source, permissionless, non-custodial, and globally accessible 24/7 to anyone with a wallet. The key trade-offs are: no KYC requirements, transparent on-chain logic, composability between protocols, but also no regulatory protection, smart contract risk, and full self-custody responsibility.

**Q2.** What are the main components of a DeFi ecosystem?

The core components include: decentralized exchanges (DEXs) for trading tokens, lending/borrowing protocols for credit markets, stablecoins for price stability, oracles for external price feeds, yield aggregators for optimizing returns, governance tokens for protocol control, and bridges for cross-chain asset transfers. These components compose together — for example, a yield aggregator may deposit to a lending protocol that uses an oracle-priced stablecoin as collateral.

**Q3.** What is a smart contract and why is it critical for DeFi protocols?

A smart contract is self-executing code deployed on a blockchain that automatically enforces the terms of an agreement when predefined conditions are met — no trusted third party required. For DeFi, smart contracts replace banks and brokers: they hold user funds (as liquidity pools or collateral vaults), execute swaps and loans, calculate fees, distribute rewards, and enforce liquidations — all transparently and without human intermediaries. Their immutability and determinism are what make trustless finance possible, but also what makes bugs catastrophic and irreversible.

**Q4.** What is the difference between Layer 1 and Layer 2 blockchains?

Layer 1 (L1) is the base blockchain (e.g., Ethereum, Solana) that handles consensus, data availability, and final settlement — it is the root of trust. Layer 2 (L2) is a protocol built on top of an L1 that executes transactions off-chain (more cheaply and quickly) and then posts compressed proofs or data back to the L1 for security. Examples of L2s include Optimism and Arbitrum (optimistic rollups) and zkSync (ZK rollups). L2s inherit L1 security while dramatically improving throughput and reducing gas costs.

**Q5.** How do Automated Market Makers (AMMs) work?

An AMM replaces the traditional order book with a liquidity pool — a smart contract holding reserves of two (or more) tokens. The price of each token is determined algorithmically by a formula based on the ratio of reserves, not by matching buyers and sellers. When a user swaps token A for token B, they deposit A into the pool and withdraw B; the formula recalculates the new price based on the updated reserves. Liquidity providers (LPs) deposit both tokens to earn a share of trading fees. Uniswap's constant product formula (`x * y = k`) is the most common AMM design.

**Q6.** What is the constant product formula used in AMMs?

The constant product formula is `x * y = k`, where `x` and `y` are the reserves of the two tokens in a pool, and `k` is a constant that must remain unchanged after each trade (ignoring fees). When a trader swaps token X for token Y, they add `Δx` to reserve `x`, and the contract pays out `Δy` such that `(x + Δx) * (y - Δy) = k`. This means prices move along a hyperbolic curve — larger trades cause more price impact (slippage), and the price of Y in terms of X is always `x / y`. The formula ensures pools never run dry, though it can diverge significantly from external market prices under large moves.

**Q9.** What is slippage in decentralized exchanges?

Slippage is the difference between the expected price of a trade and the actual executed price. In AMMs, slippage occurs because larger trades shift the pool's reserve ratio more, moving the price along the bonding curve. For example, swapping 1% of a pool's liquidity causes much less slippage than swapping 10%. Slippage also occurs from other transactions executing between when you submit and when your trade confirms (price impact from ordering). Users set a "slippage tolerance" — if the price moves beyond that threshold, the transaction reverts. High slippage is a major MEV attack vector (sandwich attacks).

**Q10.** What is a liquidity pool and how is it structured?

A liquidity pool is a smart contract that holds reserves of two or more tokens, enabling permissionless trading without an order book. In a standard Uniswap V2-style pool, LPs deposit equal values of both tokens (e.g., ETH and USDC), receiving LP tokens representing their proportional share of the pool. The pool charges traders a fee (e.g., 0.3%) on each swap, which accumulates in the reserves and is distributed to LPs when they withdraw. The pool's price is determined by the ratio of its reserves per the AMM formula. Anyone can create a pool or provide liquidity for any token pair.

**Q11.** How does a token swap occur in a decentralized exchange?

When a user swaps token A for token B on a DEX like Uniswap, their wallet sends a transaction calling the pool's `swap` function. The contract first calculates how much of token B the user receives based on the current reserves and the AMM formula (less a fee). It then transfers token B out to the user and records the new reserve balances. For multi-hop swaps (e.g., A → B → C), the router contract chains multiple pool calls within a single transaction. The entire process is atomic: either the swap completes fully or it reverts — no partial fills.

**Q43.** What are the main differences between centralized and decentralized exchanges?

Centralized exchanges (CEXs) like Coinbase custody user funds, maintain an off-chain order book, execute trades in their own database, require KYC, and can freeze accounts or be hacked. Decentralized exchanges (DEXs) like Uniswap are non-custodial (users keep keys), use on-chain smart contracts and AMMs, are permissionless and censorship-resistant, and are transparent. Trade-offs: CEXs offer faster execution, deeper liquidity, fiat on-ramps, and tighter spreads for major pairs; DEXs have no counterparty risk, support any ERC-20 token without listing fees, but have higher gas costs, slippage on large trades, and are subject to MEV.
