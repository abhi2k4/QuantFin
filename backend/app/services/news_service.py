import asyncio
import aiohttp
import feedparser
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any
from datetime import datetime
import re

class NewsService:
    """Service for fetching and analyzing financial news"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
    
    async def fetch_google_news(self, query: str, max_items: int = 20) -> List[Dict]:
        """Fetch Google News RSS for financial topics"""
        try:
            base_url = "https://news.google.com/rss/search?q="
            url = f"{base_url}{query.replace(' ', '+')}"
            
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_items]:
                article = {
                    "title": entry.get('title', ''),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "source": "Google News",
                    "summary": BeautifulSoup(entry.get('summary', ''), "html.parser").get_text()
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error fetching Google News: {e}")
            return []
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using VADER and TextBlob"""
        try:
            # VADER sentiment
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # TextBlob sentiment
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Combined sentiment score
            combined_score = (vader_scores['compound'] + textblob_polarity) / 2
            
            # Sentiment label
            if combined_score >= 0.05:
                label = "Positive"
            elif combined_score <= -0.05:
                label = "Negative"
            else:
                label = "Neutral"
            
            return {
                "vader_compound": vader_scores['compound'],
                "vader_positive": vader_scores['pos'],
                "vader_negative": vader_scores['neg'],
                "vader_neutral": vader_scores['neu'],
                "textblob_polarity": textblob_polarity,
                "textblob_subjectivity": textblob_subjectivity,
                "combined_score": combined_score,
                "sentiment_label": label
            }
        except Exception as e:
            return {
                "error": str(e),
                "combined_score": 0.0,
                "sentiment_label": "Neutral"
            }
    
    async def get_financial_news(self, symbols: List[str]) -> List[Dict]:
        """Get and analyze financial news for given symbols"""
        try:
            all_news = []
            
            for symbol in symbols[:5]:  # Limit to prevent rate limiting
                # Clean symbol for search
                clean_symbol = symbol.replace('.NS', '')
                
                # Fetch news
                articles = await self.fetch_google_news(f"{clean_symbol} stock", max_items=10)
                
                for article in articles:
                    # Analyze sentiment
                    text = f"{article['title']} {article['summary']}"
                    sentiment = await self.analyze_sentiment(text)
                    
                    news_item = {
                        "symbol": symbol,
                        "title": article['title'],
                        "url": article['link'],
                        "source": article['source'],
                        "published_at": article['published'],
                        "summary": article['summary'][:500],
                        "sentiment_score": sentiment['combined_score'],
                        "sentiment_label": sentiment['sentiment_label'],
                        "sentiment_details": sentiment
                    }
                    all_news.append(news_item)
            
            return all_news
        except Exception as e:
            raise Exception(f"News analysis error: {str(e)}")
    
    async def analyze_market_sentiment(self, symbols: List[str]) -> Dict:
        """Analyze overall market sentiment"""
        try:
            news_data = await self.get_financial_news(symbols)
            
            if not news_data:
                return {"error": "No news data available"}
            
            sentiments = [item['sentiment_score'] for item in news_data]
            
            # Calculate metrics
            avg_sentiment = np.mean(sentiments)
            sentiment_std = np.std(sentiments)
            positive_news = sum(1 for s in sentiments if s > 0.05)
            negative_news = sum(1 for s in sentiments if s < -0.05)
            neutral_news = len(sentiments) - positive_news - negative_news
            
            # Overall market sentiment
            if avg_sentiment >= 0.1:
                market_sentiment = "Bullish"
            elif avg_sentiment <= -0.1:
                market_sentiment = "Bearish"
            else:
                market_sentiment = "Neutral"
            
            return {
                "market_sentiment": market_sentiment,
                "average_sentiment": round(avg_sentiment, 3),
                "sentiment_volatility": round(sentiment_std, 3),
                "total_articles": len(news_data),
                "positive_count": positive_news,
                "negative_count": negative_news,
                "neutral_count": neutral_news,
                "positive_percentage": round((positive_news / len(sentiments)) * 100, 1),
                "negative_percentage": round((negative_news / len(sentiments)) * 100, 1),
                "top_news": news_data[:5],
                "analysis_date": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Market sentiment analysis error: {str(e)}")