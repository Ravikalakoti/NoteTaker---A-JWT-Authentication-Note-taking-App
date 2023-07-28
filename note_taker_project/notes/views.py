# notes/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, TokenObtainPairSerializer, NoteSharingInvitationSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from .models import Note, NoteSharingInvitation
from .serializers import NoteSerializer
from rest_framework import generics, permissions
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()


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
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        # Get notes that belong to the authenticated user or are shared with the user
        shared_notes = NoteSharingInvitation.objects.filter(recipient=user).values_list('note__id', flat=True)
        queryset = Note.objects.filter(Q(user=user) |Q(id__in=shared_notes))
        return queryset

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
			return Note.objects.filter(
				Q(title__icontains=search_query) |
				Q(content__icontains=search_query),
				user=self.request.user
			)
		else:
			return Note.objects.none()


class ShareNoteWithUsersView(generics.CreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSharingInvitationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        note = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create NoteSharingInvitation instances for each user in the 'users' field
        user_ids = serializer.validated_data['users']
        users_to_be_invited = [User.objects.get(id=user_id) for user_id in user_ids]

        for user in users_to_be_invited:
            invitation = NoteSharingInvitation(note=note, recipient=user)
            invitation.save()

        return Response({"message": "Note share successfully"}, status=201)

