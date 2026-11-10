# Data

**SupplyGraph** — real supply chain planning data from an FMCG manufacturer in Bangladesh
(41 products, daily, 1 Jan – 9 Aug 2023): sales orders, production, factory issues and
deliveries to distributors, plus product groups, 25 plants and 13 storage locations.

- Source: https://github.com/ciol-researchlab/SupplyGraph
- Paper: Wasi, Islam & Akib (2024), *SupplyGraph: A Benchmark Dataset for Supply Chain
  Planning using Graph Neural Networks*, arXiv:2401.15299.

To reproduce:

    git clone https://github.com/ciol-researchlab/SupplyGraph.git data/supplygraph

The raw files are not stored in this repository. The pipeline loads them into
**SAP-style tables** (MARA, MARC, VBAP, MSEG) in SQL Server. These are modelled on
SAP's table structures for demonstration; they are not a real SAP extract.