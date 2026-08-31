# Relevance to ONDC & Retail Ecosystems

The Open Network for Digital Commerce (ONDC) is an initiative by the Government of India aimed at promoting open networks for all aspects of local digital commerce. A key design principle of ONDC is the decoupling of buyer and seller platforms through open protocol specifications.

## The Cataloging Bottleneck

To list products on the open network, sellers must provide structured catalog payloads containing standardized attributes, identifiers, and taxonomy categories. This ensures that buyer applications can search, filter, and compare products across different sellers.

For small, local, and vernacular-first merchants, the process of manually filling out structured, multi-field product spreadsheets is a high-friction task. It requires digital literacy and knowledge of technical e-commerce terms.

## How Catalog-SLM Solves this Friction

1. **Structured Schema Mapping**: Catalog-SLM parses informal seller inputs (e.g. "नीले रंग की cotton shirt") and maps them to canonical attributes:
   - `color` = `Blue`
   - `material` = `Cotton`
   - `product_type` = `Shirt`
   - `category` = `Clothing`

2. **Hierarchical Taxonomy Matching**: It maps leaf nodes to the ONDC standard taxonomy (e.g., `["Clothing", "Men's Clothing", "Shirts"]`), ensuring search indexing alignment.

3. **Open-Network Output Format**: By generating standardized ONDC-oriented JSON outputs, it enables local sellers to immediately synchronize their inventories with seller node gateway databases without hiring specialized data entry staff. This democratizes open network onboarding.
