from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.models import Property, User
from app import db

class PropertyRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def _prepare_property_features(self, property):
        """Combine property features into a single string for vectorization"""
        features = [
            property.title,
            property.description,
            property.property_type,
            property.location,
            f"bedrooms_{property.bedrooms}",
            f"bathrooms_{property.bathrooms}",
            f"price_range_{self._get_price_range(property.price)}"
        ]
        return ' '.join(filter(None, features))
    
    def _get_price_range(self, price):
        """Convert price to a range category"""
        if price < 100000:
            return 'low'
        elif price < 500000:
            return 'medium'
        else:
            return 'high'
    
    def get_similar_properties(self, property_id, limit=6):
        """Get similar properties based on features"""
        properties = Property.query.filter(Property.id != property_id).all()
        if not properties:
            return []
            
        target_property = Property.query.get(property_id)
        if not target_property:
            return []
            
        # Prepare feature texts
        property_texts = [self._prepare_property_features(p) for p in properties]
        target_text = self._prepare_property_features(target_property)
        
        # Add target property text to get its vector
        all_texts = property_texts + [target_text]
        
        # Calculate TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarity scores
        cosine_similarities = cosine_similarity(
            tfidf_matrix[-1:], tfidf_matrix[:-1]
        ).flatten()
        
        # Get top similar properties
        similar_indices = cosine_similarities.argsort()[-limit:][::-1]
        return [properties[i] for i in similar_indices]
    
    def get_personalized_recommendations(self, user_id, limit=6):
        """Get personalized recommendations based on user's viewing history"""
        user = User.query.get(user_id)
        if not user:
            return []
            
        # Get user's viewed properties
        viewed_properties = user.viewed_properties
        if not viewed_properties:
            # If no viewing history, return popular properties
            return Property.query.order_by(Property.views.desc()).limit(limit).all()
            
        # Combine features of all viewed properties
        viewed_features = [
            self._prepare_property_features(p) for p in viewed_properties
        ]
        viewed_text = ' '.join(viewed_features)
        
        # Get all other properties
        all_properties = Property.query.filter(
            ~Property.id.in_([p.id for p in viewed_properties])
        ).all()
        
        if not all_properties:
            return []
            
        # Prepare feature texts
        property_texts = [self._prepare_property_features(p) for p in all_properties]
        
        # Add user's combined preferences to get its vector
        all_texts = property_texts + [viewed_text]
        
        # Calculate TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarity scores
        cosine_similarities = cosine_similarity(
            tfidf_matrix[-1:], tfidf_matrix[:-1]
        ).flatten()
        
        # Get top recommendations
        recommended_indices = cosine_similarities.argsort()[-limit:][::-1]
        return [all_properties[i] for i in recommended_indices]