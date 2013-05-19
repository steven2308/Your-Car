from django.db import models
from django.contrib.auth.models import User

class Vehiculo(models.Model):
	def url(self,filename):
		return "fotos/carros/%s/%s/%s/%s"%(self.marca, self.referencia, self.placa , filename)
	print url
	placa = models.CharField(max_length=6,primary_key=True)
	marca = models.CharField(max_length=15)
	referencia = models.CharField(max_length=15)
	gama = models.CharField(max_length=15)
	descripcionBasica = models.CharField(max_length=100)
	tipoDeFrenos = models.CharField(max_length=15, blank=True)
	numDePasajeros = models.IntegerField()
	cilindraje = models.IntegerField()
	color = models.CharField(max_length=15)
	cajaDeCambios = models.CharField(max_length=15) #poner opciones de a,m,t
	airbags = models.IntegerField(blank=True, null=True)
	tipoDeDireccion = models.CharField(max_length=15) #mecanica, hidraulica, electronica
	tipoDeTraccion = models.CharField(max_length=15, blank=True)
	modelo = models.IntegerField(blank=True, null=True)
	valorGarantia = models.IntegerField(blank=True, null=True)
	estado = models.CharField(max_length=15) #Disponible, reservado, rentado, en mantenimiento
	kilometraje = models.IntegerField(blank=True, null=True)
	limiteKilometraje = models.IntegerField()
	tarifa = models.IntegerField()
	foto = models.FileField(upload_to=url)
	fechaVencSOAT = models.DateField()
	fechaVencSeguroTodoRiesgo = models.DateField()
	fechaVencRevisionTecMec = models.DateField()
	fechaVencCambioAceite = models.DateField()
	def __unicode__(self):
		return self.marca+" "+self.referencia+" Placa: "+self.placa

# Extender de User
class ClienteAlquiler(models.Model):
	user = models.ForeignKey(User, unique=True)
	fechaNacimiento = models.DateField()
	telFijo = models.CharField(max_length=12)
	telCelular = models.CharField(max_length=12)
	genero = models.CharField(max_length=20,blank=True)
	tipoPersona = models.CharField(max_length=20)
	tipoDocumento  = models.CharField(max_length=20)
	numDocumento = models.CharField(max_length=20,primary_key=True)
	paisResidencia = models.CharField(max_length=20)
	ciudadResidencia = models.CharField(max_length=20)
	dirResidencia = models.CharField(max_length=40)
	nombrePersonaContacto = models.CharField(max_length=20,blank=True)
	telContacto = models.CharField(max_length=12,blank=True)
	direccionContacto = models.CharField(max_length=40,blank=True)
	def __unicode__(self):
		return self.user.first_name+" "+self.user.last_name+". Id: "+self.numDocumento
	class Meta:
		verbose_name_plural=u'Clientes de Alquiler'

class Reserva(models.Model):
	def url(self,filename):
		return "fotos/pagos/%s"%(self.idReserva)
	idReserva = models.AutoField(primary_key=True)
	idVehiculo = models.ForeignKey(Vehiculo)
	idCliente = models.ForeignKey(ClienteAlquiler)
	fechaInicio = models.DateTimeField()
	fechaFin = models.DateTimeField()
	lugarRecogida = models.CharField(max_length=15)
	lugarEntrega = models.CharField(max_length=15)
	pagada = models.BooleanField(default=False)
	datosDePago = models.CharField(max_length=200)
	fotoPago = models.FileField(upload_to=url)
	def __unicode__(self):
		return "Reserva de %s a %s" %(unicode(self.idCliente),unicode(self.idVehiculo))

class Mantenimiento(models.Model):
	idVehiculo = models.ForeignKey(Vehiculo)
	fecha = models.DateField()
	descripcion = models.CharField(max_length=200, blank =True)
	costo = models.IntegerField()
	tipo = models.CharField(max_length=15) #correctivo o preventivo
	def __unicode__(self):
		return "Mantenimiento %s de %s" %(self.tipo,unicode(self.idVehiculo))

class Voucher(models.Model):
	codigoAutorizacion = models.CharField(max_length=15,primary_key=True)
	idCliente = models.ForeignKey(ClienteAlquiler)
	montoVoucher = models.IntegerField()
	numTarjetaCredito = models.CharField(max_length=18)
	fechaVencTarjeta = models.DateField()
	codigoVerifTarjeta = models.CharField(max_length=5)
	nombreBanco = models.CharField(max_length=20)
	def __unicode__(self):
		return "Voucher codigo: %s" %(self.codigoAutorizacion)

class Contrato(models.Model):
	idContrato = models.AutoField(primary_key=True)
	idVehiculo = models.ForeignKey(Vehiculo)
	idVoucher = models.ForeignKey(Voucher)
	fecha = models.DateField()
	def __unicode__(self):
		return "Contrato de %s Vehiculo:  %s" %((self.idVoucher),unicode(self.idVehiculo))

class ConductorAutorizado(models.Model):
	docIdentidad = models.IntegerField(primary_key=True)
	idContrato = models.ForeignKey(Contrato)
	nombres = models.CharField(max_length=20)
	apellidos = models.CharField(max_length=20)
	licencia  = models.CharField(max_length=20)
	fechaNacimiento = models.DateField()
	tipoSangre =  models.CharField(max_length=6)
	def __unicode__(self):
		return "Conductor autorizado %s %s" %(self.nombres,self.apellidos)
	class Meta:
		verbose_name_plural=u'Conductores Autorizados'

class DatosAlquiler(models.Model):
	idDatosAlquiler = models.AutoField(primary_key=True)
	idContrato = models.ForeignKey(Contrato)
	idReserva = models.ForeignKey(Reserva, null=True) #puede ser nulo
	metodoPago = models.CharField(max_length=15)
	tarifaEstablecida = models.IntegerField()
	tarifaAplicada = models.IntegerField()
	fechaAlquiler = models.DateTimeField()
	fechaDevolucion = models.DateTimeField()
	totalDias = models.IntegerField()
	kmInicial = models.IntegerField()
	kmFinal = models.IntegerField()
	valorAlquiler = models.IntegerField()
	class Meta:
		verbose_name_plural=u'Datos Alquiler'

class InventarioVehiculo(models.Model):
	idInventarioVehiculo = models.AutoField(primary_key=True)
	idDatosAlquiler = models.ForeignKey(DatosAlquiler)
	cierre = models.BooleanField(default=False)

class Factura(models.Model):
	numFactura = models.AutoField(primary_key=True)
	idDatosAlquiler = models.ForeignKey(DatosAlquiler)
	fecha = models.DateField()
	referenciaServicio = models.CharField(max_length=20)
	#Tabla de servicios? Yo creo que si
	descripcionServicio = models.CharField(max_length=40)
	valorServicio = models.IntegerField()
	horasAdicionales = models.IntegerField()
	valorUnitario = models.IntegerField()
	galonesGasolina = models.IntegerField()
	costoTotalgasolina = models.IntegerField()
	subtotal = models.IntegerField()
	iva = models.IntegerField()
	total = models.IntegerField()

class Danyo(models.Model):
	idFactura = models.ForeignKey(Factura)
	desripcion = models.CharField(max_length=200)
	costo = models.IntegerField()

class BaseEncuesta(models.Model):
	idBaseEncuesta = models.AutoField(primary_key=True)
	nombreEncuesta = models.CharField(max_length=20)

class BasePregunta(models.Model):
	idBasePregunta = models.AutoField(primary_key=True)
	idBaseEncuesta = models.ForeignKey(BaseEncuesta)
	numPregunta = models.IntegerField()
	tipo = models.CharField(max_length=10) #Si-No o Rango

class EncuestaResuelta(models.Model):
	idEncuestaResuelta = models.AutoField(primary_key=True)
	idBaseEncuesta = models.ForeignKey(BaseEncuesta)
	fecha = models.DateField()
	observaciones = models.TextField(blank=True)

class PreguntaResuelta(models.Model):
	idPreguntaResuelta = models.AutoField(primary_key=True)
	idEncuestaResuelta = models.ForeignKey(EncuestaResuelta)
	rptaBool = models.BooleanField()
	rptaRango = models.IntegerField() #Rango 1 a 5
