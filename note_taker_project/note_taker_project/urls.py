"""note_taker_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from notes.views import (
    UserRegistrationView, TokenObtainPairView, TokenRefreshViewCustom,
    NoteListView, NoteDetailView, NoteSearchView, ShareNoteWithUsersView,
    LikeNoteView
)
from rest_framework.documentation import include_docs_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='Notes API', permission_classes=[]), name='docs'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
    path('api/register/', UserRegistrationView.as_view(), name='user_registration'),
    path('api/notes/', NoteListView.as_view(), name='note-list'),
    path('api/notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
    path('api/search/', NoteSearchView.as_view(), name='note_search'),
    path('api/notes/<int:pk>/share/', ShareNoteWithUsersView.as_view(), name='share_note_with_users'),
    path('note/<int:note_id>/like/', LikeNoteView.as_view()),
]