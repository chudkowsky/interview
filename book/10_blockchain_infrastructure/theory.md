# Layer 10: Blockchain Backend Infrastructure

---

## 1. Consensus Mechanisms

Consensus is how a distributed network of nodes agrees on the state of the blockchain without a central authority.

### Proof of Work (PoW)
- Miners compete to solve a computationally expensive puzzle (SHA-256 hash below a target)
- Winner adds the block and gets the block reward
- Security comes from the cost of computation — attacking requires 51% of total hash power
- **Downside:** Wastes enormous energy; slow finality (Bitcoin: 6 confirmations ≈ 60 minutes)
- **Used by:** Bitcoin

### Proof of Stake (PoS)
- Validators lock up ("stake") cryptocurrency as collateral
- A validator is pseudorandomly selected to propose a block (weighted by stake)
- Other validators attest (vote) to the block's validity
- Misbehavior is punished by "slashing" — destroying part of the stake
- **Downside:** "Rich get richer" criticism; complex implementation
- **Used by:** Ethereum (post-Merge), Solana, Cosmos

### BFT (Byzantine Fault Tolerance) / Tendermint
- Used in many L1s and L2 sequencers
- Validators vote in rounds — a block is finalized when 2/3+ validators agree
- **Instant finality** — once a block is committed, it cannot be reverted
- **Downside:** Requires known validator set; doesn't scale to thousands of validators
- **Used by:** Cosmos, Celestia, many app-chains

### Key difference: Probabilistic vs Deterministic Finality
- **PoW / Ethereum PoS:** Finality is probabilistic — a block buried under many blocks is practically irreversible, but theoretically reversible
- **BFT:** Finality is deterministic — once 2/3 of validators sign, it's final. Period.

---

## 2. Transaction Lifecycle

Understanding how a transaction goes from user intent to on-chain finality:

```
User signs tx
     ↓
Broadcast to mempool (public pool of pending txs)
     ↓
Validators/builders observe mempool
     ↓
Builder selects txs, orders them, builds a block
     ↓
Block proposed to validator network
     ↓
Validators attest / vote
     ↓
Block finalized (included in canonical chain)
     ↓
Receipts available (logs, events, gas used)
```

**Mempool:** A shared, public waiting room for unconfirmed transactions. Anyone can read it — this is the source of MEV.

**Gas:** The fee paid to compensate validators for computation. Users set:
- `maxFeePerGas` — max willing to pay total
- `maxPriorityFeePerGas` — tip to validator for inclusion priority

**Nonce:** A sequential counter per account. Prevents replay attacks. Each tx must have nonce = current account nonce or it's rejected.

**Finality on Ethereum:**
- A block is "safe" after 1 slot (~12s)
- A block is "finalized" after ~2 epochs (~12.8 minutes) — 2/3 validators have attested
- For most apps: 12-64 block confirmations is sufficient (1–13 minutes)

---

## 3. Account Model vs UTXO Model

**UTXO (Unspent Transaction Output) — Bitcoin:**
- No accounts. Only "coins" (UTXOs) that have never been spent
- A transaction consumes UTXOs as inputs and creates new UTXOs as outputs
- Your "balance" = sum of all UTXOs you control
- Privacy benefit: each tx looks different; harder to trace full history
- Smart contracts are extremely hard to implement in UTXO model

**Account Model — Ethereum, Starknet:**
- Explicit accounts with a balance and nonce
- A transaction decrements sender's balance, increments receiver's balance
- State is stored in a global state trie (key-value: address → {balance, nonce, code, storage})
- Intuitive, easy to reason about, natural for smart contracts
- **Downside:** Sequential nonce means parallelism is hard; full history is easily traceable

**Why it matters for backend:** Account model requires careful nonce management when sending many transactions concurrently. UTXO allows more parallelism but requires UTXO selection algorithms.

---

## 4. Account Abstraction (AA)

Traditional Ethereum: only EOAs (Externally Owned Accounts) can initiate transactions. Smart contracts can only be called.

**Account Abstraction:** Any account can define its own validation logic. The account IS a smart contract.

**What this enables:**
- **Social recovery** — lose your key? Trusted parties can restore access
- **Multisig by default** — require 2/3 signers for every transaction
- **Gas sponsorship** — a third party pays gas on behalf of the user (gasless UX)
- **Session keys** — a temporary key with limited permissions (e.g., only interact with one game contract)
- **Batch transactions** — many operations in a single "transaction"
- **Custom signature schemes** — use passkeys, hardware keys, WebAuthn instead of secp256k1

**ERC-4337 (Ethereum):** Implements AA without protocol changes via a special `EntryPoint` contract and `UserOperation` objects (pseudo-transactions). A `Bundler` collects UserOperations and submits them.

**Starknet:** AA is native — every account is a smart contract from day one. No EOAs exist.

**Why it matters for backend:** Wallet infrastructure companies (like 4ire's likely clients) build on top of AA. Understanding session keys, bundlers, paymasters is core to their work.

---

## 5. MPC and Multisig Wallets

These are the two main approaches to **institutional key management** — relevant to 4ire's "preferred qualifications."

### Multisig (Multi-Signature)
- A smart contract requires M-of-N signatures to execute a transaction
- Example: 3-of-5 multisig — 3 out of 5 keyholders must sign
- **On-chain:** The logic is enforced by the contract (Gnosis Safe is the standard)
- **Pros:** Transparent, auditable, battle-tested
- **Cons:** All signers are visible on-chain; each signature increases gas cost; requires coordination

### MPC (Multi-Party Computation)
- The private key is never assembled in one place — it's split into "shares" using cryptographic protocols (e.g., Shamir's Secret Sharing, threshold ECDSA)
- M-of-N parties each hold a share and jointly sign without ever revealing their share to each other
- The resulting signature looks like a normal single-key signature on-chain
- **Pros:** Privacy (no on-chain multisig footprint); cheaper gas; works without smart contracts
- **Cons:** Complex cryptography; requires secure communication between parties; harder to audit

**When to use what:**
- **Multisig:** DAO treasuries, on-chain governance, when transparency is required
- **MPC:** Institutional custody (Fireblocks, Anchorage), exchange hot wallets, when privacy or gas efficiency matters

---

## 6. Distributed Systems Fundamentals

### CAP Theorem
A distributed system can guarantee only 2 of 3:
- **Consistency (C):** Every read returns the most recent write
- **Availability (A):** Every request gets a response (not necessarily the latest data)
- **Partition tolerance (P):** System works even if network splits occur

Since network partitions always happen in real systems, you choose between **CP** (consistent but may be unavailable during partition) or **AP** (available but may return stale data).

**Blockchain context:** Most blockchains are CP — during a network partition, honest nodes won't finalize conflicting blocks (consistency), but may stop producing blocks (unavailable).

### Eventual Consistency
A weaker guarantee: if no new updates are made, all replicas will eventually converge to the same value. Used when availability > consistency (e.g., DNS, DynamoDB defaults, CRDTs).

### Replication Strategies
- **Leader-follower:** One node accepts writes, replicates to followers. Followers serve reads.
- **Multi-leader:** Multiple nodes accept writes. Conflict resolution needed.
- **Leaderless (Dynamo-style):** Any node can accept writes. Quorum reads/writes for consistency.

### Consensus in Distributed Systems (Raft / Paxos)
- Used for replicated state machines (databases, coordinator services)
- Raft: leader elected, log entries replicated to majority before committing
- Simpler than Paxos; same guarantees
- **Blockchain is a generalization of this** — but with open/permissionless validator sets

---

## 7. Microservices Architecture

### Core Patterns
- **API Gateway:** Single entry point for clients; routes to downstream services
- **Service Discovery:** Services register themselves; clients look up addresses dynamically (Consul, Kubernetes DNS)
- **Circuit Breaker:** If a downstream service fails repeatedly, stop calling it temporarily (fail fast, prevent cascade failures)
- **Saga Pattern:** Distributed transactions across multiple services using compensating transactions (no 2PC)
- **Event-driven:** Services communicate via events (Kafka) rather than direct calls — decouples producers from consumers

### Synchronous vs Asynchronous Communication
- **Synchronous (REST, gRPC):** Caller waits for response. Simple, but couples services.
- **Asynchronous (Kafka, RabbitMQ):** Producer sends event, consumer processes later. Decoupled, resilient, but harder to debug.

### gRPC vs REST
| | REST | gRPC |
|---|---|---|
| Protocol | HTTP/1.1, JSON | HTTP/2, Protobuf |
| Schema | Optional (OpenAPI) | Required (.proto) |
| Performance | Moderate | High (binary, streaming) |
| Browser support | Native | Requires proxy |
| Use case | Public APIs, simple services | Internal microservices, high throughput |

---

## 8. Infrastructure: Docker, Kubernetes, Helm

### Docker
- Packages application + dependencies into an image
- Container is a running instance of an image — isolated, reproducible
- Key commands: `docker build`, `docker run`, `docker push`
- **Dockerfile:** Instructions to build the image layer by layer

### Kubernetes (K8s)
- Orchestrates containers across a cluster of machines
- Key concepts:
  - **Pod:** Smallest unit — one or more containers sharing network/storage
  - **Deployment:** Manages replicas of a pod; handles rolling updates
  - **Service:** Stable DNS name + load balancer for a set of pods
  - **ConfigMap / Secret:** Configuration and sensitive values injected into pods
  - **Namespace:** Logical isolation within a cluster
- **Why it matters:** Handles scaling, self-healing (restarts failed pods), rolling deployments

### Helm
- Package manager for Kubernetes
- A **chart** is a collection of K8s manifests templated with values
- `helm install`, `helm upgrade`, `helm rollback`
- Allows parameterizing deployments across environments (dev/staging/prod)

---

## 9. Blockchain Node Infrastructure

### Node Types
- **Full node:** Downloads and validates every block and transaction. Maintains full state.
- **Archive node:** Full node + stores all historical state (needed for `eth_getStorageAt` at old blocks). Very large (Ethereum: 10TB+).
- **Light node:** Only downloads block headers; trusts full nodes for state queries.

### RPC APIs
Standard JSON-RPC interface exposed by nodes:
- `eth_blockNumber` — latest block
- `eth_getBalance` — account balance
- `eth_call` — simulate a contract call (no tx, no gas cost)
- `eth_sendRawTransaction` — broadcast signed tx
- `eth_getLogs` — query event logs by filter
- `eth_getStorageAt` — read raw contract storage slot

**Starknet equivalents:** `starknet_getStorageAt`, `starknet_call`, `starknet_addInvokeTransaction`

### Indexers
Nodes serve raw blockchain data; indexers transform it into queryable databases:
- **The Graph:** Subgraphs index events and expose GraphQL APIs
- **Torii (Dojo):** Indexes Dojo game state from Starknet events
- **Ponder, Envio:** General-purpose EVM indexers

### Rate Limiting and Reliability
- Public RPC endpoints (Infura, Alchemy) have rate limits — use exponential backoff + retry
- For production: run your own node or use dedicated RPC (no rate limits)
- Implement circuit breakers when RPC is unreliable

---

## 10. Security Best Practices for Blockchain Backend

### Private Key Management
- Never store private keys in environment variables in production — use HSM (Hardware Security Module) or KMS (AWS KMS, GCP KMS)
- For signing transactions programmatically: key should live in a dedicated signer service
- Rotate keys regularly; use separate keys for different environments

### Smart Contract Interaction
- Always validate on-chain state before trusting cached/off-chain data
- Use `eth_call` to simulate before `eth_sendRawTransaction` — catch reverts before paying gas
- Check return values — some contracts return `false` instead of reverting on failure (old ERC-20 pattern)
- Never trust user-supplied contract addresses — whitelist known contracts

### Common Attack Vectors in Backend
- **Reentrancy via callbacks:** If your backend holds state between RPC calls, an attacker replaying callbacks can corrupt it
- **Nonce race conditions:** Two concurrent goroutines/threads sending txs can use the same nonce — implement nonce manager with mutex
- **Mempool monitoring:** Assume all txs you broadcast are visible to MEV bots immediately
- **Signature replay:** Always include chainId and nonce in signed messages to prevent replay on other chains/nonces

### Nonce Management Pattern
```
NonceManger:
  - tracks current nonce per account
  - provides next nonce atomically (mutex-protected)
  - on tx failure: detect if nonce was already used or needs retry
  - on success: increment local nonce (don't wait for RPC confirmation)
```

---

## Quick Reference: Key Terms for the Interview

| Term | One-line definition |
|---|---|
| Finality | A block/tx cannot be reversed |
| Slashing | Destroying validator stake as punishment for misbehavior |
| Sequencer | Entity that orders L2 transactions before posting to L1 |
| Paymaster | Contract that sponsors gas fees on behalf of users (AA) |
| Bundler | Submits ERC-4337 UserOperations to EntryPoint |
| Threshold signature | M-of-N parties jointly sign; output = normal signature |
| State root | Cryptographic commitment to the entire chain state at a block |
| Patricia Merkle Trie | Data structure used to store Ethereum state efficiently |
| HSM | Hardware Security Module — tamper-proof key storage |
| PBS | Proposer-Builder Separation — splits block building from proposal |
