from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app1.models import Member
from .serializers import MemberSerializer


# --- ViewSet style (router handles the URLs) ---

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all().order_by('id')
    serializer_class = MemberSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['firstname', 'lastname']


# --- APIView style (you write each method yourself) ---

class MemberListCreateAPIView(APIView):
    """GET list + POST create — same as ViewSet list/create."""

    def get(self, request):
        query = request.query_params.get('search', '').strip()
        members = Member.objects.all().order_by('id')

        if query:
            members = members.filter(firstname__icontains=query) | members.filter(
                lastname__icontains=query
            )

        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberDetailAPIView(APIView):
    """GET / PUT / PATCH / DELETE one member — same as ViewSet retrieve/update/destroy."""

    def get_object(self, id):
        return get_object_or_404(Member, id=id)

    def get(self, request, id):
        member = self.get_object(id)
        serializer = MemberSerializer(member)
        return Response(serializer.data)

    def put(self, request, id):
        member = self.get_object(id)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        member = self.get_object(id)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        member = self.get_object(id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
