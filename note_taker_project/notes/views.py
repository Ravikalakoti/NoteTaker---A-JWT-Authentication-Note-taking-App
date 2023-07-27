# notes/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from .models import Note
from .serializers import NoteSerializer
from rest_framework import generics, permissions
from django.db.models import Q


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class TokenObtainPairView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshViewCustom(TokenRefreshView):
    pass


class NoteListView(generics.ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated,)


class NoteSearchView(generics.ListAPIView):
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        search_query = self.request.query_params.get('q', None)
        if search_query:
            return Note.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query), user=self.request.user)
        else:
            return Note.objects.none()

