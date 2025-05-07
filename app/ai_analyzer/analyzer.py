import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from typing import List, Dict, Any
import pandas as pd

class RedditAnalyzer:
    def __init__(self):
        """Initialize the analyzer with required models and tools."""
        # Download required NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        # Initialize NLTK's VADER sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize text vectorizer for topic modeling
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            max_df=0.95,
            min_df=2
        )
        
        # Initialize topic modeling
        self.topic_model = NMF(n_components=5, random_state=42)

    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of given texts using NLTK's VADER.
        
        Args:
            texts: List of text content to analyze
            
        Returns:
            List of sentiment analysis results
        """
        try:
            results = []
            for text in texts:
                if not text or not isinstance(text, str):
                    continue
                    
                scores = self.sentiment_analyzer.polarity_scores(text)
                sentiment_label = 'POSITIVE' if scores['compound'] > 0 else 'NEGATIVE'
                results.append({
                    'label': sentiment_label,
                    'score': abs(scores['compound']),
                    'details': scores
                })
            return results
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return []

    def extract_topics(self, texts: List[str]) -> Dict[str, Any]:
        """
        Extract main topics from the texts using NMF.
        
        Args:
            texts: List of text content for topic modeling
            
        Returns:
            Dictionary containing topics and their key terms
        """
        try:
            # Remove empty texts
            texts = [text for text in texts if text and isinstance(text, str)]
            
            # Create document-term matrix
            dtm = self.vectorizer.fit_transform(texts)
            
            # Extract topics
            topic_matrix = self.topic_model.fit_transform(dtm)
            
            # Get feature names (terms)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Extract top terms for each topic
            topics = {}
            for topic_idx, topic in enumerate(self.topic_model.components_):
                top_terms = [feature_names[i] for i in topic.argsort()[:-10:-1]]
                topics[f"topic_{topic_idx+1}"] = top_terms
                
            return {
                "topics": topics,
                "document_topic_matrix": topic_matrix.tolist()
            }
        except Exception as e:
            print(f"Error in topic modeling: {e}")
            return {"topics": {}, "document_topic_matrix": []}

    def validate_problem(self, scraped_data: pd.DataFrame, problem_statement: str) -> Dict[str, Any]:
        """
        Validate a proposed problem using scraped Reddit data.
        
        Args:
            scraped_data: DataFrame containing Reddit posts and comments
            problem_statement: The problem to validate
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Combine post and comment content
            all_content = scraped_data['content'].fillna('').tolist()
            
            # Analyze sentiment
            sentiment_results = self.analyze_sentiment(all_content)
            
            # Extract topics
            topic_results = self.extract_topics(all_content)
            
            # Calculate validation metrics
            sentiment_stats = {
                'positive': sum(1 for result in sentiment_results if result['label'] == 'POSITIVE'),
                'negative': sum(1 for result in sentiment_results if result['label'] == 'NEGATIVE')
            }
            
            return {
                'problem_statement': problem_statement,
                'sentiment_analysis': sentiment_stats,
                'topic_analysis': topic_results,
                'data_volume': len(all_content),
                'validation_score': self._calculate_validation_score(sentiment_stats, topic_results)
            }
        except Exception as e:
            print(f"Error in problem validation: {e}")
            return {}

    def _calculate_validation_score(self, sentiment_stats: Dict[str, int], topic_results: Dict[str, Any]) -> float:
        """
        Calculate a validation score for the problem based on analysis results.
        
        Args:
            sentiment_stats: Dictionary of sentiment statistics
            topic_results: Dictionary of topic modeling results
            
        Returns:
            Float between 0 and 1 indicating problem validity
        """
        try:
            # Simple scoring method - can be enhanced based on specific requirements
            total_sentiments = sentiment_stats['positive'] + sentiment_stats['negative']
            if total_sentiments == 0:
                return 0.0
                
            # Calculate sentiment ratio (higher negative sentiment might indicate a real problem)
            sentiment_score = sentiment_stats['negative'] / total_sentiments
            
            # Calculate topic coherence (more focused topics might indicate a real problem)
            topic_count = len(topic_results.get('topics', {}))
            topic_score = min(topic_count / 5, 1.0)  # Normalize to 0-1
            
            # Combine scores (can be weighted differently based on importance)
            final_score = (sentiment_score * 0.7) + (topic_score * 0.3)
            
            return round(final_score, 2)
        except Exception as e:
            print(f"Error calculating validation score: {e}")
            return 0.0
