# encoding: utf-8
"""
Created by Keith Fahlgren on Wed Nov 21 06:14:36 PST 2012
Copyright (c) 2012 Keith Fahlgren. All rights reserved.
"""

from django.conf.urls import patterns, url, include
from django.contrib.auth.views import logout
from django.views.generic import TemplateView


urlpatterns = patterns('gauth.views',
    url(r'^login-error/$', TemplateView.as_view(template_name="login-error.html")),
)

urlpatterns += patterns('', 
    url(r'^logout/$', logout, {'next_page': '/'}, name='gauth_logout'),
    url(r'^$', TemplateView.as_view(template_name="login.html")),
)
