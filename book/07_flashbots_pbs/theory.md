# Layer 7: Flashbots & Proposer-Builder Separation

---

## 1. The Problem Flashbots Solves

Before Flashbots (2020), MEV extraction was chaotic and harmful to the network:

1. **Gas wars (Priority Gas Auctions):** Searchers competed by bidding up gas prices. Dozens of bots submitting duplicate transactions for the same opportunity. Most failed — but all paid gas. This wasted block space and raised gas prices for everyone.

2. **Opaque block building:** Validators had total control and could extract MEV themselves without transparency.

3. **Network instability:** Heavy gas bidding during high-MEV events congested the network.

**What Flashbots built:** A separate, private communication channel between searchers and block builders. Instead of gas wars, searchers submit **bundles** directly to builders. The builder simulates all bundles, selects the most profitable combination, and includes them in the block.

**Result:**
- Failed txs nearly eliminated (bundles either land or are discarded before broadcast)
- Gas waste reduced
- MEV is democratized and quantified
- Transparency: Flashbots publishes MEV data

---

## 2. MEV-Geth

MEV-Geth was Flashbots' original implementation — a modified version of go-ethereum (the main Ethereum client) that added:

- A private RPC endpoint to receive bundles from searchers
- Bundle simulation: test bundles against the current chain state before including them
- Bundle ordering: select the most profitable combination of bundles
- Protection: bundles fail silently (no gas charged for failed bundles)

**Why it mattered:** Miners who ran MEV-Geth could earn significantly more than those running standard geth. This created strong economic incentives to adopt — at peak, ~90% of Ethereum hash rate ran MEV-Geth.

**Post-Merge:** MEV-Geth became obsolete. PoS validators don't run mining software. The equivalent is MEV-Boost (see below).

---

## 3. Role of a Searcher

Searchers are the "hunters" of the MEV ecosystem. They:

- Run bots that continuously monitor mempool and on-chain state
- Simulate transactions to find profitable opportunities
- Construct optimized transactions to capture the opportunity
- Package them into **bundles** with precise ordering requirements
- Submit bundles to block builders via the Flashbots relay (or direct connections)
- Specify a **bid** — the amount they're willing to pay the builder for inclusion

**What a searcher submits:**
```
Bundle {
  transactions: [tx1, tx2, tx3],    // ordered, often includes victim tx
  blockNumber: 19,500,000,          // target block
  minTimestamp / maxTimestamp,       // optional time validity window
  revertingTxHashes: [],            // txs allowed to revert without failing bundle
}
```

**Searcher economics:** If a searcher finds a $1,000 arbitrage opportunity, they bid some of it to the builder (e.g., $700), keep the rest ($300). Competition among searchers drives bids up — the equilibrium is searchers paying most of the MEV to builders/validators.

---

## 4. Role of a Block Builder

Builders specialize in constructing the most profitable possible block:

1. Receive bundles from many searchers simultaneously
2. Receive regular transactions from the public mempool
3. Simulate all possible combinations to find the optimal set
4. Construct the full block: ordered txs, correct state transitions, valid gas usage
5. Attach a **bid** (how much they'll pay the validator for this block)
6. Submit the block header to the relay

**Builder advantages:**
- Access to many searchers' bundles simultaneously (aggregation advantage)
- Specialized hardware for fast simulation
- Sophisticated ordering algorithms
- Relationships with major searchers

**Builder competition:** Multiple builders compete for the same slot. The validator's MEV-Boost software queries all builders and picks the highest-paying block. Builders who consistently produce more profitable blocks get chosen more.

**Centralization risk:** The builder market is highly centralized. A few builders (beaverbuild, Titan Builder, rsync-builder) build the majority of blocks. This is a concern for censorship resistance.

---

## 5. What is a Bundle?

A bundle is an ordered group of transactions that must be included together, in sequence, atomically.

**Key properties:**
- **Atomicity:** Either all transactions in the bundle land, or none do. (Partially — some bundles allow specific txs to revert without the bundle failing.)
- **Ordering:** The transactions must appear in the exact order specified.
- **No mempool:** Bundles bypass the public mempool. They go directly from searcher → builder. Other searchers cannot see them.
- **Failure privacy:** If a bundle isn't included, no gas is charged and no information about the bundle is revealed.

**Why bundles matter for sandwich attacks:**
```
Bundle: [
  tx1: attacker buys ETH (frontrun)
  tx2: victim's swap tx
  tx3: attacker sells ETH (backrun)
]
```
All three must execute in this exact order. If the victim's tx executes before tx1 (because someone else front-ran it), the bundle reverts — the attacker doesn't lose gas.

---

## 6. Flashbots Bundle — Structure

```json
{
  "jsonrpc": "2.0",
  "method": "eth_sendBundle",
  "params": [{
    "txs": ["0x...", "0x...", "0x..."],
    "blockNumber": "0x12A05F0",
    "minTimestamp": 0,
    "maxTimestamp": 1700000000,
    "revertingTxHashes": ["0x..."]
  }]
}
```

**Fields:**
- `txs` — array of signed raw transactions, in order
- `blockNumber` — the specific block you want inclusion in (bundles expire)
- `minTimestamp / maxTimestamp` — validity window
- `revertingTxHashes` — hashes of txs within the bundle that are allowed to revert without the whole bundle reverting

**Bundle targeting:** Searchers usually submit the same bundle targeting 3–5 consecutive blocks, since they don't know exactly which block they'll land in.

**The "tip":** Bundles typically include a transaction that pays the builder via `block.coinbase.transfer(amount)` — a direct payment to the block producer's address. This is the searcher's bid.

---

## 7. Atomic Execution — How Bundles Guarantee It

"Atomic" means: all-or-nothing. Atomicity is enforced by the EVM transaction model and bundle simulation.

**How it works:**
1. Builder receives the bundle
2. Builder simulates the entire bundle against the current state
3. If any transaction in the bundle fails (unless it's in `revertingTxHashes`), the whole bundle is discarded — not included in the block
4. If the bundle is included in a block, all transactions execute in order within the same block
5. No other transaction can be inserted between bundle transactions

**Why atomicity is critical:**
- For sandwich attacks: if the victim's tx somehow executed first (by another frontrunner), the backrun would be at a loss. Atomicity ensures the order is guaranteed or nothing happens.
- For arbitrage: if tx1 buys on DEX A and tx2 sells on DEX B, but someone else takes the DEX B liquidity between tx1 and tx2, you lose money. Atomicity prevents this.
- For liquidations: if the position's health factor recovers between detecting it and liquidating, you'd fail. Atomicity ensures the liquidation either works or reverts.

---

## 8. What Happens When One Tx in a Bundle Fails?

**Default behavior:** The entire bundle is invalid and not included.

**With `revertingTxHashes`:** You can specify certain transactions that are allowed to revert. The bundle will still land even if those specific txs fail.

**Use case:** Searchers sometimes include a third-party's pending transaction in their bundle (like the victim tx in a sandwich). This tx might fail for unrelated reasons. By putting it in `revertingTxHashes`, the searcher's bundle still lands even if the victim tx reverts.

**Important nuance for sandwich attacks:**
- The victim tx might have a tight slippage setting and revert if the attacker's frontrun moves the price too much
- If the victim tx is in `revertingTxHashes`, the sandwich bundle still lands — but the backrun would be doing nothing useful (since no victim swap happened). Good searchers detect this and calculate whether the backrun is still profitable.

---

## 9. Public Mempool vs Flashbots Relay — The Difference

| | Public Mempool | Flashbots Relay |
|---|---|---|
| Visibility | Visible to everyone | Visible only to the relay and builder |
| Failed txs | Pay gas even if tx fails | No gas for unincluded bundles |
| Front-run risk | High — anyone can see and front-run | Low — private until included in block |
| Ordering guarantees | None | Bundle ordering guaranteed |
| Who sees it | Every Ethereum node | Only relay operators and builders |
| Latency | Immediate broadcast | Slight delay (relay processing) |

**For regular users:** Sending to the public mempool is simple but exposes you to MEV bots. Flashbots Protect is a free RPC endpoint that forwards user txs privately.

**For searchers:** Sending to Flashbots relay means your strategy stays secret until the block is proposed. No one can copy your bundle.

---

## 10. Flashbots Relays — What They Are

A relay is a trusted intermediary between builders and validators.

**Problem without relays:** Builders don't want to reveal the full block contents to validators before the validator commits to including it (validators could steal the MEV). Validators don't want to commit to an unknown block (could contain invalid txs). Chicken-and-egg problem.

**What relays do:**
1. Receive the full block from a builder
2. Verify it's valid (correct execution, correct bid)
3. Expose only the block header (not contents) to the validator
4. The validator commits to the block header (signs it)
5. Only after commitment does the relay reveal the full block to the validator to broadcast

**Trust model:** Both sides trust the relay:
- Builder trusts the relay not to leak block contents before commitment
- Validator trusts the relay that the block is valid (not invalid, not missing the promised payment)

**Relay centralization:** Flashbots runs the dominant relay. This is a centralization risk — if Flashbots censors certain transactions, they can affect what lands in blocks across most of Ethereum. Alternative relays exist (BloXroute, Agnostic) to mitigate this.

---

## 11. Proposer Builder Separation (PBS)

PBS is the separation of two roles that were previously combined:
- **Proposer (validator):** Proposes the block to the network. Responsible for consensus.
- **Builder:** Constructs the block contents. Responsible for transaction ordering and MEV extraction.

**Why separate them?**
- Block building is a specialized, capital-intensive skill (fast hardware, many data connections, complex algorithms)
- Validators should not need to be MEV experts to participate in consensus
- Separation allows validators to remain lightweight and numerous (decentralized), while builders specialize

**Current state (external PBS via MEV-Boost):** PBS is not yet enshrined in Ethereum's protocol. It's implemented "externally" via MEV-Boost software. Validators voluntarily run MEV-Boost to access builder-constructed blocks.

**Future state (enshrined PBS):** The Ethereum roadmap includes baking PBS into the protocol itself, with cryptographic guarantees rather than trust in relays.

---

## 12. Why PBS Was Introduced

**Without PBS in a PoS world:**
- Validators who extract MEV themselves earn more than those who don't
- Rich validators can afford MEV infrastructure; small validators can't
- This creates pressure toward validator centralization (large staking pools dominate)
- Large validators could also use their MEV advantage to gain more stake over time

**With PBS:**
- Any validator can run MEV-Boost with one line of config
- All validators get access to the same builder market
- MEV rewards are bid by builders and shared with all validators proportionally (by slot)
- Decentralization of the validator set is preserved

**PBS democratizes MEV rewards:** A solo validator with 32 ETH earns the same MEV premium per slot as a large staking pool, because they both just pick the highest-paying builder block.

---

## 13. MEV-Boost — What It Is

MEV-Boost is open-source software (by Flashbots) that validators run alongside their consensus client. It implements external PBS.

**What it does:**
1. When a validator is selected to propose a block, MEV-Boost queries multiple relays
2. Each relay returns a block header and a bid (how much the builder will pay)
3. MEV-Boost picks the highest bid
4. Validator signs the block header (commitment)
5. MEV-Boost reveals the choice to the relay, which releases the full block
6. Validator broadcasts the block

**The validator earns:** the builder's bid payment, on top of the normal block reward.

**Adoption:** At peak, ~95% of Ethereum validators used MEV-Boost. Even validators that don't want to deal with MEV extraction can passively earn MEV rewards.

---

## 14. How MEV-Boost Interacts with Validators

```
Slot begins (12 seconds)
↓
MEV-Boost queries all registered relays
↓
Relays return: (block_header, bid_amount, builder_pubkey)
↓
MEV-Boost selects highest bid
↓
Validator signs block header → sends signed header back to relay
↓
Relay verifies signature, releases full block to validator
↓
Validator broadcasts full block to the network
↓
Builder pays the bid to validator via a tx in the block
```

**Timing constraints:** This entire flow must complete within ~4 seconds (before the block deadline). Relays and builders must be fast.

---

## 15. Builder Advantages Over Validators in Block Construction

Builders have specialized advantages:
- **Access to many searcher bundles:** Builders receive bundles from dozens of searchers. Validators building their own blocks only see the public mempool.
- **Simulation infrastructure:** Fast hardware to simulate thousands of bundle combinations per second
- **Private order flow:** Agreements with wallets, protocols, or large traders to receive their transactions before they hit the public mempool
- **Cross-domain optimization:** Optimize across hundreds of bundles simultaneously to find the most profitable combination

**Result:** Builders consistently construct blocks worth significantly more than what a validator building from the public mempool could achieve. The extra value is shared: builder keeps some, pays the rest to the validator.

---

## 16. Security Risks in Relay-Based Block Building

1. **Relay trust:** Both builders and validators must trust the relay. A malicious relay could:
   - Leak block contents before commitment (let validators steal MEV)
   - Lie about block validity (cause validators to include bad blocks)
   - Censor specific transactions
   - Front-run builders by copying their strategies

2. **Relay single point of failure:** If the dominant relay goes down, validators fall back to building blocks locally (missing MEV) or have no blocks to propose.

3. **Builder centralization:** A dominant builder could censor transactions or extract MEV unfairly.

4. **Payment griefing:** A builder could construct a block with a large promised payment but deliver a block where the payment fails. The validator proposed a block but didn't get paid.

5. **Time-bandit attacks:** A validator who sees a highly profitable block might be tempted to re-propose the same slot with a different block (reorg). Finality in PoS makes this much harder than in PoW.

---

## 17. MEV Mitigation Strategies

**For users:**
- Use Flashbots Protect RPC → txs go private, never hit public mempool
- Set minimum slippage tolerance → less attractive sandwich target
- Use CoW Protocol → batch auctions that are structurally sandwich-resistant
- Use aggregators that route privately

**For protocols:**
- Batch auctions (CoW Protocol, Gnosis Auction): txs from the same batch get the same price → no reordering advantage
- Commit-reveal schemes: hide tx details until execution (complex, introduces latency)
- TWAP orders: spread large trades over time to reduce per-trade impact
- Private mempools: protocol-level opt-in to private tx submission

**For the ecosystem (PBS/Flashbots approach):**
- Separate block building from validation → reduce validator MEV extraction power
- Make MEV transparent and measurable via dashboards
- Fair ordering protocols (research ongoing)

---

## 18. Private Order Flow

Private order flow (POF) = transactions that bypass the public mempool and go directly to a builder or searcher.

**Who generates POF:**
- Wallets (e.g., MetaMask's "MetaMask Swaps" sends txs to select builders)
- Protocols that route user txs through private channels
- Large traders (OTC desks) who don't want their orders visible

**Why builders want POF:**
- Earlier visibility = more time to optimize around the transaction
- POF may include lucrative MEV opportunities
- Builders with exclusive POF have an advantage over competitors

**Concern:** If most txs go through private channels to a small number of builders, the system becomes centralized. Builders with exclusive POF can dominate block production.

---

## 19. MEV Smoothing

MEV earnings are lumpy — some blocks have $0 MEV, others have $100,000+ MEV. This creates variance in validator earnings.

**MEV smoothing** = mechanisms to average out MEV rewards across validators over time.

**Approaches:**
- **MEV-Boost (existing):** All validators using MEV-Boost participate in the builder market. Each validator's slot earns whatever MEV that block contained. Partially smooths via market competition.
- **MEV burn (proposed):** Instead of paying MEV to the proposing validator, burn it. This benefits all ETH holders equally through deflation. Removes the incentive for validators to do anything special.
- **Distributed block building (research):** Move block construction to a decentralized network where many validators share MEV from each block.

**Why it matters:** Without smoothing, high-MEV slots are very valuable. Validators might try to manipulate which slot they get, creating consensus instability.
