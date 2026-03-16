# Layer 4: DeFi Ecosystem — Governance, Composability, Security, Infrastructure

---

## 1. Governance Tokens and Protocol Governance

Most DeFi protocols are not fully decentralized — they have parameters that need updating (fee rates, supported assets, risk limits). Governance tokens give holders the right to vote on these changes.

**How it works:**
1. A proposal is created on-chain (or via Snapshot off-chain for gas efficiency)
2. Token holders vote proportionally to their holdings
3. If quorum is reached and vote passes, the change is executed (often via a timelock)

**Examples:**
- UNI (Uniswap) — vote on fee tiers, treasury spending, supported chains
- AAVE — vote on adding new collateral assets, changing risk parameters
- MKR (MakerDAO) — vote on DAI stability fees, collateral types

**Problems:**
- **Plutocracy:** Rich holders dominate. Whales can pass anything.
- **Voter apathy:** Most token holders don't vote. Quorum is often not reached.
- **Token concentration:** VCs and team hold most tokens, making governance theater.
- **Governance attacks:** Buy enough tokens to pass a malicious proposal (e.g., drain the treasury).

---

## 2. Timelocks in Governance

A timelock is a smart contract that delays execution of a passed governance vote by a fixed period (e.g., 48 hours, 7 days).

**Why it exists:**
- Gives users time to react to malicious proposals before they execute
- If a governance attack passes (e.g., "send all treasury to attacker"), users have time to see it and withdraw funds before the proposal executes
- Signals commitment to decentralization and trustworthiness

**Flow:**
```
Vote passes → queued in timelock → 48-hour delay → executed
```

**Tradeoff:** Slower response to urgent issues (e.g., can't patch a bug instantly). Some protocols have emergency multisigs that can pause the protocol without a governance vote.

---

## 3. Composability — "Money Legos"

Composability means that any DeFi protocol can interact with any other DeFi protocol without permission, because they share the same open blockchain.

**"Money legos"** — like LEGO bricks, each protocol is a primitive that can be snapped together. No API key, no business agreement, no whitelist needed.

**Examples:**
- A **yield aggregator** (Yearn) deposits into a **lending protocol** (Aave) which uses an **oracle** (Chainlink) — three protocols composed together
- A **DEX aggregator** (1inch) routes a swap across multiple **DEXs** (Uniswap, Curve, Balancer) in one transaction
- A strategy might: borrow DAI from Maker → deposit into Curve pool → stake Curve LP tokens in Convex → earn CRV + CVX rewards. Four protocols, one user action.

**The risk of composability:** If any one protocol in a chain is exploited, the entire stack is affected. Protocols that depend on each other create systemic interdependencies.

---

## 4. DeFi Aggregators

Aggregators query multiple protocols and route users to the best outcome automatically.

**DEX aggregators (1inch, Paraswap):**
- Split a trade across multiple pools to minimize slippage
- "Optimal routing" — sometimes routing through 3 pools gives a better price than 1
- Users get better prices without manually checking every DEX

**Yield aggregators (Yearn Finance):**
- Automatically move funds between lending protocols to earn the best yield
- Auto-compound rewards
- Abstract away the complexity of yield farming

**How routing works:**
User wants to swap 100 ETH for USDC. 1inch finds:
- Route 1: Uniswap V3 (ETH/USDC) — price: $2,001
- Route 2: 60% Uniswap + 40% Curve — blended price: $2,003
- Route 2 wins. The split reduces price impact.

---

## 5. Vaults

A vault is a smart contract that accepts a token, deploys it into a yield-generating strategy, and returns a "receipt token" (e.g., yUSDC).

**Basic mechanics:**
1. User deposits USDC into vault
2. Vault receives USDC, returns yUSDC (represents a share of the vault)
3. Vault deploys USDC into the highest-yielding strategy (lending, LP, etc.)
4. Over time, yUSDC appreciates vs USDC (your share is worth more USDC)
5. User withdraws: burns yUSDC, receives USDC + earnings

**Why vaults exist:** Gas costs make it impractical for small depositors to manually manage yield strategies. Vaults pool capital and spread gas costs across all depositors.

---

## 6. Common Smart Contract Vulnerabilities

1. **Reentrancy** — the #1 historical bug (see below)
2. **Integer overflow/underflow** — before Solidity 0.8, arithmetic could wrap around; e.g., 0 - 1 = 2^256. Now auto-checked.
3. **Access control** — missing `onlyOwner` or role checks on privileged functions
4. **Uninitialized proxies** — if a proxy's implementation isn't initialized, anyone can call `initialize()` and take ownership
5. **Oracle manipulation** — using manipulable price sources (covered in Layer 3)
6. **Flash loan exploits** — using flash loans to amplify attacks
7. **Frontrunning** — transactions can be seen and frontrun in the mempool
8. **Signature replay attacks** — reusing a valid signature in a different context
9. **Rounding errors** — integer division truncates; can be exploited to drain small amounts repeatedly
10. **Logic bugs** — protocol-specific incorrect assumptions in business logic

---

## 7. Reentrancy Attack

The most famous smart contract bug — responsible for The DAO hack (2016, $60M), and many others.

**The concept:** A contract calls an external contract (e.g., to send ETH). Before the first call finishes, the external contract calls back into the original contract. If the original contract hasn't updated its state yet, the attacker can drain funds.

**Vulnerable code (pseudocode):**
```
function withdraw() {
    uint amount = balances[msg.sender];
    // Step 1: Send ETH (calls attacker's contract)
    msg.sender.call{value: amount}();
    // Step 2: Update balance (NEVER REACHED in attack)
    balances[msg.sender] = 0;
}
```

**Attack flow:**
1. Attacker deposits 1 ETH → `balances[attacker] = 1 ETH`
2. Attacker calls `withdraw()`
3. Contract sends 1 ETH to attacker's contract
4. Attacker's contract has a `receive()` function that immediately calls `withdraw()` again
5. `balances[attacker]` is still 1 ETH (not yet zeroed) → sends another 1 ETH
6. Loop repeats until the victim contract is drained

---

## 8. Checks-Effects-Interactions Pattern

The fix for reentrancy. Always follow this order in any function:

1. **Checks** — validate inputs, permissions, state conditions (require statements)
2. **Effects** — update all state variables (balances, flags, etc.)
3. **Interactions** — call external contracts, send ETH

**Fixed code:**
```
function withdraw() {
    uint amount = balances[msg.sender];
    // Checks
    require(amount > 0);
    // Effects (state updated BEFORE external call)
    balances[msg.sender] = 0;
    // Interactions
    msg.sender.call{value: amount}();
}
```

Now if the attacker reenters, `balances[attacker] = 0` so the second `withdraw()` sends nothing.

**Reentrancy guard:** Many protocols also use a mutex:
```
bool private locked;
modifier noReentrant() {
    require(!locked);
    locked = true;
    _;
    locked = false;
}
```

---

## 9. Why Audits Matter

An audit is a manual review of smart contract code by security experts before deployment.

**Why it's critical:** Smart contracts are immutable (usually). A bug in production can be exploited at any time and there's no way to call the bank and reverse the transaction. You must find bugs before deployment.

**What auditors look for:**
- All vulnerabilities listed in Section 6
- Business logic errors
- Gas optimizations
- Compliance with intended behavior

**What audits don't guarantee:**
- Audits are not a security guarantee. They reduce risk. Many audited protocols have been hacked. Auditors miss things.
- Auditors only review the code as written. Novel exploit combinations may not be anticipated.

**Best practice:** Multiple independent audits + bug bounty program + formal verification for critical components.

---

## 10. Upgradeable Contracts and Proxy Patterns

**The problem:** Once deployed, smart contracts are immutable. You can't patch a bug. But protocols need to evolve.

**Solution: Proxy pattern.** Separate the contract into two parts:
- **Proxy contract** — holds all the state (balances, etc.) and storage. Its address never changes. Users interact with this.
- **Implementation contract** — holds the logic (functions). Can be swapped out.

When a user calls the proxy, the proxy **delegates** the call to the implementation (using `DELEGATECALL`). `DELEGATECALL` runs the implementation's code but in the proxy's storage context.

To upgrade: deploy a new implementation, point the proxy at it.

**Common patterns:**
- **Transparent proxy (OpenZeppelin):** Admin calls go to proxy, user calls go to implementation
- **UUPS (Universal Upgradeable Proxy Standard):** Upgrade logic is in the implementation itself
- **Beacon proxy:** Many proxies point to one "beacon" that holds the implementation address; upgrade the beacon, all proxies upgrade

**Risks:** If the upgrade mechanism is centralized (one multisig can upgrade), the protocol can be rug-pulled by deploying malicious logic.

---

## 11. DeFi Bridges and Why They Are Risky

A bridge allows you to move assets between two blockchains (e.g., ETH from Ethereum to Arbitrum).

**How they work (simplified):**
1. You deposit ETH on Ethereum into a bridge contract
2. A relayer observes this deposit
3. Wrapped ETH (wETH) is minted on Arbitrum and sent to your address
4. When bridging back, wETH is burned on Arbitrum, ETH is released on Ethereum

**Why they are risky — they hold enormous value:**
A bridge's Ethereum-side contract can hold billions of dollars in locked assets. This makes them the highest-value targets in crypto.

**Attack vectors:**
- Exploiting the bridge smart contract (Ronin bridge: $625M, Wormhole: $320M, Nomad: $190M)
- Compromising the relayer/validator set
- Signature verification bugs (accepting fake proofs)

Bridges are the #1 source of DeFi hacks by dollar amount.

---

## 12. Wrapped Tokens

A wrapped token is a tokenized representation of an asset from another chain or format.

**WBTC (Wrapped Bitcoin):** BTC doesn't exist on Ethereum. A custodian holds real BTC, mints WBTC (an ERC-20) 1:1. Now BTC can be used in Ethereum DeFi.

**WETH (Wrapped ETH):** ETH itself is not an ERC-20 token (it predates the standard). WETH is ETH wrapped into ERC-20 format so it can be used in DeFi protocols uniformly. You deposit ETH, get WETH 1:1. Always redeemable.

**Why wrapping is needed:** DeFi protocols are built to handle ERC-20 tokens. Native ETH has slightly different behavior. WETH normalizes it.

---

## 13. How DeFi Protocols Generate Revenue

| Protocol type | Revenue source |
|---|---|
| DEX (Uniswap) | % of trading fees (protocol fee, if enabled) |
| Lending (Aave) | Spread between borrow rate and supply rate |
| Stablecoin (MakerDAO) | Stability fee (interest on DAI loans) |
| Yield aggregator (Yearn) | Performance fee (% of profits generated) |
| Derivatives | Trading fees, liquidation fees |

**Protocol fee vs LP fee:** In Uniswap, trading fees go entirely to LPs by default. The protocol can enable a "protocol fee" that takes a portion (e.g., 1/6 of the LP fee), sending it to the DAO treasury. This is governed by UNI holders.

---

## 14. Key Metrics — TVL and Others

**TVL (Total Value Locked):** The USD value of assets deposited into a protocol. The primary metric for DeFi protocol size. Limitations: double-counting (same assets in multiple protocols), TVL can spike due to token price not new deposits.

**Volume:** Total trading volume in a period. DEX revenue is proportional to this.

**Revenue / Protocol fees:** Actual cash flows, more meaningful than TVL for valuation.

**Unique users / active addresses:** Growth metric.

**Bad debt:** Uncollateralized debt that can't be liquidated. Sign of protocol insolvency risk.

**Liquidation volume:** High during market stress. Shows protocol working as intended (if liquidations happen before health factor < 1).

---

## 15. Systemic Risks in DeFi

1. **Cascading liquidations** — a price crash triggers mass liquidations, which push prices lower, triggering more liquidations
2. **Composability contagion** — one protocol exploited → other protocols that depend on it fail
3. **Stablecoin depeg** — if DAI or USDC loses its peg, every protocol using it as collateral or a unit of account is affected
4. **Oracle failure / manipulation** — wrong prices propagate across every protocol using that oracle
5. **Governance attacks** — a well-funded attacker acquires governance tokens to drain treasuries
6. **Regulatory risk** — governments can ban access, pressure centralized stablecoin issuers to freeze assets
7. **Smart contract monoculture** — many protocols fork the same code; one bug affects dozens of forks simultaneously

---

## 16. Designing a Basic Decentralized Lending Protocol

**Core components:**

**1. Collateral management**
- Accept whitelisted ERC-20 tokens as collateral
- Track each user's deposited collateral and its current USD value (via oracle)

**2. Borrow logic**
- User specifies how much to borrow (must be < LTV × collateral value)
- Protocol mints/transfers the borrowed asset to the user
- Track user's debt including accrued interest

**3. Interest accrual**
- Interest accrues every block (or per second)
- Interest rate model: as utilization (borrowed/deposited) rises, rates rise to incentivize more deposits
- Typical model: base rate + utilization × slope. After 80% utilization, rate spikes sharply.

**4. Liquidation**
- Any external address can trigger liquidation when health factor < 1
- Liquidator repays debt, receives collateral at discount
- Incentive must be large enough to cover gas + risk

**5. Oracle**
- Use Chainlink for prices
- TWAP as backup / manipulation resistance

**6. Governance**
- Token holders vote on: supported assets, LTV ratios, liquidation thresholds, fee parameters
- Timelock on all changes

**Key risk to design around:** Ensure liquidations are profitable before the protocol becomes insolvent. The gap between LTV and liquidation threshold must exceed expected gas costs + price volatility during a block.
