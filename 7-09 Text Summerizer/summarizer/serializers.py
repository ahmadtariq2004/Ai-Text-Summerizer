from rest_framework import serializers


class SummarizeSerializer(serializers.Serializer):
    text = serializers.CharField(
        min_length=80,
        max_length=20000,
        trim_whitespace=True,
        help_text="Text to summarize.",
    )
    style = serializers.ChoiceField(
        choices=["concise", "balanced", "detailed"],
        default="balanced",
        required=False,
    )
