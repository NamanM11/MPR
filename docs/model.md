# Model Architecture

Catalog-SLM employs a lightweight Multi-Task Sequence Classification Neural Network built with TensorFlow and Keras. 

## Neural Network Block Diagram

```
                 [Input Text Description]
                            │
                            ▼
              [Tokenization (Custom Tokenizer)]
                            │
                            ▼
           [Integer Vector (Sequence Length = 20)]
                            │
                            ▼
              [Embedding Layer (Dim = 64)]
                            │
                            ▼
           [Bidirectional LSTM Layer (Units = 64)]
                     (Output Dim = 128)
                            │
                            ▼
                      [Dropout (0.2)]
                            │
                            ▼
           [Shared Dense Representation (Units = 64)]
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    [Category Head]    [Color Head]     [Material Head]
  (Softmax, 5 classes) (Softmax, 10)    (Softmax, 9)
         │                  │                  │
         ▼                  ▼                  ▼
       ...                 ...                ...
         (Total 10 parallel classification output heads)
```

## Layer Specifications

1. **Embedding Layer**:
   - Maps input token integers to dense continuous vectors of dimension 64.
   - Learns word relationships (e.g., placing multilingual synonyms like "लाल" and "red" close together in the vector space).

2. **Bidirectional LSTM**:
   - Consists of a forward and a backward LSTM layer with 64 units each.
   - Learns sequence dependencies in both directions (important for code-mixed Hindi/English word orders like "लाल रंग की cotton shirt" vs "cotton shirt in red color").

3. **Dropout Layer**:
   - Dropout rate of 20% to prevent overfitting on templates.

4. **Shared Dense Representation**:
   - A fully connected layer of 64 units with ReLU activation.
   - Compresses sequence features into a joint representation that captures overall semantics.

5. **Parallel Softmax Output Heads**:
   - 10 parallel Dense layers with Softmax activation.
   - Output category distribution probabilities for: `category`, `subcategory`, `product_type`, `color`, `material`, `gender`, `size`, `brand`, `quantity`, and `language`.
