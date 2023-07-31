# notes/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import (
    UserSerializer, TokenObtainPairSerializer, NoteSharingInvitationSerializer,
    NoteLikeSerializer
)
from rest_framework_simplejwt.views import TokenRefreshView
from .models import Note, NoteSharingInvitation, UserRelationship
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


class LikeNoteView(generics.CreateAPIView):
    queryset = Note.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NoteLikeSerializer

    def create(self, request, *args, **kwargs):
        try:
            note = Note.objects.get(pk=kwargs['note_id'])
        except Note.DoesNotExist:
            return Response({"error": "Note does not exist."}, status=404)

        user = request.user
        if user in note.collaborators.all():
            return Response({"error": "Collaborators cannot like the note."}, status=400)

        if user in note.likes.all():
            return Response({"message": "You have already liked this note."}, status=400)

        note.likes.add(user)
        note.save()

        return Response({"message": "Note liked successfully."}, status=200)


class FollowUnfollowUserView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = UserRelationship.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        return None

    def get_serializer(self, *args, **kwargs):
        return None

    def create(self, request, *args, **kwargs):
        following_user_id = kwargs.get('user_id')
        try:
            following_user = User.objects.get(pk=following_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User to follow does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        follower_user = request.user

        if follower_user == following_user:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if UserRelationship.objects.filter(
            follower=follower_user,
            following=following_user
        ).exists():
            return Response(
                {"error": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        relationship = UserRelationship(follower=follower_user, following=following_user)
        relationship.save()

        return Response({"message": "You are now following this user."}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        following_user_id = kwargs.get('user_id')
        try:
            following_user = User.objects.get(pk=following_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User to unfollow does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        follower_user = request.user

        if UserRelationship.objects.filter(
            follower=follower_user,
            following=following_user
        ).exists():
            relationship = UserRelationship.objects.get(
                follower=follower_user,
                following=following_user
            )
            relationship.delete()
            return Response(
                {"message": "You have unfollowed this user."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowersFollowingListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        relation_type = self.kwargs['relation_type']
        request_user = self.request.user

        if relation_type == 'followers':
            # Get the list of users who are following the request_user
            return User.objects.filter(following__following=request_user)
        elif relation_type == 'following':
            # Get the list of users whom the request_user is following
            return User.objects.filter(followers__follower=request_user)

    def list(self, request, *args, **kwargs):
        relation_type = self.kwargs['relation_type']

        if relation_type not in ('followers', 'following'):
            return Response({"error": "Invalid relation type."}, status=400)

        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

