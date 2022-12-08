from django.urls import path
from .views import home, signup, signin, activate, add_blog, blog_detail, see_blog, blog_delete, blog_update, logout_view,ForgetPassword,ChangePassword

urlpatterns = [
    path('', home, name="home"),
    path('signup',signup, name='signup'),
    path('signin',signin, name='signin'),
    path('forget-password/' , ForgetPassword , name="forget_password"),
    path('activate/<token>/<uidb64>',activate, name='activate'),
    path('change-password/<token>/<username>' , ChangePassword , name="change_password"),
    path('add-blog/', add_blog, name="add_blog"),
    path('blog-detail/<slug>', blog_detail, name="blog_detail"),
    path('see-blog/', see_blog, name="see_blog"),
    path('blog-delete/<id>', blog_delete, name="blog_delete"),
    path('blog-update/<slug>', blog_update, name="blog_update"),
    path('logout-view/', logout_view, name="logout_view"),
] 