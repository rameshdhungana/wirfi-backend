from wirfi_app.views.add_device_status import DeviceStatusView
from wirfi_app.views.admin_activity_log import AdminActivityLogListView
from wirfi_app.views.admin_createlist_users import AdminListCreateUserView
from wirfi_app.views.billing import BillingDetailView, BillingView, delete_billing_card
from wirfi_app.views.business import BusinessView  # , BusinessDetailView
from wirfi_app.views.caching import add_or_get_cached_device_list, update_cached_device_list
from wirfi_app.views.check_version import CheckVersion
from wirfi_app.views.dashboard import dashboard_view
from wirfi_app.views.device import DeviceView, DeviceDetailView, device_images_view
from wirfi_app.views.device_camera import DeviceCameraDetailView, DeviceCameraView, stream
from wirfi_app.views.device_network import DeviceNetworkDetailView, DeviceNetworkView
from wirfi_app.views.device_notification import AllNotificationView, UpdateNotificationView  # , DeviceNotificationView
from wirfi_app.views.device_settings import DeviceSleepView, device_priority_view, mute_device_view
from wirfi_app.views.industry_type import IndustryTypeDetailView, IndustryTypeListView
from wirfi_app.views.location_type import LocationTypeDetailView, LocationTypeListView
from wirfi_app.views.login_logout import Login, get_logged_in_user, logout
from wirfi_app.views.password_change import ChangePasswordView
from wirfi_app.views.password_reset import ResetPasswordView, ResetPasswordConfirmView, \
    ResetPasswordConfirmMobileView, validate_reset_password
from wirfi_app.views.preset_filter import PresetFilterDeleteView, PresetFilterView
from wirfi_app.views.register_user import RegisterUserView, VerifyEmailRegisterView
from wirfi_app.views.user import UserDetailView, profile_images_view, toggle_push_notifications
from wirfi_app.views.ping_server import ping_server_from_wirfi_device
from wirfi_app.views.signal_receivers import queue_device_create_task, queue_device_network_task
from wirfi_app.views.impersonate import impersonate_user, stop_impersonation
