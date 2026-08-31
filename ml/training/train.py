import json
import os
import time
import numpy as np
import tensorflow as tf

def load_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    input_ids = np.array([x["input_ids"] for x in data], dtype=np.int32)
    
    # Restructure targets for Keras multi-output
    targets = {}
    if len(data) > 0:
        keys = data[0]["targets"].keys()
        for k in keys:
            targets[k] = np.array([x["targets"][k] for x in data], dtype=np.int32)
            
    return input_ids, targets, data

def calculate_metrics(y_true, y_pred, num_classes):
    # Calculate precision, recall, F1 (macro average)
    precisions = []
    recalls = []
    f1s = []
    
    for c in range(num_classes):
        tp = np.sum((y_true == c) & (y_pred == c))
        fp = np.sum((y_true != c) & (y_pred == c))
        fn = np.sum((y_true == c) & (y_pred != c))
        
        precision = tp / (tp + fp + 1e-7)
        recall = tp / (tp + fn + 1e-7)
        f1 = 2 * precision * recall / (precision + recall + 1e-7)
        
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        
    macro_precision = float(np.mean(precisions))
    macro_recall = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))
    accuracy = float(np.sum(y_true == y_pred) / len(y_true))
    
    return accuracy, macro_precision, macro_recall, macro_f1

def generate_confusion_matrix(y_true, y_pred, num_classes):
    matrix = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        matrix[t, p] += 1
    return matrix.tolist()

def main():
    print("TensorFlow Version:", tf.__version__)
    
    # Load tokenizer details
    tokenizer_path = "ml/models/catalog_slm/tokenizer.json"
    if not os.path.exists(tokenizer_path):
        print(f"Error: Tokenizer metadata not found at {tokenizer_path}. Run preprocess_dataset.py first.")
        return
        
    with open(tokenizer_path, "r", encoding="utf-8") as f:
        tokenizer_data = json.load(f)
        
    vocab = tokenizer_data["vocab"]
    labels = tokenizer_data["labels"]
    max_len = tokenizer_data["max_len"]
    
    vocab_size = len(vocab)
    
    # Load splits
    train_ids, train_targets, train_raw = load_data("ml/data/processed/train.json")
    val_ids, val_targets, val_raw = load_data("ml/data/processed/val.json")
    test_ids, test_targets, test_raw = load_data("ml/data/processed/test.json")
    
    print(f"Loaded train: {len(train_ids)}, val: {len(val_ids)}, test: {len(test_ids)}")
    
    # Define multi-task Keras model
    embedding_dim = 64
    lstm_units = 64
    
    inputs = tf.keras.Input(shape=(max_len,), dtype="int32", name="input_ids")
    embedded = tf.keras.layers.Embedding(vocab_size, embedding_dim, name="embedding")(inputs)
    bilstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(lstm_units, return_sequences=False), name="bilstm")(embedded)
    dropout = tf.keras.layers.Dropout(0.2, name="dropout")(bilstm)
    shared_dense = tf.keras.layers.Dense(64, activation='relu', name="shared_dense")(dropout)
    
    # Generate output heads based on label definitions
    outputs = {}
    loss_weights = {}
    losses = {}
    
    for head_name, label_list in labels.items():
        num_classes = len(label_list)
        # Separate output head
        outputs[head_name] = tf.keras.layers.Dense(num_classes, activation='softmax', name=head_name)(shared_dense)
        losses[head_name] = 'sparse_categorical_crossentropy'
        # Categories and product types have higher weight for correct classification
        if head_name in ["category", "subcategory", "product_type"]:
            loss_weights[head_name] = 2.0
        else:
            loss_weights[head_name] = 1.0
            
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="catalog_slm")
    
    # Compile the multi‑output model with a per‑head accuracy metric
    metrics = {head: ['accuracy'] for head in outputs.keys()}
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=losses,
        loss_weights=loss_weights,
        metrics=metrics
    )
    
    model.summary()
    
    # Train
    epochs = 15
    batch_size = 32
    
    print("Training model...")
    history = model.fit(
        train_ids,
        train_targets,
        validation_data=(val_ids, val_targets),
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )
    
    # Save the model
    os.makedirs("ml/models/catalog_slm", exist_ok=True)
    model_path = "ml/models/catalog_slm/model.keras"
    try:
        model.save(model_path)
        print(f"Saved model as native Keras format: {model_path}")
    except Exception as e:
        print(f"Could not save in native format: {e}. Trying legacy HDF5 format.")
        model_path = "ml/models/catalog_slm/model.h5"
        model.save(model_path)
        print(f"Saved model as legacy H5 format: {model_path}")
        
    # Evaluate model performance
    print("Evaluating model...")
    test_preds = model.predict(test_ids)
    
    evaluation_results = {}
    overall_correct = 0
    total_predictions = 0
    
    # Compute metrics for each prediction head
    for head_name, label_list in labels.items():
        pred_probs = test_preds[head_name]
        pred_labels = np.argmax(pred_probs, axis=-1)
        true_labels = test_targets[head_name]
        
        acc, prec, rec, f1 = calculate_metrics(true_labels, pred_labels, len(label_list))
        
        evaluation_results[head_name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4)
        }
        
        # Category confusion matrix
        if head_name == "category":
            cm = generate_confusion_matrix(true_labels, pred_labels, len(label_list))
            evaluation_results["category_confusion_matrix"] = {
                "classes": label_list,
                "matrix": cm
            }
            
        overall_correct += np.sum(true_labels == pred_labels)
        total_predictions += len(true_labels)
        
    overall_accuracy = float(overall_correct / total_predictions)
    print(f"Overall Multi-Task Accuracy: {overall_accuracy:.4f}")
    
    # Measure inference time (single sample latency)
    single_sample = test_ids[:1]
    latencies = []
    for _ in range(50):
        t0 = time.time()
        _ = model.predict(single_sample, verbose=0)
        latencies.append((time.time() - t0) * 1000)
    avg_latency = float(np.mean(latencies[10:])) # exclude warm-up runs
    
    # Parameters and sizes
    param_count = model.count_params()
    file_size_mb = float(os.path.getsize(model_path) / (1024 * 1024))
    
    # Build evaluation metadata
    history_dict = {}
    for k, v in history.history.items():
        history_dict[k] = [float(val) for val in v]
        
    metadata = {
        "model_name": "Catalog-SLM",
        "version": "1.0",
        "languages": ["English", "Hindi", "Mixed"],
        "framework": "TensorFlow/Keras",
        "training_examples": len(train_ids),
        "validation_examples": len(val_ids),
        "test_examples": len(test_ids),
        "model_parameters": param_count,
        "model_size_mb": round(file_size_mb, 2),
        "avg_inference_time_ms": round(avg_latency, 2),
        "overall_accuracy": round(overall_accuracy, 4),
        "metrics": evaluation_results,
        "history": history_dict,
        "model_file": os.path.basename(model_path)
    }
    
    metadata_path = "ml/models/catalog_slm/metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Saved evaluation metrics metadata to {metadata_path}")
    print("ML Pipeline complete!")

if __name__ == "__main__":
    main()
