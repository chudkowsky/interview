# Layer 3: Questions

---

**Q17.** What is overcollateralization in DeFi lending?

Overcollateralization means borrowers must deposit collateral worth more than the loan they receive. For example, to borrow $100 USDC on Aave, you might need to deposit $150 worth of ETH — a 150% collateral ratio. This buffer protects the protocol from losses if the collateral price falls before the loan is repaid. The excess collateral absorbs price volatility and gives the protocol time to liquidate undercollateralized positions before they go underwater. Overcollateralization is necessary in DeFi because there's no credit score, legal enforcement, or identity — the collateral itself is the only guarantee.

**Q18.** How do lending protocols determine liquidation thresholds?

Liquidation thresholds are set per-asset based on the asset's volatility, liquidity, and historical price behavior. A stable asset like USDC might have an 85% LTV (Loan-to-Value) threshold, meaning liquidation triggers when the loan value reaches 85% of collateral value. Volatile assets like altcoins get lower thresholds (e.g., 50–65%). Protocols like Aave use separate "loan-to-value" (how much you can borrow) and "liquidation threshold" (when you get liquidated) parameters, with a health factor — when the health factor drops below 1.0, the position becomes liquidatable. These parameters are set by governance and updated as market conditions change.

**Q19.** What happens during a liquidation event in a lending protocol?

When a borrower's health factor falls below 1.0 (their collateral value is too close to their debt), liquidators — bots or users — can repay part of the borrower's debt in exchange for a discounted portion of their collateral (the "liquidation bonus," typically 5–15%). For example, a liquidator repays $100 of USDC debt and receives $108 worth of ETH collateral — earning an instant 8% profit. This incentivizes third parties to maintain protocol solvency. The borrower loses their collateral at a discount and retains the borrowed assets. Liquidations are competitive — MEV bots race to execute them in the same block the position becomes eligible.

**Q20.** What are flash loans and why are they unique to DeFi?

Flash loans are uncollateralized loans that must be borrowed and repaid within a single blockchain transaction. If the repayment (plus fee) doesn't happen by the end of the transaction, the entire transaction reverts — meaning the loan never actually occurred from the blockchain's perspective. This is only possible in DeFi because smart contracts can enforce atomicity: either all steps execute or none do. Flash loans enable massive capital for arbitrage, liquidations, and collateral swaps without any upfront capital. They are unique to blockchains because traditional finance has no equivalent "all or nothing" atomic execution guarantee within a single settlement step.

**Q21.** How can flash loans be used maliciously in attacks?

Flash loans amplify attacks by providing unlimited capital to exploit price oracle vulnerabilities or protocol logic bugs. In a classic oracle manipulation attack, an attacker borrows a huge sum, manipulates a DEX spot price (which a protocol uses as its oracle), borrows against the inflated price, and repays the flash loan — all in one transaction. The bZx attacks in 2020 demonstrated this: attackers flash-loaned ETH, manipulated Uniswap's ETH/WBTC price, used that inflated price to borrow more from another protocol, and kept the profit. Flash loans don't create vulnerabilities — they just remove the capital barrier to exploiting existing ones.

**Q22.** What are price oracles and why are they important in DeFi?

Price oracles are services that provide external price data (e.g., ETH/USD) to smart contracts, which cannot access off-chain information on their own. They are critical for DeFi because lending protocols need accurate prices to determine if positions are undercollateralized, DEXs use them for limit orders, synthetic assets need peg data, and liquidations depend on real-time valuations. Without oracles, on-chain protocols are isolated from real-world markets. The most widely used oracle is Chainlink (decentralized network of data providers), but protocols also use on-chain TWAP oracles derived from their own pool prices.

**Q23.** What risks exist when relying on external price oracles?

The main risks are: (1) **Manipulation** — if a protocol uses a DEX spot price as its oracle, an attacker can manipulate that price with a large trade (especially in low-liquidity pools); (2) **Staleness** — oracles may not update fast enough during high volatility, leaving protocols using outdated prices; (3) **Centralization** — if a single data provider controls the oracle (as in early Compound), it becomes a single point of failure or attack; (4) **Flash loan amplification** — attackers can use flash loans to temporarily move oracle prices; (5) **Network congestion** — during congestion, oracle updates may be delayed, creating stale-price windows. TWAP oracles mitigate manipulation by averaging prices over time.

**Q24.** What is a TWAP (Time Weighted Average Price) oracle?

A TWAP oracle calculates the average price of an asset over a specified time window by continuously accumulating the price multiplied by the time it was observed. Uniswap V2/V3 accumulates a `price * time` value with every block, and any contract can query the average price over any past window by taking two snapshots and dividing by the elapsed time. Because the TWAP smooths out instantaneous price spikes, it is much harder to manipulate than a spot price — an attacker would need to sustain a manipulated price for the entire averaging window, which is expensive and economically impractical. The trade-off is latency: TWAPs lag real-time prices.

**Q28.** What are stablecoins and why are they important for DeFi?

Stablecoins are cryptocurrencies designed to maintain a stable value, typically pegged to the US dollar (1 USDC = $1). They are essential to DeFi because they provide a price-stable medium of exchange and store of value within an otherwise volatile ecosystem — enabling lending, borrowing, trading, and payroll without the need to constantly convert back to fiat. Without stablecoins, DeFi participants would be forced to accept full crypto volatility on every transaction. Major stablecoins: USDC and USDT (fiat-backed), DAI (crypto-collateralized), and LUSD/FRAX (algorithmic/hybrid).

**Q29.** What are the differences between algorithmic, crypto-collateralized, and fiat-backed stablecoins?

**Fiat-backed** (e.g., USDC, USDT): Each token is backed 1:1 by USD held in a bank. Highly stable but centralized — issuer can freeze wallets, banks can fail, and requires trust in the custodian. **Crypto-collateralized** (e.g., DAI): Backed by on-chain crypto collateral at overcollateralization ratios (e.g., 150%+ ETH). Decentralized and transparent but capital-inefficient and vulnerable to collateral crashes causing mass liquidations. **Algorithmic** (e.g., UST/LUNA): Maintains the peg through supply/demand mechanisms and seigniorage — no direct collateral. Capital-efficient but extremely fragile; UST's 2022 collapse ($40B wiped) demonstrated that algorithmic stablecoins can enter death spirals under bank-run conditions.

**Q30.** How do DeFi protocols maintain stablecoin pegs?

Peg mechanisms vary by type. **Fiat-backed**: redeemability 1:1 for USD maintains the peg through arbitrage — if price drops below $1, arbitrageurs buy and redeem for real USD. **Crypto-collateralized (MakerDAO/DAI)**: stability fee (interest rate) and DSR (savings rate) incentivize borrowing/saving to adjust supply; emergency shutdown and liquidations protect solvency. **Algorithmic (Frax)**: fractional reserve with algorithmic market operations to expand/contract supply. All systems rely on arbitrageurs correcting deviations — when the stablecoin trades below peg, arbitrageurs buy and redeem (or burn); above peg, they mint and sell. Protocols also use stability pools and circuit breakers for extreme conditions.
