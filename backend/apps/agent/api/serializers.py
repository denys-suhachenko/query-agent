from rest_framework import serializers


class AgentQuerySerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=5000,
        trim_whitespace=True,
    )
