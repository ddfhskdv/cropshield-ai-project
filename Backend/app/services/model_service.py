import os
from typing import Any, Dict, List

from PIL import Image

from app.core.config import settings


class DiseaseModelService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_status = 'unavailable'
        self.model_message = 'PlantVillage ViT model is not loaded in this environment.'
        self.supported_crops = settings.SUPPORTED_CROPS

    def _normalise_label(self, crop_name: str, label: str) -> str:
        normalized = str(label).strip()
        if not normalized or normalized == 'Unknown':
            return f'{crop_name} health alert'
        if '___' in normalized:
            segments = normalized.split('___')
            if len(segments) > 1:
                clean = segments[1].replace('_', ' ')
                return clean.title()
        return normalized.replace('_', ' ').title()

    def _load_if_available(self):
        if self.model is not None and self.processor is not None:
            return True

        candidate_models = [settings.MODEL_ID] + list(getattr(settings, 'FALLBACK_MODEL_IDS', []))
        candidate_models = [m for m in candidate_models if m]

        errors: List[str] = []
        for model_id in candidate_models:
            try:
                import torch
                from transformers import AutoImageProcessor, AutoModelForImageClassification

                self.model = AutoModelForImageClassification.from_pretrained(model_id, local_files_only=False)
                self.processor = AutoImageProcessor.from_pretrained(model_id, local_files_only=False)
                self.model.eval()
                self.model_status = 'loaded'
                self.model_message = f'Model loaded successfully using {model_id}.'
                return True
            except Exception as exc:  # pragma: no cover - environment dependent
                errors.append(f'{model_id}: {exc.__class__.__name__}: {exc}')

        self.model_status = 'unavailable'
        self.model_message = 'Model unavailable: ' + '; '.join(errors[:2]) if errors else 'Model unavailable.'
        return False

    def validate_image(self, file_contents: bytes, filename: str) -> Dict[str, Any]:
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise ValueError('Only PNG and JPG images are allowed.')
        if len(file_contents) > 5 * 1024 * 1024:
            raise ValueError('Image size must be below 5MB.')

        try:
            image = Image.open(__import__('io').BytesIO(file_contents))
            image.verify()
        except Exception as exc:  # pragma: no cover
            raise ValueError('The uploaded file is not a valid image.') from exc

        return {'is_valid': True, 'mime': 'image', 'width': 0, 'height': 0}

    def predict(self, image_bytes: bytes, crop_name: str):
        if crop_name not in self.supported_crops:
            crop_name = crop_name.strip() or 'Crop'
            if crop_name.lower() not in [item.lower() for item in self.supported_crops]:
                self.supported_crops = list(settings.SUPPORTED_CROPS)

        if not self._load_if_available():
            return {
                'prediction_status': 'model_unavailable',
                'model_name': settings.MODEL_ID,
                'message': self.model_message,
                'crop': crop_name,
                'label': 'Unavailable',
                'confidence': 0.0,
                'symptoms': ['Model is not available in this environment, so no genuine AI prediction was produced.'],
                'causes': ['Model loading failed or dependencies are missing.'],
                'recommendations': ['Check the configuration and retry with a supported environment.'],
                'supported_crops': self.supported_crops,
            }

        try:
            import torch
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            inputs = self.processor(images=image, return_tensors='pt')
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
            pred_idx = torch.argmax(probs, dim=-1).item()
            conf = float(probs[0][pred_idx].item())
            labels = self.model.config.id2label
            label = labels.get(pred_idx, 'Unknown')
            label = self._normalise_label(crop_name, label)
            return {
                'prediction_status': 'predicted',
                'model_name': settings.MODEL_ID,
                'message': 'AI prediction generated successfully.',
                'crop': crop_name,
                'label': label,
                'confidence': round(conf * 100, 2),
                'symptoms': ['Follow recommended field inspection.'],
                'causes': ['Environmental conditions and crop stress.'],
                'recommendations': ['Review the result, inspect the affected crop, and use recommended agronomy practices.'],
                'supported_crops': self.supported_crops,
            }
        except Exception as exc:  # pragma: no cover - network/dependency depending
            return {
                'prediction_status': 'model_unavailable',
                'model_name': settings.MODEL_ID,
                'message': f'Prediction failed: {exc.__class__.__name__}: {exc}',
                'crop': crop_name,
                'label': 'Unavailable',
                'confidence': 0.0,
                'symptoms': ['The model could not complete an inference run.'],
                'causes': ['Inference environment issue.'],
                'recommendations': ['Retry later or inspect the model configuration.'],
                'supported_crops': self.supported_crops,
            }
