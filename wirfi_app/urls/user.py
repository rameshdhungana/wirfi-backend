from django.urls import path
from wirfi_app.views import BillingView, BillingDetailView, delete_billing_card, \
    BusinessView, BusinessDetailView, UserDetailView, profile_images_view, \
    Login, logout, get_logged_in_user, AdminActivityLogListView, UserListCreateView


urlpatterns = [
    # billing
    path('billing/', BillingView.as_view()),
    path('billing/<int:id>/', BillingDetailView.as_view()),
    path('delete-billing-card/', delete_billing_card, ),

    # business
    path('business/', BusinessView.as_view()),
    path('business/<int:id>/', BusinessDetailView.as_view()),

    # user
    path('user/<int:id>/', UserDetailView.as_view(), name="user-detail"),
    path('user/<int:id>/image/', profile_images_view, name="user-image"),

    # login/logout
    path('login/', Login.as_view(), name='user_login'),
    path('logout/', logout, name='user_logout'),

    # logged in user
    path('me/', get_logged_in_user, name="me"),

    # admin user list-create
    path('users/', UserListCreateView.as_view(), name="user-list"),

    path('activity-log/', AdminActivityLogListView.as_view(), name="activity-log"),
]