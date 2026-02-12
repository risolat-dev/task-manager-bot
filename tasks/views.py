from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # Filtrlash va qidiruv (Buni qo'shish esdan chiqmasin)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['completed']
    search_fields = ['title']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Ushbu metod API-ga statistika qavatini qo'shadi.
        Manzil: /api/tasks/stats/
        """
        queryset = self.get_queryset()
        total = queryset.count()
        completed = queryset.filter(completed=True).count()
        uncompleted = total - completed

        return Response({
            "total_tasks": total,
            "completed_tasks": completed,
            "uncompleted_tasks": uncompleted,
            "status_message": f"Sizda {uncompleted} ta bajarilishi kerak bo'lgan ish bor."
        })