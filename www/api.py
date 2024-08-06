from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

import json

from .models import Scenario

from patient import RaspatientPi
from raspatientpi.config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID

@require_POST
def play_scenario(request):
    data = json.loads(request.body)
    
    scenario = get_object_or_404(Scenario, pk=data.get('scenario'))
    voice = data.get('voice')
    use_avatar = data.get('use_avatar')

    pp = RaspatientPi(OPENAI_API_KEY, OPENAI_ASSISTANT_ID, voice=voice, log_on_mqtt=True, use_avatar=use_avatar)

    thread = pp.create_thread(scenario.description)
    pp.loop(thread)

    return JsonResponse(True, safe=False)

def get_scenario_data(request, pk):
    scenario = get_object_or_404(Scenario, pk=pk)

    return JsonResponse({
        'id': scenario.id,
        'name': scenario.name,
        'description': scenario.description,
        'gender': scenario.gender.lower()
    })

@require_POST
def avatar_api(request):
    text = request.POST.get('text')
    voice = request.POST.get('voice')

    pp = RaspatientPi(OPENAI_API_KEY, None, voice=voice)
    data = pp.openai_tts_with_captions(text)

    return JsonResponse(data)
