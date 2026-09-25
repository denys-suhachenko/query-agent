from django.urls import path

from apps.agent.api.views import AgentQueryView

urlpatterns = [
    path("query/", AgentQueryView.as_view(), name="agent-query"),
]
