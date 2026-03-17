# Layer 4: Questions

---

**Q16.** What are governance tokens and how are they used in DeFi protocols?

Governance tokens give holders voting rights over a protocol's parameters, upgrades, treasury, and future direction. Holders can propose and vote on changes like adjusting interest rate models, adding new collateral types, changing fee structures, or upgrading smart contracts. Examples: UNI (Uniswap), AAVE (Aave), MKR (MakerDAO). They also often provide economic incentives — fee sharing, staking rewards, or protocol revenue. The risk is plutocracy: large holders ("whales") can dominate votes, and voter apathy is common. Some protocols use vote-escrow (veToken) models where users lock tokens for longer periods to gain more voting power, aligning incentives with long-term protocol success.

**Q31.** What is composability in DeFi?

Composability is the ability for DeFi protocols to seamlessly interact with each other — any protocol can call any other protocol's smart contracts as building blocks, without permission. A single transaction can: borrow from Aave, swap on Uniswap, deposit into Yearn, and stake the result in Curve — all atomically. This is possible because all protocols share the same execution environment (the EVM) and expose public interfaces. Composability enables complex financial products to be built quickly by combining existing primitives, and allows flash loans to orchestrate multi-protocol operations in one block. The downside is that failures propagate: a bug in one protocol can cascade through everything that depends on it.

**Q32.** Why is composability considered a 'money lego' property?

Like LEGO bricks, each DeFi protocol is a modular, standardized piece with well-defined interfaces (token standards like ERC-20, ABI calls). Developers can snap protocols together in novel ways — just as you build complex structures from simple bricks. A stablecoin issued by one protocol becomes collateral for another, whose LP tokens are farmed in a third. This permissionless interoperability is fundamentally different from TradFi, where APIs are proprietary, integrations require legal agreements, and composing across institutions takes months. The result is an explosion of innovation: new protocols launch in days by building on existing ones rather than rebuilding infrastructure from scratch.

**Q33.** What are DeFi aggregators and how do they work?

DeFi aggregators (e.g., 1inch, Paraswap) find the best trade execution across multiple DEXs and route orders to minimize price impact and maximize output. When you want to swap 1 ETH for USDC, the aggregator queries dozens of pools and AMMs, potentially splitting your order across multiple paths (e.g., 60% through Uniswap V3, 40% through Curve) to get better rates than any single venue. They may also chain through intermediate tokens (e.g., ETH → WBTC → USDC) if that path is cheaper. Aggregators also exist for lending (yield aggregators like Yearn), which automatically move funds to the highest-yielding protocol.

**Q34.** What is a vault in DeFi protocols?

A vault is a smart contract that accepts deposits of a token or LP position and executes an automated yield strategy on behalf of depositors. In Yearn Finance, for example, you deposit USDC and the vault automatically cycles between lending protocols, liquidity pools, and farms to maximize yield — harvesting and compounding rewards periodically. Depositors receive vault shares (yTokens) representing their proportional claim. Vaults abstract complex multi-step strategies into a single deposit, and the gas costs of strategy execution are socialized across all depositors. Maker's CDP vaults work differently — they are collateral containers that allow users to mint DAI against locked collateral.

**Q35.** What are the common vulnerabilities in DeFi smart contracts?

The most common vulnerabilities are: (1) **Reentrancy** — an external contract calls back into the victim before state updates complete; (2) **Integer overflow/underflow** — arithmetic wraps around (mitigated by Solidity 0.8+ built-in checks or SafeMath); (3) **Oracle manipulation** — using manipulable spot prices for critical logic; (4) **Access control bugs** — admin functions missing `onlyOwner` modifiers; (5) **Flash loan attacks** — price or state manipulation amplified by atomic capital; (6) **Logic errors** — incorrect formulas or edge cases in financial math; (7) **Front-running/MEV** — exploiting transaction ordering; (8) **Proxy storage collisions** — in upgradeable contracts. Many billion-dollar hacks trace to one of these root causes.

**Q36.** What is a reentrancy attack?

A reentrancy attack occurs when a malicious external contract, upon receiving ETH or tokens from a victim contract, immediately calls back into the victim contract before it has updated its internal state (e.g., reducing the attacker's balance). The victim processes the callback as if the attacker still has full balance, allowing repeated withdrawals. The DAO hack (2016, $60M) was the canonical reentrancy attack. The fix is the checks-effects-interactions pattern: update all internal state before making any external calls. Alternatively, use a `ReentrancyGuard` (mutex lock) that reverts if the function is entered recursively.

**Q37.** What is the checks-effects-interactions pattern?

The checks-effects-interactions (CEI) pattern is the standard way to prevent reentrancy in Solidity. It mandates this order: (1) **Checks** — validate all preconditions (require statements, input validation, ownership checks); (2) **Effects** — update all internal state variables (deduct balances, set flags); (3) **Interactions** — make external calls (transfer ETH, call other contracts). By updating state before interacting, any reentrant callback sees the already-updated state (e.g., balance already deducted), making reentrancy economically futile. Violating this pattern — for example, transferring ETH before deducting the balance — is the root cause of most reentrancy vulnerabilities.

**Q38.** Why are audits important for DeFi protocols?

Audits involve security experts systematically reviewing smart contract code for vulnerabilities before deployment. Since DeFi contracts are immutable (or upgradeable via governance, which takes time), bugs discovered post-launch may be exploited before a fix can be deployed, causing irreversible fund loss. Audits catch common vulnerabilities (reentrancy, access control, math errors), verify business logic against the specification, and provide a public trust signal to users. However, audits are not guarantees — major audited protocols have still been exploited. Best practice: multiple independent audits, formal verification for critical math, bug bounties post-launch, and time-locks on upgrades.

**Q39.** What is protocol governance and how is it implemented?

Protocol governance is the decision-making process for changing a DeFi protocol's parameters and code. On-chain governance (e.g., Compound, Uniswap) involves token holders creating proposals, voting over a defined period, and — if quorum and approval thresholds are met — the proposal is automatically executed by a timelock contract. Off-chain governance (e.g., Snapshot) uses token-weighted voting for sentiment but requires multisig signers to execute decisions manually. Parameters governed include: fee rates, collateral factors, reward emissions, and contract upgrades. Risks include: low voter participation, plutocracy, and governance attacks (buying voting power to pass malicious proposals).

**Q40.** What are timelocks in governance systems?

A timelock is a smart contract that delays the execution of governance decisions by a mandatory waiting period (typically 24 hours to 7 days). After a governance vote passes, the proposed action is queued in the timelock, and can only be executed after the delay expires. This gives users time to review and react to potentially harmful changes — if a malicious proposal passes, users can withdraw funds before it takes effect. Timelocks are a critical safety mechanism in DeFi governance, balancing protocol adaptability with protection against rushed or malicious upgrades. Emergency multisigs sometimes have the power to cancel timelocked actions.

**Q41.** What are upgradeable smart contracts?

Upgradeable smart contracts separate storage from logic, allowing the implementation (logic) to be replaced without losing the stored state or changing the contract's address. This is done via proxy patterns: the proxy contract holds all storage and delegates all function calls to a separate logic contract. Upgrading means pointing the proxy at a new logic contract. While upgradability enables bug fixes and new features, it introduces trust assumptions — whoever controls the upgrade key can change the contract to steal funds. Best practices include: governance-controlled upgrades, timelocks, and eventually "ossifying" (making immutable) once the protocol matures.

**Q42.** What are proxy patterns used for in smart contracts?

Proxy patterns (e.g., Transparent Proxy, UUPS) enable upgradeable contracts and allow a single address to serve as the stable entry point while the underlying logic can be changed. They work by having the proxy `delegatecall` to a logic contract — the logic executes in the context of the proxy's storage. Key use cases: upgradeable protocol contracts (to fix bugs), gas optimization (deploy one logic contract shared by many proxies), and factory patterns (clones). Risks include: storage layout collisions between proxy and implementation, and the upgrade mechanism itself being a governance attack vector.

**Q44.** What are DeFi bridges and why are they risky?

Bridges allow assets to be transferred between different blockchains (e.g., Ethereum to Arbitrum). The general mechanism: lock tokens on chain A, mint wrapped tokens on chain B; burn on B to unlock on A. They are among DeFi's most exploited components — in 2022, bridge hacks totaled over $2B (Ronin: $625M, Wormhole: $320M, Nomad: $190M). Risks: bugs in the bridge's validation logic, compromised validator sets (especially in federated multisig bridges), and the complexity of cross-chain message passing. The fundamental issue is that a bridge's security is limited by the weaker of the two chains it connects, plus its own smart contract security.

**Q45.** What is wrapped crypto (e.g., wrapped tokens)?

Wrapped tokens are synthetic representations of an asset on a different blockchain or in a different standard. For example, WBTC (Wrapped Bitcoin) is an ERC-20 token on Ethereum backed 1:1 by real BTC held by a custodian — it lets Bitcoin be used in Ethereum DeFi. WETH (Wrapped ETH) is an ERC-20 version of ETH (native ETH is not ERC-20 compliant). Wrapping enables cross-chain interoperability and standardization. The risk is custodian/bridge risk: the wrapped token's value is only as good as the entity or bridge holding the underlying asset. Decentralized wrapped tokens (via bridges) reduce custodian risk but introduce smart contract risk.

**Q47.** How do DeFi protocols generate revenue?

DeFi protocols generate revenue primarily through: (1) **Trading fees** — DEXs like Uniswap charge 0.05–1% per swap, distributed to LPs (and optionally a protocol treasury); (2) **Interest spread** — lending protocols like Aave earn the difference between borrower interest rates and LP rates; (3) **Liquidation bonuses** — protocols may take a cut of liquidation penalties; (4) **Protocol fees** — a portion of trading or lending fees routed to the treasury (e.g., Uniswap's "protocol fee" switch); (5) **Yield optimization fees** — aggregators like Yearn charge performance fees (20%) and management fees (2%) on vault returns. Revenue sustains protocol development, insurance funds, and token buybacks.

**Q48.** What metrics are commonly used to evaluate a DeFi protocol (e.g., TVL)?

Key metrics: **TVL (Total Value Locked)** — total assets deposited in the protocol (measures adoption but can be inflated by leverage); **Volume** — daily/weekly trading volume (for DEXs, directly correlates to fee revenue); **Revenue** — actual fees earned by the protocol and/or LPs; **Active users** — unique wallets interacting per day/week; **P/S ratio** (Price-to-Sales) — token market cap divided by annualized revenue (lower is better value); **Liquidity depth** — price impact for standard trade sizes; **Borrow utilization** — for lending protocols, the ratio of borrowed to supplied assets (high utilization = higher rates and liquidation risk). TVL alone is misleading; revenue and user metrics provide better health signals.

**Q49.** What are the main systemic risks in the DeFi ecosystem?

The main systemic risks are: (1) **Composability cascades** — a failure in one widely-used protocol (e.g., Curve, USDC) propagates through every protocol that depends on it; (2) **Stablecoin depegging** — a $1 stablecoin dropping to $0.90 can cause mass liquidations across all lending protocols using it as collateral; (3) **Oracle failure** — incorrect price feeds cause wrong liquidations or under-collateralization; (4) **Governance attacks** — a well-funded attacker accumulates governance tokens and passes malicious proposals; (5) **Regulatory risk** — sudden regulatory action against centralized stablecoin issuers or key infrastructure; (6) **Smart contract exploits** — a single bug in widely forked code can affect dozens of protocols simultaneously.

**Q50.** How would you design a basic decentralized lending protocol?

A basic lending protocol needs: (1) **Deposit pools** — users supply assets and receive interest-bearing tokens (aTokens, cTokens) representing their share plus accrued interest; (2) **Collateral registry** — track each user's collateral deposits per asset; (3) **Borrow accounting** — track each user's debt with an interest rate that updates based on utilization (`borrowed / supplied`); (4) **Oracle integration** — use Chainlink or TWAP prices to calculate collateral values in a common unit (USD); (5) **Health factor** — continuously check if `(collateral value * LTV threshold) / debt value ≥ 1.0`; (6) **Liquidation mechanism** — allow third parties to repay debt and claim collateral at a discount when health factor < 1.0; (7) **Interest rate model** — higher utilization → higher borrow rates to incentivize more supply and less demand. Governance can set per-asset parameters.
