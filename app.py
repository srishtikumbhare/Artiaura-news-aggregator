import os
from datetime import datetime
import feedparser
from dateutil import parser
from dotenv import load_dotenv
from newsapi import NewsApiClient


# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variables
api_key = os.getenv('NEWSAPI_KEY')

if not api_key:
    raise ValueError("API key not found. Please set the NEWSAPI_KEY environment variable.")

# Initialize NewsApiClient with the API key
newsapi = NewsApiClient(api_key=api_key)

def format_date(date_str):
    """Converts a date string into 'dd/mm/yy h:m' format."""
    try:
        # Use dateutil.parser to handle multiple date formats
        date_obj = parser.parse(date_str)
        
        # Convert to the desired format
        return date_obj.strftime("%d/%m/%y %H:%M")
    except (ValueError, TypeError):
        return "Invalid date format"

def fetch_news_from_newsapi(user_query):
    # Get top headlines based on user query
    top_headlines = newsapi.get_top_headlines(q=user_query, language='en', country='us')
    top_headlines = top_headlines['articles'][:10]

    # Get all articles based on user query
    all_articles = newsapi.get_everything(q=user_query, language='en', sort_by='relevancy')
    all_articles = all_articles['articles'][:10]

    return top_headlines, all_articles

def fetch_news_from_rss(rss_urls, user_query):
    rss_articles = []

    for url in rss_urls:
        feed = feedparser.parse(url)

        for entry in feed.entries[:30]:  # Limit to the first 10 articles per feed
            # Check if the user query is in the title or summary
            if user_query.lower() in entry.title.lower() or (hasattr(entry, 'summary') and user_query.lower() in entry.summary.lower()):
                # Format the published date if it exists
                published = entry.published if 'published' in entry else 'No date available'
                formatted_date = format_date(published) if published != 'No date available' else published

                # Append the formatted article data
                rss_articles.append({
                    'title': entry.title,
                    'source': feed.feed.title if 'title' in feed.feed else 'Unknown Source',
                    'published': formatted_date,
                    'link': entry.link,
                })

    return rss_articles

def display_news(top_headlines, all_articles, rss_articles):
    # Display top headlines from the News API
    print("\nTop Headlines from News API:\n")
    for headline in top_headlines:
        formatted_date = format_date(headline['publishedAt'])
        print(f"Title: {headline['title']}\nSource: {headline['source']['name']}\nPublished: {formatted_date}\nURL: {headline['url']}\n")

    # Display all articles from the News API
    print("\nAll Articles from News API:\n")
    for article in all_articles:
        formatted_date = format_date(article['publishedAt'])
        print(f"Title: {article['title']}\nSource: {article['source']['name']}\nPublished: {formatted_date}\nURL: {article['url']}\n")

    # Display articles from RSS feeds
    print("\nArticles from RSS Feeds:\n")
    for article in rss_articles:
        print(f"Title: {article['title']}\nSource: {article['source']}\nPublished: {article['published']}\nURL: {article['link']}\n")

def get_news_from_terminal():
    # Accept query input from the terminal
    user_query = input("Enter your search query: ")

    # Define a list of RSS feed URLs to scrape
    rss_urls = [
        'https://www.indiatoday.in/rss/1206578',
    ]

    # Fetch news using the News API
    top_headlines, all_articles = fetch_news_from_newsapi(user_query)

    # Fetch news from RSS feeds
    rss_articles = fetch_news_from_rss(rss_urls, user_query)

    # Display all news articles
    display_news(top_headlines, all_articles, rss_articles)

if __name__ == '__main__':
    get_news_from_terminal()
