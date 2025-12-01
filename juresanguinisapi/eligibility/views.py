from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.evaluator import evaluate_lineage

from .serializers import EvaluationRequestSerializer


class EvaluateLineageView(APIView):
    """Accepts applicant lineage data and returns an eligibility evaluation."""

    def post(self, request):
        serializer = EvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        people = EvaluationRequestSerializer.build_person_index(serializer.validated_data)
        lineage_links = EvaluationRequestSerializer.build_lineage_links(
            serializer.validated_data, people
        )
        process_context = EvaluationRequestSerializer.normalize_context(
            serializer.validated_data
        )

        result = evaluate_lineage(lineage_links, process_context=process_context)

        payload = {
            "overall_status": result.overall_status.value,
            "confidence": result.confidence.value,
            "court_viability": result.court_viability.value,
            "needs_lawyer": result.needs_lawyer,
            "acquisition_mode": result.acquisition_mode.value,
            "explanations": result.explanations,
            "rule_outcomes": [
                {
                    "rule_id": outcome.rule_id,
                    "status": outcome.status.value,
                    "notes": outcome.notes,
                    "confidence": outcome.confidence.value,
                    "needs_lawyer": outcome.needs_lawyer,
                }
                for outcome in result.rule_outcomes
            ],
        }

        return Response(payload, status=status.HTTP_200_OK)
