# Future Scope and Limitations

While Catalog-SLM provides a working end-to-end framework, several enhancements can be made to adapt it to a large-scale production digital retail ecosystem.

## Current Limitations

1. **Taxonomy Span**: The controlled taxonomy is limited to 5 main categories and 27 subcategories. Expanding this to cover thousands of FMCG, pharmaceutical, and grocery products requires more training data.
2. **Controlled Vocabulary**: Attribute classification heads use predefined lists (e.g. 10 colors, 9 materials). Unseen attributes default to manual entry.
3. **Indic Language Range**: The system is trained on English, Hindi, and mixed code inputs. It does not yet support other Indian languages.

## Future Research & Expansion

1. **Multilingual Transformer Architectures**: Future iterations can integrate lightweight pretrained Indic-centric models like **IndicBERT** or **mBERT** as the shared text encoder. This would enable semantic understanding of up to 22 official Indian languages.
2. **Named Entity Recognition (NER) for Open Attributes**: Moving from multi-class attribute predictions to token-level Named Entity Recognition (NER) would allow extraction of open-ended values (such as arbitrarily named brands, size numbers, or specific quantities).
3. **Active Learning Loop**: Implement a feedback mechanism where seller-corrected catalogs in the SQLite history are periodically queued to automatically fine-tune the Keras model.
4. **Direct API Integration with Seller Nodes**: Implement actual ONDC transaction APIs (such as search, select, init, confirm, and catalog push protocols) to test raw catalog updates directly with ONDC sandbox gateway servers.
