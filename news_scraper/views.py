from django.shortcuts import render
from .models import Article

def article_list(request):
    articles = Article.objects.filter(has_keywords=True)
    
    # Filter by keyword if provided
    keyword = request.GET.get('keyword')
    if keyword:
        articles = articles.filter(keywords_found__icontains=keyword)
    
    # Filter by source if provided
    source = request.GET.get('source')
    if source:
        articles = articles.filter(source_domain__icontains=source)
    
    context = {
        'articles': articles,
        'keywords':[
                    ("vitamin d", "Vitamin D"),
                    ("vitamin d3", "Vitamin D3"),
                    ("sun exposure", "Sun exposure"),
                    ("uv index", "UV index"),
                    ("cognitive", "Cognitive"),
                    ("dementia", "Dementia"),
        ]
,
        'sources': Article.objects.values_list('source_domain', flat=True).distinct(),
        'selected_keyword': keyword,
        'selected_source': source,
    }
    context["vd_result"] = request.session.get("vd_result")
    return render(request, 'news_scraper/article_list.html', context)

from .models import CuratedArticle

def curated_news_list(request):
    articles = CuratedArticle.objects.all()  # ordered by -date_published via Meta
    return render(request, "news_scraper/curated_list.html", {"articles": articles})
