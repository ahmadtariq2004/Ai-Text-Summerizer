from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SummarizeSerializer
from .services import SummarizationError, summarize_with_qwen


class SummarizeAPIView(APIView):
    def post(self, request):
        serializer = SummarizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            summary = summarize_with_qwen(
                serializer.validated_data["text"], serializer.validated_data["style"]
            )
        except SummarizationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(
            {
                "summary": summary,
                "model": "Qwen 3",
                "style": serializer.validated_data["style"],
            }
        )
