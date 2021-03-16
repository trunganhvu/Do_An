from django.urls import path
from . import views
from . import adminviews
from .viewapi import showviewlearningoutcomeview

urlpatterns = [
    # path('login/', adminviews.login_page, name='login'),
    path('login/', adminviews.user_login, name='login'),
    path('logout/', adminviews.user_logout, name='logout'),

    # path('changepassword/', views.changepassword_page, name='changepassword'),

    # path('viewlearningoutcome/', showviewlearningoutcomeview.viewlearningoutcome, name='viewlearningoutcome'),

    # path('suggestioncourse/', views.suggestioncourse_page, name='suggestioncourse'),
    # path('scoreforecast/', views.scoreforecast_page, name='scoreforecast'),
    # path('statistical/', views.statistical_page, name='statistical'),
    # path('statisticals/', views.statistical_page, name = 'statistical1'),
    # path('process_data/<str:save>/<str:course>', views.get_distribute),
    # path('transcripts/<str:unit>/<str:gen>/<str:group>/<str:sem>', views.transcript),
    # path('transcript_file_process', views.transcript_file_process),
]