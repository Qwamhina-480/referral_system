from django.urls import path
from .views import SignupView ,CheckPointsView, ReferralRedirectView, LeaderboardView, UserDashboardView, delete, admin_dashboard, leaderboard_html, user_dashboard, signup_html, login_html, logout_html, landing_html

urlpatterns = [ 
    path('referral/', SignupView.as_view(), name='submit-referral'),
    path('points/<str:referral_code>/', CheckPointsView.as_view(), name='check-points'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('dashboard/<str:referral_code>/', UserDashboardView.as_view()),
    path('ref/<str:referral_code>/', ReferralRedirectView.as_view(), name='referral-link'),
    path('leaderboard-page/', leaderboard_html, name='leaderboard-page'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('user-dashboard/<str:referral_code>/', user_dashboard, name='user-dashboard'),
    path('login/', login_html, name='login'),
    path('signup/', signup_html, name='signup'),
    path('logout/', logout_html, name='logout'),
    path('', landing_html, name="landiing-page"),
    path('delete/', delete, name='delete'),
    


    


    

]
