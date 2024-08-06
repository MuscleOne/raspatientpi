from django.urls import path

from . import views, api

urlpatterns = [
    path("", views.index, name="index"),

    path('scenario/create/', views.ScenarioCreationFormView.as_view(), name="scenario_create"),
    path('scenario/<pk>/edit/', views.ScenarioUpdateView.as_view(), name='scenario_edit'),
    path('scenario/<pk>/delete/', views.delete_scenario, name='scenario_delete'),
    path('scenario/<pk>/play/', views.play_scenario, name='scenario_play'),

    path('api/scenario/<pk>', api.get_scenario_data, name='api_scenario'),
    path('api/play/', api.play_scenario, name='api_play'),

    # Experiment with 3D avatar
    path('avatar/', views.avatar, name='avatar'),
    path('avatar/api', api.avatar_api, name='api_avatar'),
]
