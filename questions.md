# DeFi, MEV, Flashbots, and Uniswap V3 Interview Questions

## DeFi Questions (1--50)

1.  What is DeFi and how does it differ from traditional finance?
2.  What are the main components of a DeFi ecosystem?
3.  What is a smart contract and why is it critical for DeFi protocols?
4.  What is the difference between Layer 1 and Layer 2 blockchains?
5.  How do Automated Market Makers (AMMs) work?
6.  What is the constant product formula used in AMMs?
7.  What is impermanent loss and when does it occur?
8.  How do liquidity providers earn rewards in AMMs?
9.  What is slippage in decentralized exchanges?
10. What is a liquidity pool and how is it structured?
11. How does a token swap occur in a decentralized exchange?
12. What are the main risks for liquidity providers?
13. What is yield farming?
14. What is the difference between APR and APY?
15. What is staking and how does it differ from yield farming?
16. What are governance tokens and how are they used in DeFi protocols?
17. What is overcollateralization in DeFi lending?
18. How do lending protocols determine liquidation thresholds?
19. What happens during a liquidation event in a lending protocol?
20. What are flash loans and why are they unique to DeFi?
21. How can flash loans be used maliciously in attacks?
22. What are price oracles and why are they important in DeFi?
23. What risks exist when relying on external price oracles?
24. What is a TWAP (Time Weighted Average Price) oracle?
25. What is front-running and how does it occur on blockchains?
26. What is MEV (Maximal Extractable Value)?
27. How do sandwich attacks work?
28. What are stablecoins and why are they important for DeFi?
29. What are the differences between algorithmic, crypto-collateralized,
    and fiat-backed stablecoins?
30. How do DeFi protocols maintain stablecoin pegs?
31. What is composability in DeFi?
32. Why is composability considered a 'money lego' property?
33. What are DeFi aggregators and how do they work?
34. What is a vault in DeFi protocols?
35. What are the common vulnerabilities in DeFi smart contracts?
36. What is a reentrancy attack?
37. What is the checks-effects-interactions pattern?
38. Why are audits important for DeFi protocols?
39. What is protocol governance and how is it implemented?
40. What are timelocks in governance systems?
41. What are upgradeable smart contracts?
42. What are proxy patterns used for in smart contracts?
43. What are the main differences between centralized and decentralized
    exchanges?
44. What are DeFi bridges and why are they risky?
45. What is wrapped crypto (e.g., wrapped tokens)?
46. What are liquidity mining incentives?
47. How do DeFi protocols generate revenue?
48. What metrics are commonly used to evaluate a DeFi protocol (e.g.,
    TVL)?
49. What are the main systemic risks in the DeFi ecosystem?
50. How would you design a basic decentralized lending protocol?

## MEV / Flashbots / Uniswap V3 Questions (51--100)

51. What is MEV (Maximal Extractable Value) and how does it arise in
    blockchains?
52. What actors participate in the MEV ecosystem (searchers, builders,
    validators)?
53. How did Ethereum's move to Proof of Stake change the MEV landscape?
54. What is the difference between MEV and miner extractable value?
55. What are the most common types of MEV strategies?
56. What is a sandwich attack?
57. What is arbitrage MEV?
58. What is liquidation MEV?
59. How does front-running differ from back-running?
60. What is a bundle in MEV systems?
61. Why does public mempool transparency create MEV opportunities?
62. What are the risks MEV poses to normal users?
63. How can protocols try to mitigate MEV?
64. What is private order flow?
65. What is MEV smoothing?
66. What problem does Flashbots attempt to solve?
67. What is MEV-Geth?
68. What is the role of a searcher in the Flashbots architecture?
69. What is the role of a block builder?
70. What is Proposer Builder Separation (PBS)?
71. Why was PBS introduced in Ethereum?
72. What is a Flashbots bundle and how is it structured?
73. How do bundles ensure atomic execution?
74. What happens if one transaction in a bundle fails?
75. What is MEV-Boost?
76. How does MEV-Boost interact with validators?
77. What advantages do builders have over validators in block
    construction?
78. What is the difference between sending a transaction to the public
    mempool vs Flashbots relay?
79. What are Flashbots relays?
80. What security risks exist in relay-based block building?
81. What is the main innovation introduced in Uniswap V3?
82. What is concentrated liquidity?
83. Why does concentrated liquidity improve capital efficiency?
84. What is a price range position in Uniswap V3?
85. What happens when the price moves outside a liquidity provider's
    range?
86. What are ticks in Uniswap V3?
87. How do ticks determine price ranges?
88. Why are pools divided into discrete price ticks?
89. What are the fee tiers in Uniswap V3 pools and why do they exist?
90. What is an NFT liquidity position?
91. Why are LP positions represented as NFTs in Uniswap V3?
92. How does Uniswap V3 reduce impermanent loss compared to V2?
93. Why does Uniswap V3 require active liquidity management?
94. How do arbitrageurs keep pool prices aligned with external markets?
95. What role does MEV play in Uniswap arbitrage?
96. Why are DEXs major sources of MEV?
97. How do arbitrage bots exploit price differences between pools?
98. How does concentrated liquidity affect MEV opportunities?
99. How could a large swap create a sandwich opportunity?
100. How can private transaction relays help protect users from sandwich
     attacks?

## Advanced Questions (101--110)

101. Explain a sandwich attack step-by-step at the mempool and block
     level.
102. How do arbitrage bots operate between multiple decentralized
     exchanges?
103. Why does MEV exist in blockchains with public mempools?
104. Why are decentralized exchanges the largest source of MEV?
105. Explain concentrated liquidity and its implications for capital
     efficiency.
106. What happens to a liquidity position when price leaves its
     specified range?
107. Why are Uniswap V3 liquidity positions represented as NFTs?
108. What are ticks and why are they necessary in Uniswap V3 price math?
109. Why do arbitrageurs help maintain price correctness in AMMs?
110. Explain how a Flashbots bundle works and why atomic execution is
     important.
