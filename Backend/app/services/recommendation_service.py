from typing import Any, Dict

import httpx

from app.core.config import settings


class RecommendationService:
    def __init__(self):
        self.early_blight_plan = {
            'disease': 'Early Blight',
            'symptoms': [
                'Check older, lower leaves for brown spots with concentric rings and surrounding yellowing.',
                'Look for lesions that enlarge and cause lower leaves to yellow or dry.',
            ],
            'causes': [
                'Early blight is commonly associated with the fungus Alternaria, and disease pressure increases in warm, humid conditions.',
                'Infected crop debris, soil splash, and prolonged leaf wetness can help it spread.',
            ],
            'action_plan': [
                {
                    'timing': 'Today — verify and map',
                    'steps': [
                        'Inspect several plants in different parts of the field, starting with the oldest lower leaves.',
                        'Compare the spots with the symptoms above; photograph a clear close-up and note the affected rows or area.',
                        'If symptoms are atypical, rapidly spreading, or the crop is valuable, ask a local extension officer or agronomist to confirm before treating.',
                    ],
                },
                {
                    'timing': 'Today — reduce spread',
                    'steps': [
                        'When foliage is dry, remove only clearly infected leaves from a small number of affected plants; avoid stripping healthy foliage.',
                        'Place removed leaves and fallen crop debris in a bag or remove them from the field; do not leave infected material between rows.',
                        'Avoid handling wet plants and clean soil or plant debris from tools before moving to healthy rows.',
                    ],
                },
                {
                    'timing': 'Next irrigation',
                    'steps': [
                        'Water at the soil line where practical and avoid overhead irrigation or evening watering that keeps leaves wet overnight.',
                        'Maintain airflow by keeping plants appropriately spaced and controlling weeds without damaging crop roots.',
                        'Use clean mulch where suitable to reduce soil splash onto lower leaves.',
                    ],
                },
                {
                    'timing': 'Next 3–7 days',
                    'steps': [
                        'Recheck the marked area and nearby plants for new lesions; take photos from the same locations to compare spread.',
                        'Keep a simple record of affected rows, recent rain or irrigation, and actions taken.',
                        'If new lesions continue to appear or damage is increasing, seek local crop-specific advice on registered control options.',
                    ],
                },
                {
                    'timing': 'After harvest / next planting',
                    'steps': [
                        'Remove or properly manage infected crop residue and volunteer plants that can carry disease between crops.',
                        'Where practical, rotate away from tomato, potato, and other susceptible nightshades; confirm a suitable rotation with local guidance.',
                    ],
                },
            ],
            'recommendations': [
                'Confirm symptoms in the field before taking costly action.',
                'Prioritize dry-leaf scouting, sanitation, and reducing leaf wetness.',
                'Use a fungicide only if a local agricultural adviser recommends it and the product is registered for this crop and disease; follow its label, protective-equipment, harvest-interval, and resistance-management directions.',
            ],
            'safety_note': 'This image result is a screening aid, not a confirmed diagnosis. Do not mix or apply pesticides based only on this prediction.',
            'follow_up': 'Reinspect in 3–7 days, or sooner if the disease appears to be spreading quickly.',
        }

    def get_recommendations(self, disease_name: str, crop_name: str = '') -> Dict[str, Any]:
        disease = (disease_name or '').strip()
        key = disease.lower().replace('_', ' ')
        crop = (crop_name or '').strip().title()

        if key == 'early blight':
            return {**self.early_blight_plan, 'crop': crop or 'Crop'}

        return {
            'disease': disease or 'Unconfirmed crop issue',
            'crop': crop or 'Crop',
            'symptoms': ['Compare the image result with symptoms on multiple plants, including healthy and affected leaves.'],
            'causes': ['The image classifier result may be incorrect; visual stress can also result from pests, nutrient issues, or weather.'],
            'action_plan': [
                {
                    'timing': 'Today — inspect',
                    'steps': [
                        'Check several plants across the field and inspect both leaf surfaces, stems, and nearby plants.',
                        'Photograph the affected area and note when symptoms began, where they occur, and recent irrigation or weather.',
                        'Ask a local extension officer or agronomist to confirm the cause if symptoms are unclear or spreading.',
                    ],
                },
                {
                    'timing': 'Next 3–7 days — monitor',
                    'steps': [
                        'Mark the affected plants or rows and revisit them in 3–7 days to check for new symptoms.',
                        'Keep foliage as dry as practical, avoid moving through wet plants, and remove heavily affected debris only when safe and appropriate for the crop.',
                        'Do not apply pesticides or fertilizer solely from this image result; use only crop- and issue-specific local advice.',
                    ],
                },
            ],
            'recommendations': [
                'Use field inspection and local expert confirmation before choosing a treatment.',
                'Maintain a record of symptoms, location, weather, and changes over time.',
            ],
            'safety_note': 'This image result is a screening aid, not a confirmed diagnosis. Treatment depends on crop, growth stage, and local conditions.',
            'follow_up': 'Reinspect in 3–7 days, or seek local advice sooner if damage is increasing.',
        }

    def fetch_groq_explanation(self, disease_name: str) -> str:
        if not settings.GROQ_API_KEY:
            return 'Groq explanation not configured.'
        try:
            response = httpx.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {settings.GROQ_API_KEY}'},
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': [
                        {'role': 'user', 'content': f'Explain this crop disease in 3 sentences: {disease_name}'}
                    ],
                },
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get('choices', [{}])[0].get('message', {}).get('content', 'Groq explanation unavailable.')
        except Exception:
            return 'Groq explanation not available at the moment.'
