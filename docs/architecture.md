# System Architecture

The Catalog-SLM system consists of a Vite-based React frontend dashboard, a FastAPI backend, an SQLite database for catalog history, and a TensorFlow-based multi-task NLP pipeline.

## System Block Diagram

```mermaid
graph TD
    Seller([Seller / User]) -->|Natural Language input| ReactApp[React Web Dashboard]
    ReactApp -->|HTTP POST Request| FastAPI[FastAPI Backend Server]
    
    subgraph FastAPI Backend
        FastAPI -->|1. Tokenize Text| TokenizerService[Custom Tokenizer]
        TokenizerService -->|2. Integer Sequence| ModelInference[Catalog-SLM TensorFlow Model]
        
        subgraph NLP Multi-Task Model
            ModelInference -->|Predict Category & Subcategory| CatHeads[Category Prediction Heads]
            ModelInference -->|Predict Attributes| AttrHeads[Attribute Prediction Heads]
        end
        
        CatHeads & AttrHeads -->|3. Raw Predictions| Processor[Catalog Processor Service]
        Processor -->|4. Resolve Synonyms| Normalization[Normalization Layer]
        Processor -->|5. Resolve Hierarchical Path| Taxonomy[Taxonomy Mapping Layer]
        
        Normalization & Taxonomy -->|6. Compile Catalog| OutputGen[Structured Catalog Generator]
    end
    
    OutputGen -->|7. Persist Record| SQLite[(SQLite Database)]
    OutputGen -->|8. Standardized JSON| ReactApp
    Processor -->|Retrieve known product & validate variants| ProductResolver[Product Knowledge Resolver]
    ProductResolver -->|Trusted metadata / match result| OutputGen
    ProductResolver --> ProductStore[(SQLite Product Knowledge)]
    
    ReactApp -->|9. Manual Edit & Approval| ApproveEndpoint[FastAPI Approve Endpoint]
    ApproveEndpoint -->|10. Update Status| SQLite
    
    SQLite -->|Catalog history and resolution metrics| Analytics[Analytics Service]
    Analytics -->|HTTP GET Response| ReactApp
```

## Architectural Components

1. **Presentation Layer (React + Vite + Tailwind CSS)**:
   - Dashboard: High-level analytics on processed items and success rate.
   - Catalog Generator: Primary workspace for inputting product descriptions, seeing step-by-step processing state, and correcting/approving the output.
   - History: Table interface for managing previous catalogs (Draft, Approved, Needs Review).
   - Taxonomy Browser: A browseable tree showing the active ONDC taxonomy.
   - Evaluation: Displays the ML metrics generated during training.

2. **Inference & Service Layer (FastAPI)**:
   - Orchestrates requests, manages database state, and serves taxonomy configurations.
   - Houses the `CatalogProcessor` which encapsulates tokenizer, model execution, normalization synonyms, taxonomy mapping, and existing-product resolution.

3. **Data Layer (SQLite)**:
   - Lightweight relational database to persist catalogs, resolution outcomes, processing times, confidence logs, and seller decisions.
   - A product knowledge table stores trusted product metadata and valid variants. The catalog processor retrieves this data before finalizing catalog details; approved new products can be added to the same table.
