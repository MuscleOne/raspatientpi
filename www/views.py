from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView, UpdateView
from django.views.decorators.http import require_POST

from .models import Scenario
from .forms import ScenarioForm

def index(request):
    return render(request, "www/index.html", { 'scenarios': Scenario.objects.all() })

class ScenarioCreationFormView(FormView):
    template_name = 'www/scenario_form.html'
    form_class = ScenarioForm

    def form_valid(self, form):
        form.save()
        return redirect('index')

class ScenarioUpdateView(UpdateView):
    model = Scenario
    form_class = ScenarioForm
    template_name = 'www/scenario_form.html'

    def form_valid(self, form):
        form.save()
        return redirect('index')
    
@require_POST
def delete_scenario(request, pk):
    get_object_or_404(Scenario, pk=pk).delete()
    return redirect('index')

def play_scenario(request, pk):
    scenario = get_object_or_404(Scenario, pk=pk)
    return render(request, "www/play.html", { 'scenario_id': scenario.id })

def avatar(request):
    return render(request, "www/avatar.html")
