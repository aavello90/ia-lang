import numpy as np
import joblib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import Dict

_MODEL_PATH = Path(__file__).parent / "router_model.txt"

class LLMRouter:
    _instance = None

    def __new__(cls, model_path="router_model.txt"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_path="router_model.txt"):
        if getattr(self, "_initialized", False):
            return
        self.encoder = SentenceTransformer('BAAI/bge-m3')
        self.encoder.max_seq_length = 512
        self.model = joblib.load(model_path) if isinstance(model_path, (str, Path)) else model_path
        
        self.label_map = {0: "casual", 1: "medio", 2: "potente"}
        
        # Instrucción consistente (se usa tanto en train como en predict)
        self.instruction = "Clasifica esta consulta de usuario para enviarla al modelo de IA más adecuado (casual, medio o potente):"
        self._initialized = True

    def _embed(self, text: str) -> np.ndarray:
        prompt = f"{self.instruction}\n\nConsulta: {text}"
        embedding = self.encoder.encode(
            prompt,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding

    def predict(self, text: str, min_confidence: float = 0.55) -> Dict:
        emb = self._embed(text)
        proba = self.model.predict([emb])[0]           # LightGBM multiclass devuelve probabilidades
        predicted_class = int(np.argmax(proba))
        confidence = float(proba[predicted_class])

        # Fallback de seguridad: si no está seguro, mejor mandar a potente
        if confidence < min_confidence:
            predicted_class = 2
            confidence = float(proba[2])

        return {
            "route": self.label_map[predicted_class],
            "confidence": round(confidence, 4),
            "probabilities": {
                "casual": round(float(proba[0]), 4),
                "medio": round(float(proba[1]), 4),
                "potente": round(float(proba[2]), 4)
            }
        }

router = LLMRouter(_MODEL_PATH)