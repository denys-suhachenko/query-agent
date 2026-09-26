import json

from django.http import StreamingHttpResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.agent import run_agent, stream_agent
from .serializers import AgentQuerySerializer


class AgentQueryView(APIView):
    def post(self, request: Request) -> Request:
        serializer = AgentQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = run_agent(
            serializer.validated_data["message"],
        )

        return Response(result)


class AgentQueryStreamView(APIView):
    def post(self, request: Request) -> StreamingHttpResponse:
        serializer = AgentQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]

        def event_stream():
            try:
                for event in stream_agent(message):
                    yield ("data: " + json.dumps(event, default=str) + "\n\n")

            except Exception as exc:
                yield (
                    "data: "
                    + json.dumps(
                        {
                            "type": "error",
                            "message": str(exc),
                        }
                    )
                    + "\n\n"
                )

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )

        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"

        return response
