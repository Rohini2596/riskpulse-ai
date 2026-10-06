import re
from dataclasses import asdict, dataclass
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_finbert_pipeline():
    from transformers import pipeline

    return pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        device=-1,
    )
    
    
@dataclass(frozen=True)
class RiskSignal:
    source: str
    text: str
    entity: str
    sentiment: float
    event: str
    confidence: float
    impact: float

    def to_dict(self):
        return asdict(self)


class RiskNlpEngine:
    """
    Hybrid NLP engine.

    FinBERT scores sentiment. Transparent keyword rules identify entities
    and event categories, and estimate confidence and impact.
    """

    EVENTS = {
        "Geopolitical": (
            "war", "military", "invasion", "sanctions", "tariff",
            "geopolitical", "conflict", "taiwan", "china"
        ),
        "Macroeconomic": (
            "inflation", "interest rate", "rate hike", "recession",
            "gdp", "unemployment", "federal reserve", "fed"
        ),
        "Credit Event": (
            "default", "bankruptcy", "downgrade", "downgrades",
            "downgraded", "credit rating", "debt restructuring",
            "missed payment", "miss payments", "credit loss",
            "credit losses", "borrower"
        ),
        "Regulatory": (
            "regulation", "regulator", "antitrust", "fine", "lawsuit",
            "investigation", "compliance"
        ),
        "M&A": (
            "acquisition", "merger", "takeover", "buyout"
        ),
        "Earnings": (
            "earnings", "revenue", "profit", "quarterly results",
            "guidance", "loss"
        ),
        "Market Shock": (
            "market crash", "selloff", "market shock", "plunge",
            "surge", "volatility"
        ),
        "Management Change": (
            "ceo resigns", "ceo steps down", "appoints ceo",
            "executive departure", "management change"
        ),
        "Product Launch": (
            "launches", "product launch", "unveils", "new product"
        ),
    }

    POSITIVE = (
        "beats expectations", "record profit", "profit rises",
        "strong growth", "approval", "wins contract", "raises guidance",
        "surges", "successful"
    )
    NEGATIVE = (
        "misses expectations", "profit falls", "loss widens",
        "default", "bankruptcy", "downgrade", "sanctions", "war",
        "recall", "investigation", "plunges", "cuts guidance"
    )

    ENTITY_ALIASES = {
        "TSMC": ("tsmc", "taiwan semiconductor"),
        "Apple": ("apple", "aapl"),
        "JPMorgan": ("jpmorgan", "jp morgan", "jpm"),
        "Federal Reserve": ("federal reserve", "fed"),
        "Taiwan": ("taiwan",),
        "China": ("china",),
        "Microsoft": ("microsoft", "msft"),
        "Nvidia": ("nvidia", "nvda"),
        "Tesla": ("tesla", "tsla"),
    }

    def analyze(self, text: str, source: str = "unknown") -> RiskSignal:
        if not text or not text.strip():
            raise ValueError("text cannot be empty")

        normalized = re.sub(r"\s+", " ", text.lower()).strip()

        entity = self._find_entity(normalized)
        event, event_hits = self._find_event(normalized)
        sentiment = self._finbert_sentiment(text.strip())
        confidence = self._confidence(event_hits, entity, normalized)
        impact = self._impact(event, normalized)
        return RiskSignal(
            source=source,
            text=text.strip(),
            entity=entity,
            sentiment=sentiment,
            event=event,
            confidence=confidence,
            impact=impact,
        )

    def _find_entity(self, text: str) -> str:
        for entity, aliases in self.ENTITY_ALIASES.items():
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", text):
                    return entity

        # Recognize cashtags such as $AAN or $UBER as ticker entities.
        ticker_match = re.search(r"\$([A-Za-z]{1,5})\b", text)
        if ticker_match:
            return ticker_match.group(1).upper()

        return "Unknown"

    def _find_event(self, text: str):
        matches = {}

        for event, keywords in self.EVENTS.items():
            hits = []
            for keyword in keywords:
                # Match whole words or full phrases, not substrings inside
                # unrelated words such as "war" inside "warns".
                pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
                if re.search(pattern, text):
                    hits.append(keyword)

            if hits:
                matches[event] = hits

        if not matches:
            return "Other", []

        # The most keyword matches wins. Declared event order breaks ties.
        event = max(matches, key=lambda name: len(matches[name]))
        return event, matches[event]

    def _sentiment(self, text: str) -> float:
        positive_hits = sum(term in text for term in self.POSITIVE)
        negative_hits = sum(term in text for term in self.NEGATIVE)
        if positive_hits == negative_hits:
            return 0.0
        score = (positive_hits - negative_hits) / max(
            1, positive_hits + negative_hits
        )
        return round(max(-1.0, min(1.0, score)), 2)
    
    def _finbert_sentiment(self, text: str) -> float:
        classifier = _get_finbert_pipeline()
        predictions = classifier(text, top_k=None, truncation=True)

        if predictions and isinstance(predictions[0], list):
            predictions = predictions[0]

        probabilities = {}
        id_to_label = classifier.model.config.id2label

        for prediction in predictions:
            label = prediction["label"].lower()

            if label.startswith("label_"):
                label_id = int(label.split("_")[1])
                label = id_to_label[label_id].lower()

            probabilities[label] = float(prediction["score"])

        score = probabilities.get("positive", 0.0) - probabilities.get("negative", 0.0)
        return round(max(-1.0, min(1.0, score)), 3)
    
    def _confidence(self, event_hits, entity: str, text: str) -> float:
        score = 0.35
        if event_hits:
            score += min(0.30, 0.15 * len(event_hits))
        if entity != "Unknown":
            score += 0.20
        if len(text.split()) >= 8:
            score += 0.10
        return round(min(0.95, score), 2)

    def _impact(self, event: str, text: str) -> float:
        base_scores = {
            "Geopolitical": 7.0,
            "Macroeconomic": 6.5,
            "Credit Event": 8.0,
            "Regulatory": 6.0,
            "M&A": 5.5,
            "Earnings": 5.5,
            "Market Shock": 8.0,
            "Management Change": 4.5,
            "Product Launch": 3.5,
            "Other": 3.0,
        }
        score = base_scores[event]
        high_severity = (
            "global", "major", "record", "emergency", "default",
            "bankruptcy", "war", "crisis", "collapse"
        )
        if any(term in text for term in high_severity):
            score += 1.0
        if len(text.split()) > 35:
            score += 0.5
        return round(min(10.0, score), 1)