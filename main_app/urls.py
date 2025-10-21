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
    path('shares/<int:share_id>/fare/<int:pk>/', views.FareDetail.as_view(), name='fare-detail'),
    path('share/<int:share_id>/fare/<int:pk>/fare-update', views.FareUpdate.as_view(), name='fare-update'),
    path('share/<int:share_id>/fare/<int:pk>/fare-delete', views.FareDelete.as_view(), name='fare-delete'),

    path('accounts/signup/', views.signup, name='signup'),


]
