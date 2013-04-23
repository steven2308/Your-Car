from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('YourCar.alquiler.views',		
    url(r'^admin/', include(admin.site.urls)),
    #Links publicos:
    url(r'^$', 'inicioControl', name='vistaPrincipal'),
    url(r'^registro/$', 'registroControl', name='vistaRegistro'),
    url(r'^login/$', 'loginControl', name='vistaLogin'),    
    url(r'^vehiculos/$', 'verVehiculosControl', name='vistaVehiculos'),
    url(r'^cotizar/$', 'cotizarControl', name='vistaCotizar'),
    #Links del administrador:
    url(r'^vehiculos/agregar/$', 'agregarVehiculoControl', name='vistaAgregarVehiculos'),
    url(r'^vehiculos/detalles/$', 'detallesVehiculoControl', name='vistadetallesVehiculo'),
    url(r'^vehiculos/modificar/$', 'modificarVehiculoControl', name='vistamodificarVehiculo'),
    url(r'^vehiculos/eliminar/$', 'eliminarVehiculoControl', name='vistaeliminarVehiculo'),
    url(r'^estadisticas/$', 'estadisticasControl', name='vistaEstadisticas'),    
    url(r'^alertas/$', 'alertasControl', name='vistaAlertas'),
    url(r'^voucher/$', 'voucherControl', name='vistaVoucher'),
    #Links para usuarios conectados:  
    url(r'^reservas/$', 'reservasControl', name='vistaReservas'),
    url(r'^reservas/agregar/$', 'agregarReservaControl', name='vistaReservas'),   
    url(r'^logout/$', 'logoutControl', name='vistaLogout'),
    url(r'^404/$', 'notFoundControl', name='vistaNotFound'),
    url(r'^vehiculos/historialMantenimiento/$', 'historialMantenimientoControl', name='vistaHistorialMantenimiento'),
    url(r'^vehiculos/historialMantenimiento/agregar/$', 'agregarHistorialMantenimientoControl', name='vistaAgregarHistorialMantenimiento'),
    url(r'^vehiculos/historialMantenimiento/eliminar/$', 'eliminarHistorialMantenimientoControl', name='vistaEliminarHistorialMantenimiento'),

)
	
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )