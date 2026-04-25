import pytest
from apiproxy.service.str_util import trim_indent
from apiproxy.generate.java_model import generate_java_model

def test_generate_java_model() -> None:
    json_str = trim_indent('''
        {
        "search_metadata": {
            "id": "68306006ac29783e0920f33d",
            "status": "Success",
            "json_endpoint": "https://serpapi.com/searches/f50945285d31c18f/68306006ac29783e0920f33d.json",
            "created_at": "2025-05-23 11:46:14 UTC",
            "processed_at": "2025-05-23 11:46:14 UTC",
            "google_news_light_url": "https://www.google.com/search?q=Coffee&oq=Coffee&sourceid=chrome&ie=UTF-8&gbv=1&tbm=nws",
            "raw_html_file": "https://serpapi.com/searches/f50945285d31c18f/68306006ac29783e0920f33d.html",
            "total_time_taken": 0.72
        },
        "search_parameters": {
            "engine": "google_news_light",
            "q": "Coffee",
            "google_domain": "google.com",
            "device": "desktop"
        },
        "search_information": {
            "query_displayed": "Coffee",
            "news_results_state": "Results for exact spelling"
        },
        "news_results": [
            {
            "position": 1,
            "title": "I Got a Sneak Peek of the Ratio Eight Series 2 Coffee Maker. Lord, It’s Beautiful",
            "link": "https://www.wired.com/story/ratio-eight-series-two-preview/",
            "source": "WIRED",
            "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUNGY6_aXSgAhnkxhIqpevyoFTonFJ3KHLw4AgRvGGLpf2ECCSZyy6kCOxuA&s",
            "snippet": "Ratio's new coffee maker is a luxury machine that avoids plastic and makes delicious coffee.",
            "date": "2 hours ago"
            },
            {
            "position": 2,
            "title": "The optimal time to drink coffee isn't when you normally have it",
            "link": "https://www.foxnews.com/food-drink/optimal-time-drink-coffee-isnt-when-you-normally-have",
            "source": "Fox News",
            "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUZkkyCl2tISQh15_BcN7jbqhVCCHyIoOjve0och1ZFQICE7g0iMUIWsAQ9w&s",
            "snippet": "Experts suggest delaying your coffee intake in the morning to align with natural cortisol levels, enhancing alertness and reducing the...",
            "date": "1 day ago"
            },
            {
            "position": 3,
            "title": "Yeti Reinvented the French Press, and It’s a Game-Changer for Coffee Lovers",
            "link": "https://www.foodandwine.com/yeti-rambler-french-press-coffee-maker-review-11739511",
            "source": "Food & Wine",
            "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR7KSW7amernGekEAfKAr4U7GJejaJPLNmEcIf7oz8pI0udnutb2JAN64OYKg&s",
            "snippet": "The Yeti Rambler French Press is a highly insulated press that keeps coffee hot for hours without the bitterness from over-steeped grounds.",
            "date": "1 day ago"
            }
        ],
        "serpapi_pagination": {
            "current": 1,
            "next": "https://serpapi.com/search.json?device=desktop&engine=google_news_light&google_domain=google.com&q=Coffee&start=10location=Austin%2C+TX%2C+Texas%2C+United+States"
        }
        }
        ''')
    
    code = generate_java_model(json_str.encode(), 'GoogleSearchResponse')
    print(code)
