from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MemberViewSet,
    MemberListCreateAPIView,
    MemberDetailAPIView,
)

router = DefaultRouter()
router.register('members', MemberViewSet, basename='member')

urlpatterns = [
    # ViewSet routes: /api/members/ and /api/members/<id>/
    path('', include(router.urls)),

    # APIView routes: /api/apiview/members/ and /api/apiview/members/<id>/
    path('apiview/members/', MemberListCreateAPIView.as_view(), name='apiview-member-list'),
    path('apiview/members/<int:id>/', MemberDetailAPIView.as_view(), name='apiview-member-detail'),
]
