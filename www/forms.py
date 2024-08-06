from django.forms import ModelForm

from .models import Scenario

class ScenarioForm(ModelForm):
    class Meta:
        model = Scenario
        fields = "__all__"
