from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('YourCar.alquiler.views',
	url(r'^$', 'inicioControl', name='vistaPrincipal'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^registro/$', 'registroControl', name='vistaRegistro'),
    url(r'^login/$', 'loginControl', name='vistaLogin'),
    url(r'^portal/$', 'portalControl', name='vistaPortal'),    
    url(r'^vehiculos/$', 'vehiculosPrueba', name='vistaVehiculos'),    
    url(r'^logout/$', 'logoutControl', name='vistalogout'),
)
	