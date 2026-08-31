# Objectives

The main objective of this project is to develop and evaluate a lightweight bilingual natural language processing system that automates the generation of standardized product catalogs from natural text.

## Specific Technical Objectives

1. **Controlled Dataset Creation**: Develop a structured dataset containing English, Hindi, and mixed-language (Hinglish) product descriptions associated with standardized attributes and category labels to train and evaluate the SLM.
2. **Lightweight SLM Architecture**: Design a multi-task learning neural network using TensorFlow and Keras that utilizes a shared Bidirectional LSTM sequence encoder to simultaneously predict category, subcategory, product type, language, and controlled attributes.
3. **Attribute Normalization Service**: Implement a rule-based normalization layer to map predicted multilingual synonyms (e.g., "लाल" or "नीला") to standard English/canonical values (e.g., "Red" or "Blue").
4. **Bilingual Support (English + Hindi)**: Train the system to understand English, Hindi, and mixed code-switched product inputs, ensuring high classification performance on colloquial terms.
5. **ONDC Schema Compliance**: Map leaf subcategories to a standard, open-network-oriented hierarchical taxonomy.
6. **Dashboard & Human-in-the-Loop Workflow**: Provide an intuitive web dashboard allowing sellers to input descriptions, trace extraction steps, manually review/edit values, download ONDC-compliant JSON catalog schemas, and review model performance analytics.
