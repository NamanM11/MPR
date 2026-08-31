# Training Procedure

The Catalog-SLM multi-task model is compiled and trained locally using TensorFlow's high-level Keras APIs.

## Optimization Strategy

### Multi-Output Compilation
The model uses `sparse_categorical_crossentropy` as the loss function for all 10 parallel classification heads. 

To prioritize core commerce categorization tasks, different loss weights were assigned:
- **Category, Subcategory, Product Type**: Weight = `2.0`
- **Language and Attributes (Color, Material, Gender, Size, Brand, Quantity)**: Weight = `1.0`

$$Loss_{total} = 2 \cdot L_{cat} + 2 \cdot L_{subcat} + 2 \cdot L_{type} + \sum_{attr} 1 \cdot L_{attr}$$

### Optimizer & Settings
- **Optimizer**: Adam (learning rate = $0.001$)
- **Batch Size**: 32
- **Epochs**: 15
- **Validation**: 10% validation split is fed directly into Keras' training loop to monitor generalization.

## Model Serialization
Upon successful training completion, the model is serialized into Keras' unified file format (`model.keras` or fallback `model.h5`) under `ml/models/catalog_slm/`. 
The custom tokenizer's vocabulary maps and target categories are exported to `tokenizer.json` for deterministic inference preprocessing.
Training and test evaluation stats are recorded in `metadata.json`.
