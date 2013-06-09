from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from bambu.bootstrap.decorators import body_classes
from bambu.saas.views import ajax
from bambu.saas.views import *
from bambu.saas.models import Plan
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
	url(r'^plans/$', body_classes(plans, 'saas-plans'), name = 'plans'),
	url(r'^signup/$', body_classes(signup, 'saas-signup'), name = 'signup'),
	url(r'^signup/pay/$', body_classes(signup_pay, 'saas-signup', 'saas-signup-pay'),
		name = 'signup_pay'
	),
	url(r'^signup/complete/$', body_classes(verify_email, 'saas-verify'), name = 'signup_complete'),
	url(r'^upgrade/$', body_classes(upgrade, 'saas-upgrade'), name = 'upgrade'),
	url(r'^upgrade/pay/$', body_classes(upgrade_pay, 'saas-upgrade'), name = 'upgrade_pay'),
	url(r'^verify/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
		body_classes(verify_email, 'saas-verify'), name = 'verify_email'
	),
	url(r'^invite/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
		body_classes(invitation_accept, 'saas-verify'), name = 'invitation_accept'
	),
	url(r'^reset/$', body_classes(reset_password, 'saas-reset'), name = 'forgot_password'),
	url(r'^reset/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
		body_classes(reset_password, 'saas-reset', 'saas-reset-result'), name = 'reset_password'
	),
	url(r'^profile/$', body_classes(profile, 'profile'), name = 'profile'),
	url(r'^profile/edit/$', body_classes(profile_edit, 'profile', 'profile-edit'), name = 'profile_edit'),
	url(r'^profile/team/$', body_classes(profile_subusers, 'profile', 'profile-subusers'), name = 'profile_subusers'),
	url(r'^profile/team/invitations/$',
		body_classes(profile_subusers_invitations, 'profile', 'profile-subusers', 'profile-subusers-invitations'),
		name = 'profile_subusers_invitations'
	),
	url(r'^profile/team/(?P<username>[\w-]+)/delete/$',
		body_classes(profile_delete_subuser, 'profile', 'profile-subusers', 'delete-confirm'), name = 'profile_delete_subuser'
	),
	url(r'^profile/team/invitations/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/resend/$',
		profile_resend_invitation, name = 'profile_resend_invitation'
	),
	url(r'^profile/team/invitations/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/delete/$',
		profile_delete_invitation, name = 'profile_delete_invitation'
	),
	url(r'^profile/team/invite/$', profile_subusers_invite, name = 'profile_subusers_invnite'),
	url(r'^login/$', body_classes(login, 'login'),
		{
			'extra_context': {
				'matrix': Plan.objects.matrix
			}
		}, name = 'login'
	),
	url(r'^logout/$', logout, {'next_page': '/'}, name = 'logout'),
	url(r'^ajax/username-exists\.js$', ajax.username_exists, name = 'username_exists_ajax'),
	url(r'^ajax/email-exists\.js$', ajax.email_exists, name = 'email_exists_ajax')
)