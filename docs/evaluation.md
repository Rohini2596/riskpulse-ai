# Sentiment Evaluation

## Models compared

- **Keyword baseline:** transparent positive/negative phrase matching.
- **ProsusAI FinBERT:** pretrained financial sentiment classifier.

## Financial PhraseBank

Evaluated on 2,264 `Sentences_AllAgree` examples:

| Model | Accuracy |
|---|---:|
| Keyword baseline | 60.0% |
| ProsusAI FinBERT | 97.2% |

**Important limitation:** ProsusAI FinBERT was fine-tuned using Financial PhraseBank. This score uses the same dataset family and is not an independent estimate of performance on new text. Do not present 97.2% as generalization accuracy.

## Twitter Financial News validation set

Evaluated on 2,388 usable posts from the downloaded validation CSV:

| Model | Accuracy |
|---|---:|
| Always-neutral reference | 65.6% |
| Keyword baseline | 64.3% |
| ProsusAI FinBERT | 72.5% |

The always-neutral reference is the proportion of neutral labels in this CSV. FinBERT performed better than that reference and the keyword baseline on this dataset. The result is a cross-source validation, not a guarantee of performance on live social media.

The dataset card lists 2,486 validation rows, while the downloaded CSV yielded 2,388 usable rows. We report the actual evaluated count and should investigate this discrepancy before presenting the benchmark as fully reproducible.

## Interpretation

- FinBERT improves sentiment classification over the current keyword baseline on the tested Twitter validation CSV.
- The dataset is class-imbalanced, with neutral as the largest class. Accuracy alone does not describe performance for each sentiment class.
- FinBERT sentiment is used by the NLP pipeline. Event, entity, impact, and heuristic confidence still use rule-based logic.
- Scenario losses are illustrative outputs from synthetic portfolio assumptions; they are not forecasts.

## Sources

- ProsusAI FinBERT: https://huggingface.co/ProsusAI/finbert
- ProsusAI training data notes: https://github.com/ProsusAI/finBERT#datasets
- Twitter Financial News dataset: https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment
- Financial PhraseBank license and use notes: see the downloaded dataset's `README.txt` and `License.txt`.

Do not include the Financial PhraseBank files in a public repository until its usage terms have been confirmed.