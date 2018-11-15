from wirfi_app.urls import dashboard_version_check, device, industry_location_type, password_reset_change, \
    preset_filter, user_register, user, ping_server

urlpatterns = dashboard_version_check.urlpatterns
urlpatterns += device.urlpatterns
urlpatterns += industry_location_type.urlpatterns
urlpatterns += password_reset_change.urlpatterns
urlpatterns += preset_filter.urlpatterns
urlpatterns += user_register.urlpatterns
urlpatterns += user.urlpatterns
urlpatterns += ping_server.urlpatterns
