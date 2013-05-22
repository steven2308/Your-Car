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
    url(r'^vehiculos/(pag/(?P<pagina>\d{1,2})/)?$', 'verVehiculosControl', name='vistaVehiculos'),
    url(r'^cotizar/$', 'cotizarControl', name='vistaCotizar'),
    #Links del administrador:
    url(r'^vehiculos/agregar/$', 'agregarVehiculoControl', name='vistaAgregarVehiculos'),
    url(r'^vehiculos/detalles/(?P<placa>([A-Z]|[a-z]){3}[0-9]{3})/$', 'detallesVehiculoControl', name='vistadetallesVehiculo'),
    url(r'^vehiculos/modificar/$', 'modificarVehiculoControl', name='vistamodificarVehiculo'),
    url(r'^vehiculos/eliminar/$', 'eliminarVehiculoControl', name='vistaeliminarVehiculo'),
    url(r'^estadisticas/$', 'estadisticasControl', name='vistaEstadisticas'),
    url(r'^alertas/$', 'alertasControl', name='vistaAlertas'),
    url(r'^voucher/(pag/(?P<pagina>\d{1,5})/)?$', 'voucherControl', name='vistaVoucher'),
    url(r'^voucher/agregar/$', 'agregarVoucherControl', name='vistaAgregarVoucher'),
    url(r'^voucher/eliminar/$', 'eliminarVoucherControl', name='vistaEliminarVoucher'),
    url(r'^reservas/eliminar/$', 'eliminarReservaControl', name='vistaEliminarReservas'),
    url(r'^vehiculos/historialMantenimiento/(pag/(?P<pagina>\d{1,5})/)?$', 'historialMantenimientoControl', name='vistaHistorialMantenimiento'),
    url(r'^vehiculos/historialMantenimiento/agregar/$', 'agregarHistorialMantenimientoControl', name='vistaAgregarHistorialMantenimiento'),
    url(r'^vehiculos/historialMantenimiento/eliminar/$', 'eliminarHistorialMantenimientoControl', name='vistaEliminarHistorialMantenimiento'),
    url(r'^parametrizar/$', 'parametrizarControl', name='vistaParametrizar'),
    url(r'^contratos/(pag/(?P<pagina>\d{1,5})/)?$', 'contratosControl', name='vistaContrato'),
    url(r'^contratos/detalles/(?P<idContrato>[0-9]{1,9})/$$', 'detallesContratoControl', name='vistaDetallesContrato'),
    url(r'^contratos/agregar/$', 'agregarContratosControl', name='vistaAgregarContrato'),
    url(r'^contratos/agregarConductor/$', 'agregarConductorControl', name='vistaAgregarConductor'),
    url(r'^alquiler/(pag/(?P<pagina>\d{1,5})/)?$', 'alquileresControl', name='vistaAlquileres'),
    url(r'^alquiler/detalles/(?P<idDatosAlquiler>[0-9]{1,9})/$$', 'detallesDatosAlquilerControl', name='vistaDatosAlquiler'),
    url(r'^alquiler/agregar/$', 'agregarDatosAlquilerControl', name='vistaAgregarDatosAlquiler'),
    url(r'^alquiler/cierre/$', 'cierreDatosAlquilerControl', name='vistaCierreDatosAlquiler'),
    url(r'^facturas/(pag/(?P<pagina>\d{1,5})/)?$', 'facturasControl', name='vistaFactura'),
    url(r'^facturas/detalles/(?P<numFactura>[0-9]{1,9})/$$', 'detallesFacturaControl', name='vistaDetallesFactura'),
    url(r'^facturas/agregar/$', 'agregarFacturaControl', name='vistaAgregarFactura'),
    url(r'^facturas/agregarCobro/$', 'agregarCobroControl', name='vistaAgregarCobro'),
    #Links para usuarios conectados:
    url(r'^reservas/(pag/(?P<pagina>\d{1,5})/)?$', 'verReservasControl', name='vistaReservas'),
    url(r'^reservas/agregar/$', 'agregarReservaControl', name='vistaAgregarReservas'),
    url(r'^reservas/detalles/(?P<idReserva>\d{1,9})/$', 'detallesReservaControl', name='vistaDetallesReservas'),
    url(r'^reservas/modificar/$', 'modificarReservaControl', name='vistaModificarReservas'),
    url(r'^logout/$', 'logoutControl', name='vistaLogout'),
    url(r'^404/$', 'notFoundControl', name='vistaNotFound'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )