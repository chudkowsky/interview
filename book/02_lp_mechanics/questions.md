# Layer 2: Questions

---

**Q7.** What is impermanent loss and when does it occur?

Impermanent loss (IL) is the difference in value between holding tokens in an AMM liquidity pool versus simply holding them in your wallet. It occurs whenever the price ratio of the two pooled tokens changes from when liquidity was deposited. If ETH doubles in price, arbitrageurs rebalance the pool by buying ETH until the pool price matches the market — your pool share ends up with less ETH and more of the other token than you'd have held outright. The loss is "impermanent" because it reverses if prices return to the original ratio, but becomes permanent upon withdrawal. IL increases with price volatility and is worst for uncorrelated token pairs.

**Q8.** How do liquidity providers earn rewards in AMMs?

LPs earn a fee on every trade routed through their pool, typically 0.05%–1% of the swap amount depending on the pool. These fees accumulate in the pool reserves — meaning the pool holds slightly more of each token after each trade. Since LPs hold pro-rata shares of the reserves (represented by LP tokens), they claim their accrued fees when they withdraw liquidity. Additionally, many protocols distribute governance or incentive tokens to LPs on top of trading fees (liquidity mining). The net profit for an LP is: trading fees earned minus impermanent loss, plus any additional token rewards.

**Q12.** What are the main risks for liquidity providers?

The primary risks are: (1) **Impermanent loss** — the pool rebalances when prices diverge, leaving LPs with less value than if they'd simply held; (2) **Smart contract risk** — bugs or exploits can drain the pool entirely; (3) **Token depreciation** — if one or both pooled assets crash in price, the LP's dollar value drops; (4) **Oracle manipulation** — on-chain price oracles can be manipulated if the pool is small; (5) **Regulatory risk** — governance changes or protocol upgrades may alter fee structures or rug-pull scenarios. For concentrated liquidity pools (Uniswap V3), there's also the risk of going "out of range" and earning zero fees while fully exposed to one asset.

**Q13.** What is yield farming?

Yield farming is the practice of deploying crypto assets across multiple DeFi protocols to maximize returns, typically by chasing the highest combination of trading fees, lending interest, and liquidity mining rewards. A yield farmer might: deposit USDC into a lending protocol to earn interest, borrow ETH against it, supply that ETH to an AMM pool to earn fees and token rewards, and stake the LP tokens in a farm for additional emissions. The strategies can be complex and involve constant rebalancing. High APYs are often temporary, driven by token inflation, and carry compounding smart contract and liquidation risks.

**Q14.** What is the difference between APR and APY?

APR (Annual Percentage Rate) is the simple annualized return without compounding — if you earn 1% per month, the APR is 12%. APY (Annual Percentage Yield) accounts for compounding — reinvesting earnings back into the position throughout the year. At 1% monthly compounding, the APY is approximately 12.68%. In DeFi, protocols typically advertise APY (with auto-compounding) or APR (without). The higher the compounding frequency, the greater the divergence between APR and APY. When comparing yields across protocols, you must use the same metric to avoid misleading comparisons.

**Q15.** What is staking and how does it differ from yield farming?

Staking is locking tokens in a protocol to earn rewards, most commonly to secure a Proof-of-Stake blockchain (e.g., staking ETH with validators to earn ~4% annually in ETH) or to participate in protocol governance and receive fee distributions. It is relatively passive and low-risk. Yield farming is actively deploying capital across multiple DeFi protocols to maximize returns, often involving complex strategies, frequent rebalancing, and exposure to smart contract risk across multiple protocols simultaneously. Staking usually has a single type of risk (slashing for validators, or token price risk), while yield farming compounds multiple risks for potentially higher returns.

**Q46.** What are liquidity mining incentives?

Liquidity mining is a mechanism where a DeFi protocol distributes its native governance or reward tokens to users who provide liquidity to its pools. For example, a new DEX might offer 1,000 TOKEN/day split among all LPs proportional to their share of the pool. This bootstraps liquidity quickly without requiring organic trading volume. The incentives are typically highest at launch and decay over time (emission schedules). The risk is "mercenary liquidity" — LPs who farm and dump the reward token, causing price collapse. Successful protocols use vesting periods or vote-escrow (veToken) models to align LP incentives with long-term protocol health.
