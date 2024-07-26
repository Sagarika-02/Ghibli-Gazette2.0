from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from . import views 

urlpatterns = [
    # Your existing URL patterns here
    path('',views.home,name="home"),
    path('signup/',views.signup,name="signup"),
    path('user_login/',views.user_login,name="user_login"),
    path('logout/',views.logout,name="logout"),
    path('profile/',views.profile,name="profile"),
    path('createprofile/',views.createprofile,name="createprofile"),
    path('delete_profile/',views.delete_profile,name="delete_profile"),
    path('createpost/',views.createpost,name="createpost"),
    path('allposts/',views.allposts,name="allposts"),
    path('editpost/<int:pk>/',views.editpost,name="editpost"),
    path('deletepost/<int:pk>/',views.deletepost,name="deletepost"),
    path('mypost/',views.mypost,name="mypost"),
    path('readmore/<int:pk>/',views.readmore,name="readmore"),
    path('search_results/',views.search_results,name="search_results"),
    
    #path('add_comment/<int:post_id>/',views.add_comment,name="add_comment"),
    #Wpath('add_reply/<comment_id>/',views.add_reply,name="add_reply"),
   

]
