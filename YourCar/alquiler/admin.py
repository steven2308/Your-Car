from django.contrib import admin
from YourCar.alquiler.models import Vehiculo,ClienteAlquiler,Reserva,Mantenimiento,Voucher,Contrato,ConductorAutorizado,DatosAlquiler,Danyo,Factura,BaseEncuesta,BasePregunta,EncuestaResuelta,PreguntaResuelta

#class AdminMateria(admin.ModelAdmin):
#	list_filter = ('nombre',)
#	ordering = ('-nombre',)
#	search_fields = ('nombre', 'tematica', 'semestre',)

admin.site.register(Vehiculo)
admin.site.register(ClienteAlquiler)
admin.site.register(Reserva)
admin.site.register(Mantenimiento)
admin.site.register(Voucher)
admin.site.register(Contrato)
admin.site.register(ConductorAutorizado)
admin.site.register(DatosAlquiler)
admin.site.register(Danyo)
admin.site.register(Factura)
admin.site.register(BaseEncuesta)
admin.site.register(BasePregunta)
admin.site.register(EncuestaResuelta)
admin.site.register(PreguntaResuelta)