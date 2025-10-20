from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),

    path('shares/', views.ShareIndex.as_view(), name='share-index'),
    path('shares/<int:pk>/', views.ShareDetail.as_view(), name='share-detail'),
    path('shares/create/', views.ShareCreate.as_view(), name='share-create'),
    path('shares/<int:pk>/update/', views.ShareUpdate.as_view(), name='share-update'),
    path('shares/<int:pk>/delete/', views.ShareDelete.as_view(), name='share-delete'),

    path('shares/<int:share_id>/fare-create/', views.FareCreate.as_view(), name='fare-create'),

    path('accounts/signup/', views.signup, name='signup'),


]
