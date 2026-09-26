from django.urls import path

from apps.agent.api.views import AgentQueryStreamView, AgentQueryView

urlpatterns = [
    path(
        "query/",
        AgentQueryView.as_view(),
        name="agent-query",
    ),
    path(
        "query/stream/",
        AgentQueryStreamView.as_view(),
        name="agent-query-stream",
    ),
]
