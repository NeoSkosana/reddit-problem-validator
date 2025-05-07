from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from app.scraper.scraper import RedditScraper
from app.ai_analyzer.analyzer import RedditAnalyzer

class ProblemValidationView(APIView):
    """API view for problem validation workflow"""
    
    def post(self, request):
        """Handle problem validation request"""
        problem_statement = request.data.get('problem_statement')
        keywords = request.data.get('keywords', [])
        
        try:
            # Initialize our existing components
            scraper = RedditScraper()
            analyzer = RedditAnalyzer()
            
            # Use scraper to collect data
            discovered_subreddits = scraper._discover_subreddits(keywords)
            scraped_data = scraper.fetch_posts_and_comments(discovered_subreddits)
            
            # Use analyzer to process data
            validation_results = analyzer.validate_problem(scraped_data, problem_statement)
            
            return Response({
                'status': 'success',
                'results': validation_results
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'dashboard/index.html')