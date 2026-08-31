# Problem Statement

## Automated Product Cataloging for Small & Medium Enterprises (SMEs) in Digital Commerce

A critical barrier to onboarding small-scale sellers, local merchants, and artisans onto open digital commerce networks (such as ONDC in India) is the complexity of product cataloging. Traditional e-commerce platforms require structured, standardized, and high-quality catalogs containing detailed taxonomies, product types, and attribute fields (e.g., brand, color, material, gender, size, and quantity).

Local sellers frequently enter product information in:
1. **Unstructured Natural Language**: Informal descriptions rather than structured data fields.
2. **Vernacular & Multilingual Text**: Hindi, regional languages, or mixed-language input (e.g., "Hinglish").
3. **Inconsistent Terminology**: Using synonyms or colloquial terms (e.g., "लाल रंग", "red color", "सूती शर्ट", "cotton shirt").

### Core Challenge
There is a lack of lightweight, multilingual, and domain-specific Natural Language Processing (NLP) models that can operate on normal local servers to parse unstructured, code-mixed descriptions, classify them into standard digital-commerce taxonomies, and extract normalized product attributes.

### Project Objective
**Catalog-SLM** addresses this gap by implementing a Lightweight Small Language Model (SLM) based on a TensorFlow multi-task classification architecture. It translates unstructured, bilingual English/Hindi product descriptions into standardized, structured, and ONDC-oriented digital commerce catalog entries.
