# Model Evaluation

The evaluation of Catalog-SLM is performed on a dedicated 10% test set (213 samples) that was completely isolated during model training to ensure unbiased metrics.

## Evaluated Metrics

For each classification output head, the system computes:
1. **Accuracy**: The ratio of correctly predicted labels to total samples.
2. **Precision (Macro Average)**: Evaluates false positives across all classes.
3. **Recall (Macro Average)**: Evaluates false negatives across all classes.
4. **F1-Score (Macro Average)**: Harmonic mean of precision and recall.

$$\text{Precision}_c = \frac{TP_c}{TP_c + FP_c} \quad \text{Recall}_c = \frac{TP_c}{TP_c + FN_c}$$

$$\text{Macro F1} = \frac{1}{|C|} \sum_{c \in C} 2 \cdot \frac{\text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

## Confusion Matrix

A category confusion matrix is generated dynamically to track cross-class errors (e.g., misclassifying "Footwear" as "Accessories"). 

## Model Efficiency Indicators

As a domain-specific Micro Language Model, efficiency stats are measured and outputted:
- **Parameter Count**: Total trainable weights (indicates model scale).
- **Model Size (MB)**: Size of the model on disk.
- **Inference Time (ms)**: Average time taken to tokenize, predict, and output standardized attributes for a single input text.
