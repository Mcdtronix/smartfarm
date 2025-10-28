import pickle
import os
import numpy as np
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CropRecommendationService:
    """Service class for handling crop recommendations using ML model"""
    
    def __init__(self):
        self.model = None
        self.feature_mapping = {
            'soil_type': {
                'loamy': 0, 'clay': 1, 'sandy': 2, 'silt': 3, 'peat': 4, 'chalky': 5
            },
            'fertilizer_type': {
                'organic': 0, 'urea': 1, 'dap': 2, 'npk': 3, 'compost': 4
            },
            'water_access': {
                'rainfed': 0, 'irrigation': 1, 'mixed': 2
            }
        }
        self.crop_names = [
            'Maize', 'Rice', 'Wheat', 'Barley', 'Sorghum', 'Millet', 'Beans', 
            'Groundnuts', 'Soybeans', 'Potatoes', 'Sweet Potatoes', 'Cassava',
            'Tomatoes', 'Onions', 'Cabbage', 'Carrots', 'Spinach', 'Lettuce',
            'Peppers', 'Eggplant', 'Cucumber', 'Pumpkin', 'Watermelon', 'Banana',
            'Mango', 'Avocado', 'Coffee', 'Tea', 'Sugarcane', 'Cotton'
        ]
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'model', 'crop_recommendation_model.pkl')
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading ML model: {str(e)}")
            self.model = None
    
    def _encode_features(self, land_size, soil_type, fertilizer_type, water_access, location=None):
        """Encode categorical features to numerical values"""
        try:
            # Basic feature encoding
            features = [
                float(land_size),
                self.feature_mapping['soil_type'].get(soil_type, 0),
                self.feature_mapping['fertilizer_type'].get(fertilizer_type, 0),
                self.feature_mapping['water_access'].get(water_access, 0)
            ]
            
            # Add some derived features
            features.extend([
                float(land_size) * 0.1,  # Normalized land size
                self.feature_mapping['soil_type'].get(soil_type, 0) * 0.1,
                self.feature_mapping['fertilizer_type'].get(fertilizer_type, 0) * 0.1,
                self.feature_mapping['water_access'].get(water_access, 0) * 0.1
            ])
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            logger.error(f"Error encoding features: {str(e)}")
            return None
    
    def get_recommendations(self, land_size, soil_type, fertilizer_type, water_access, location=None, top_n=5):
        """Get crop recommendations based on farm parameters"""
        if self.model is None:
            logger.warning("ML model not loaded, using fallback recommendations")
            return self._get_fallback_recommendations(land_size, soil_type, fertilizer_type, water_access)
        
        try:
            # Encode features
            features = self._encode_features(land_size, soil_type, fertilizer_type, water_access, location)
            if features is None:
                return self._get_fallback_recommendations(land_size, soil_type, fertilizer_type, water_access)
            
            # Get predictions
            probabilities = self.model.predict_proba(features)[0]
            class_indices = np.argsort(probabilities)[::-1][:top_n]
            
            recommendations = []
            for idx in class_indices:
                if idx < len(self.crop_names):
                    crop_name = self.crop_names[idx]
                    score = probabilities[idx]
                    confidence = 'high' if score > 0.7 else 'medium' if score > 0.4 else 'low'
                    
                    recommendations.append({
                        'crop_name': crop_name,
                        'suitability_score': float(score),
                        'confidence_level': confidence
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting ML recommendations: {str(e)}")
            return self._get_fallback_recommendations(land_size, soil_type, fertilizer_type, water_access)
    
    def _get_fallback_recommendations(self, land_size, soil_type, fertilizer_type, water_access):
        """Fallback recommendations when ML model is not available"""
        recommendations = []
        
        # Basic rule-based recommendations
        if soil_type == 'loamy' and float(land_size) >= 5:
            recommendations.extend([
                {'crop_name': 'Maize', 'suitability_score': 0.85, 'confidence_level': 'high'},
                {'crop_name': 'Beans', 'suitability_score': 0.80, 'confidence_level': 'high'},
                {'crop_name': 'Wheat', 'suitability_score': 0.75, 'confidence_level': 'medium'}
            ])
        elif soil_type == 'clay' or water_access == 'irrigation':
            recommendations.extend([
                {'crop_name': 'Rice', 'suitability_score': 0.80, 'confidence_level': 'high'},
                {'crop_name': 'Sugarcane', 'suitability_score': 0.70, 'confidence_level': 'medium'}
            ])
        elif fertilizer_type == 'organic' and float(land_size) < 5:
            recommendations.extend([
                {'crop_name': 'Tomatoes', 'suitability_score': 0.85, 'confidence_level': 'high'},
                {'crop_name': 'Onions', 'suitability_score': 0.80, 'confidence_level': 'high'},
                {'crop_name': 'Cabbage', 'suitability_score': 0.75, 'confidence_level': 'medium'}
            ])
        elif soil_type == 'sandy' and water_access == 'irrigation':
            recommendations.extend([
                {'crop_name': 'Groundnuts', 'suitability_score': 0.80, 'confidence_level': 'high'},
                {'crop_name': 'Sweet Potatoes', 'suitability_score': 0.75, 'confidence_level': 'medium'}
            ])
        else:
            # Default recommendations
            recommendations.extend([
                {'crop_name': 'Maize', 'suitability_score': 0.70, 'confidence_level': 'medium'},
                {'crop_name': 'Beans', 'suitability_score': 0.65, 'confidence_level': 'medium'},
                {'crop_name': 'Potatoes', 'suitability_score': 0.60, 'confidence_level': 'medium'}
            ])
        
        return recommendations[:5]  # Return top 5 recommendations

# Global instance
crop_service = CropRecommendationService()
