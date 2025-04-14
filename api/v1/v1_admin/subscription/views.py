from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from subscription_app.models import Subscription, Plan
from .serializers import SubscriptionSerializer, PlanSerializer
from accounts.models import User


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.filter(is_active=True).defer("is_deleted", "deleted_at")
    serializer_class = PlanSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('plan_title',)

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAdminUser,)
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['user', 'plan', 'status', 'is_active']
    # search_fields = ['user__mobile_phone', 'user__email']
    # ordering_fields = ['start_date', 'end_date', 'created_at']
    # ordering = ['-created_at']

    # @action(detail=True, methods=['post'])
    # def renew(self, request, pk=None):
    #     subscription = self.get_object()
    #     plan_id = request.data.get('plan_id')
    #     duration_days = request.data.get('duration_days')
    #
    #     if plan_id:
    #         try:
    #             plan = Plan.objects.get(id=plan_id)
    #             subscription.renew(plan=plan)
    #         except Plan.DoesNotExist:
    #             return Response({'error': 'Plan not found'}, status=400)
    #     elif duration_days:
    #         subscription.renew(duration_days=duration_days)
    #     else:
    #         return Response({'error': 'Provide either plan_id or duration_days'}, status=400)
    #
    #     return Response(self.get_serializer(subscription).data)

    # @action(detail=True, methods=['post'])
    # def cancel(self, request, pk=None):
    #     subscription = self.get_object()
    #     subscription.cancel()
    #     return Response(self.get_serializer(subscription).data)

    # @action(detail=False, methods=['get'])
    # def expiring_soon(self, request):
    #     threshold = request.query_params.get('days', 7)
    #     try:
    #         threshold = int(threshold)
    #     except ValueError:
    #         threshold = 7
    #
    #     subscriptions = Subscription.objects.filter(
    #         end_date__gte=datetime.date.today(),
    #         end_date__lte=datetime.date.today() + datetime.timedelta(days=threshold),
    #         status=Subscription.Status.ACTIVE
    #     )
    #     serializer = self.get_serializer(subscriptions, many=True)
    #     return Response(serializer.data)
