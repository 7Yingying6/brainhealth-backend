# insights/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .questions import QUESTIONNAIRE, score_total, classify
from .models import Factoid, LifestyleTip

SESSION_KEYS = {
    "answers": "vd_answers",   # list[int|None]
    "result": "vd_result",     # "Adequate"|"Borderline"|"Inadequate"
}

@api_view(['POST'])
def questionnaire_start(request):
    """Initialize a new questionnaire session"""
    # initialise answers list equal to number of questions
    request.session[SESSION_KEYS["answers"]] = [None] * len(QUESTIONNAIRE)
    request.session.pop(SESSION_KEYS["result"], None)
    request.session.modified = True
    
    # Format questions for frontend
    questions = []
    for i, q in enumerate(QUESTIONNAIRE):
        questions.append({
            'id': i,
            'code': q['code'],
            'text': q['text'],
            'helper': q.get('helper', ''),
            'options': [{
                'code': j,
                'text': opt['label'],
                'score': opt['score']
            } for j, opt in enumerate(q['options'])]
        })
    
    return Response({
        'message': 'Questionnaire initialized',
        'questions': questions,
        'total_questions': len(QUESTIONNAIRE),
        'next_question_index': 0
    })

@api_view(['GET', 'POST'])
def questionnaire_question(request, index: int):
    """Get question or submit answer"""
    answers = request.session.get(SESSION_KEYS["answers"])
    if answers is None:
        return Response({
            'error': 'Session expired. Please restart questionnaire.'
        }, status=status.HTTP_400_BAD_REQUEST)

    qcount = len(QUESTIONNAIRE)
    index = max(0, min(index, qcount - 1))
    question = QUESTIONNAIRE[index]
    selected = answers[index]

    if request.method == "GET":
        return Response({
            'question': {
                'index': index,
                'total': qcount,
                'code': question['code'],
                'text': question['text'],
                'helper': question.get('helper', ''),
                'options': [{'label': opt['label'], 'value': i} for i, opt in enumerate(question['options'])]
            },
            'selected': selected,
            'is_last': index == qcount - 1
        })

    if request.method == "POST":
        action = request.data.get("action")
        chosen = request.data.get("option")
        
        # save selected option if provided
        if chosen is not None:
            answers[index] = int(chosen)
            request.session[SESSION_KEYS["answers"]] = answers
            request.session.modified = True

        if action == "back":
            prev_idx = max(0, index - 1)
            return Response({'next_index': prev_idx})

        if action in ("next", "finish"):
            next_idx = index + 1
            if next_idx < qcount:
                return Response({'next_index': next_idx})
            # finished - compute and store result
            total = score_total(answers)
            result = classify(total)
            request.session[SESSION_KEYS["result"]] = result
            request.session.modified = True
            return Response({
                'completed': True,
                'total_score': total,
                'result': result
            })

@api_view(['POST', 'GET'])
def questionnaire_result(request):
    """Submit answers and get questionnaire result"""
    if request.method == 'POST':
        # Save all answers and calculate result
        answers_data = request.data.get('answers', [])
        if not answers_data:
            return Response({
                'error': 'No answers provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save answers to session
        request.session[SESSION_KEYS["answers"]] = answers_data
        
        # Calculate result
        total = score_total(answers_data)
        result = classify(total)
        request.session[SESSION_KEYS["result"]] = result
        request.session.modified = True
        
        return Response({
            'result': result,
            'total_score': total,
            'classification': {
                'Adequate': 'Your vitamin D level appears adequate',
                'Borderline': 'Your vitamin D level may be borderline', 
                'Inadequate': 'Your vitamin D level may be inadequate'
            }.get(result, '')
        })
    
    # GET method - return existing result
    result = request.session.get(SESSION_KEYS["result"])
    answers = request.session.get(SESSION_KEYS["answers"])
    total = score_total(answers) if answers else None

    if not result:
        return Response({
            'error': 'No result available. Please complete the questionnaire first.'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'result': result,
        'total_score': total,
        'classification': {
            'Adequate': 'Your vitamin D level appears adequate',
            'Borderline': 'Your vitamin D level may be borderline',
            'Inadequate': 'Your vitamin D level may be inadequate'
        }.get(result, '')
    })

@api_view(['GET'])
def hub(request):
    """Get hub information"""
    return Response({
        'title': 'Vitamin D & Brain Health',
        'description': 'Low vitamin D has been associated with smaller brain volumes and poorer cognitive scores in observational research. Sun exposure, skin type, season, clothing coverage, and diet/supplements all influence your vitamin D status.',
        'factors': [
            {'title': 'Sun exposure', 'description': 'time outdoors between 10am-3pm'},
            {'title': 'Skin type', 'description': 'darker skin synthesises vitamin D more slowly'},
            {'title': 'Location & season', 'description': 'southern states in winter have lower UV'},
            {'title': 'Clothing coverage', 'description': 'more covered = less UV to skin'},
            {'title': 'Diet & supplements', 'description': 'oily fish, fortified milk/margarine, eggs; supplements can help'}
        ]
    })

@api_view(['GET'])
def disclaimer(request):
    """Get disclaimer information"""
    return Response({
        'title': 'Supplementation Disclaimer',
        'content': 'This tool provides general information only and should not replace professional medical advice. Please consult with a healthcare provider before starting any vitamin D supplementation.'
    })

@api_view(['GET'])
def learn_more(request):
    """Get educational content"""
    return Response({
        'title': 'Learn More About Vitamin D',
        'sources': [
             {
                 'name': 'UniSA - Research news on vitamin D & brain health',
                 'url': 'https://www.unisa.edu.au/Media-Centre/News/'
             },
             {
                 'name': 'ABS - Australian Health Survey (general health stats)',
                 'url': 'https://www.abs.gov.au/'
             },
             {
                 'name': 'SBS Health - Public-facing explainers and news',
                 'url': 'https://www.sbs.com.au/news/health'
             }
         ],
        'cards': [
            {
                'title': 'Vitamin D & Brain Function',
                'text': 'Research suggests vitamin D receptors in the brain may influence cognitive performance.'
            },
            {
                'title': 'Sun Exposure Guidelines', 
                'text': 'Safe sun exposure varies by skin type, location, and season.'
            },
            {
                'title': 'Dietary Sources',
                'text': 'Oily fish, fortified foods, and supplements can help maintain vitamin D levels.'
            }
        ]
    })

@api_view(['GET'])
def dashboard(request):
    """Get dashboard data"""
    return Response({
        'title': 'Data Awareness Dashboard',
        'description': 'Explore vitamin D facts and lifestyle tips'
    })

@api_view(['GET'])
def api_factoids(request):
    data = [
        {
            "id": f.id,
            "title": f.title,
            "text": f.text,
            "badge": f.badge,
            "source_name": f.source_name,
            "source_url": f.source_url,
            "icon": f.icon,
        }
        for f in Factoid.objects.filter(is_active=True).order_by("order_index", "id")
    ]
    return JsonResponse(data, safe=False)

@api_view(['GET'])
def api_tips(request):
    data = [
        {
            "id": t.id,
            "title": t.title,
            "impact": t.impact,
            "front_summary": t.front_summary,
            "back_detail": t.back_detail,
            "icon": t.icon,
        }
        for t in LifestyleTip.objects.filter(is_active=True).order_by("order_index", "id")
    ]
    return JsonResponse(data, safe=False)
