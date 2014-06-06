from django.conf.urls import patterns, url

from poa_deploy import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add_application_to_database', views.add_application_to_database, name='add_application_to_database'),
    url(r'^install_application', views.install_application, name='install_application'),
    url(r'^add_poa_installation', views.add_poa_installation, name='add_poa_installation')
)