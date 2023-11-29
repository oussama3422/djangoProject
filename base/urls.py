from django.urls import path
from . import views




urlpatterns = [
    path('login/', views.login_auth,name="login"),
    path('logout/', views.logout_user,name="logout"),
    path('register/', views.register_user,name="register"),
    
    path('', views.home,name="home"),
    path('room/<str:pk>', views.room,name="room"),
    
    # profile url
    path('user-profile/<str:pk>', views.user_profile,name="user-profile"),
    
    path('create-room/', views.createRoom,name="create-room"),
    path('update-room/<str:pk>', views.updateRoom,name="update-room"),
    path('delete-room/<str:pk>', views.deleteRoom,name="delete-room"),
    
    path('delete-message/<str:pk>', views.deleteMessage,name="delete-message"),
    
    # update user url
    path('update-user/', views.update_user,name="update-user"),
]
