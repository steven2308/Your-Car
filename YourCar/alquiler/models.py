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

class ClientePotencial(models.Model):
	email=models.EmailField()
	def __unicode__(self):
		return "Cliente Potencial "+self.email

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
	franquicia = models.CharField(max_length=20)
	def __unicode__(self):
		return "Voucher codigo: %s" %(self.codigoAutorizacion)

class Contrato(models.Model):
	idContrato = models.AutoField(primary_key=True)
	idVehiculo = models.ForeignKey(Vehiculo)
	idVoucher = models.ForeignKey(Voucher)
	fechaInicio = models.DateTimeField()
	fechaFin = models.DateTimeField()
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
	lugarRecogida = models.CharField(max_length=15)
	lugarEntrega = models.CharField(max_length=15)
	cierre = models.BooleanField(default=False)
	#valorAlquiler = models.IntegerField()
	def __unicode__(self):
		return "Datos de alquiler id: %s " %(self.idDatosAlquiler)
	class Meta:
		verbose_name_plural=u'Datos Alquiler'

class ChecklistVehiculo(models.Model):
	idChecklistVehiculo = models.AutoField(primary_key=True)
	idDatosAlquiler = models.ForeignKey(DatosAlquiler)
	cierre = models.BooleanField(default=False)
	documentosDelAuto = models.IntegerField(max_length=1) #0 True, 1 False
	"""radio = models.IntegerField(max_length=1)
	tapetes = models.IntegerField(max_length=1)
	llantaDeRepuesto = models.IntegerField(max_length=1)
	gato = models.IntegerField(max_length=1)
	cruceta = models.IntegerField(max_length=1)
	nivelAceiteDelMotorFrenos = models.IntegerField(max_length=1)
	nivelRefrigerante = models.IntegerField(max_length=1)
	latoneriaYPintura = models.IntegerField(max_length=1)
	tapizado = models.IntegerField(max_length=1)
	cinturonesDeSeguridad = models.IntegerField(max_length=1)
	controlesInternos = models.IntegerField(max_length=1)
	instrumentosDelPanel = models.IntegerField(max_length=1)
	pito = models.IntegerField(max_length=1)
	relojConHoraCorrecta = models.IntegerField(max_length=1)
	limpiabrisas = models.IntegerField(max_length=1)
	liquidoDeLimpiabrisas = models.IntegerField(max_length=1)
	seguroCentral = models.IntegerField(max_length=1)
	elevaVidrios = models.IntegerField(max_length=1)
	aireAcondicionado = models.IntegerField(max_length=1)
	cojineria = models.IntegerField(max_length=1)
	lucesInternas = models.IntegerField(max_length=1)
	lucesMediasDelanterasYTraseras = models.IntegerField(max_length=1)
	lucesAltasYBajas = models.IntegerField(max_length=1)
	direccionalesDelantesYTraseras = models.IntegerField(max_length=1)
	luzDeFreno = models.IntegerField(max_length=1)
	luzDeReversa = models.IntegerField(max_length=1)
	antenaDeRadio = models.IntegerField(max_length=1)
	rines = models.IntegerField(max_length=1)
	farolasYStops = models.IntegerField(max_length=1)
	exploradoras = models.IntegerField(max_length=1)
	retrovisores = models.IntegerField(max_length=1)
	cristalesVidrios = models.IntegerField(max_length=1)
	chapas = models.IntegerField(max_length=1)
	llaves = models.IntegerField(max_length=1)
	kitCarretera = models.IntegerField(max_length=1)"""
	def __unicode__(self):
		return "Checklist con id: %s de %s" %((self.idChecklistVehiculo),unicode(self.idDatosAlquiler))

class Factura(models.Model):
	numFactura = models.AutoField(primary_key=True)
	idDatosAlquiler = models.ForeignKey(DatosAlquiler)
	fecha = models.DateField()
	tarifa = models.IntegerField()
	limiteKilometraje = models.IntegerField()
	galonesGasolina = models.IntegerField()
	costoGalon = models.IntegerField()
	costoRecogida = models.IntegerField()
	costoEntrega = models.IntegerField()
	costoLavada = models.IntegerField()
	porcentajeIVA = models.IntegerField()
	# subtotal = models.IntegerField()
	# iva = models.IntegerField()
	# total = models.IntegerField()
	def __unicode__(self):
		return "Factura num: %s " %(self.numFactura)

class CobroAdicional(models.Model):
	idCobroAdicional = models.AutoField(primary_key=True)
	numFactura = models.ForeignKey(Factura)
	idServicio = models.IntegerField()
	servicio = models.CharField(max_length=20)
	descripcion = models.CharField(max_length=200)
	costoUnidad = models.IntegerField()
	cantidad = models.IntegerField()
	total = models.IntegerField()
	def __unicode__(self):
		return "Cobro Adicional num: %s %s " %(self.idCobroAdicional,self.numFactura)
	class Meta:
		verbose_name_plural=u'Cobros Adicionales'

class Proveedor(models.Model):
	idProveedor = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=20)
	descripcion = models.CharField(max_length=200)
	nombrePersonaContacto = models.CharField(max_length=20,blank=True)
	telCelular = models.CharField(max_length=20,blank=True)
	telFijo = models.CharField(max_length=20)
	calificacion = models.IntegerField()
	def __unicode__(self):
		return "Proveedor %s" %(self.nombre)
	class Meta:
		verbose_name_plural=u'Proveedores'

class Servicio(models.Model):
	idProveedor = models.ForeignKey(Proveedor)
	servicio = models.CharField(max_length=20)
	costo = models.IntegerField()
	def __unicode__(self):
		return "Servicio %s por %s" %(self.servicio, self.idProveedor)