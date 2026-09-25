from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.agent import run_agent
from .serializers import AgentQuerySerializer


class AgentQueryView(APIView):
    def post(self, request: Request) -> Request:
        serializer = AgentQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = run_agent(
            serializer.validated_data["message"],
        )

        return Response(result)
