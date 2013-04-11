from django.db import models

class Vehiculo(models.Model):
	placa = models.CharField(max_length=6,primary_key=True)
	marca = models.CharField(max_length=15) 
	referencia = models.CharField(max_length=15) 
	gama = models.CharField(max_length=15)
	descripcionBasica = models.CharField(max_length=100,blank=True)
	tipoDeFrenos = models.CharField(max_length=15) 
	numDePasajeros = models.IntegerField()
	cilindraje = models.IntegerField()
	color = models.CharField(max_length=15)
	cajaDeCambios = models.CharField(max_length=15) #poner opciones de a,m,t
	airbags = models.IntegerField()
	tipoDeDireccion = models.CharField(max_length=15) #mecanica, hidraulica, electronica
	traccion = models.CharField(max_length=15)
	modelo = models.IntegerField()
	valorGarantia = models.IntegerField()
	estado = models.CharField(max_length=15) #Disponible, reservado, rentado, en mantenimiento
	kilometraje = models.IntegerField()
	limiteKilometraje = models.IntegerField()
	tarifa = models.IntegerField()
	fechaVencSOAT = models.DateField()
	fechaVencSeguroTodoRiesgo = models.DateField()
	fechaVencRevisionTecMec = models.DateField()
	fechaVencCambioAceite = models.DateField()
	def __unicode__(self):
		return self.marca+" "+self.referencia+" Placa: "+self.placa

# Extender de User 
class ClienteAlquiler(models.Model):
	nombres = models.CharField(max_length=20)
	apellidos = models.CharField(max_length=20)
	#contrasena
	tipoPersona = models.CharField(max_length=10) #natural, legal
	tipoDocumento  = models.CharField(max_length=10) #que tipos hay?
	numDocumento = models.IntegerField(primary_key=True)
	correo = models.EmailField()
	fechaNacimiento = models.DateField()
	telFijo = models.CharField(max_length=10)
	telCelular = models.CharField(max_length=10)
	genero = models.CharField(max_length=1)
	paisResidencia = models.CharField(max_length=10)
	ciudadResidencia = models.CharField(max_length=10)
	dirResidencia = models.CharField(max_length=30)
	nombrePersonaContacto = models.CharField(max_length=20)
	telContacto = models.IntegerField()
	direccionContacto = models.CharField(max_length=30)	
	def __unicode__(self):
		return self.nombres+" "+self.apellidos
	class Meta:
		verbose_name_plural=u'Clientes de Alquiler'

class Reserva(models.Model):
	idReserva = models.AutoField(primary_key=True)
	idVehiculo = models.ForeignKey(Vehiculo)
	idCliente = models.ForeignKey(ClienteAlquiler)
	fechaInicio = models.DateTimeField()
	fechaFin = models.DateTimeField()
	lugar = models.CharField(max_length=15)
	pagada = models.BooleanField(default=False)
	datosDePago = models.CharField(max_length=200,blank=True)
	def __unicode__(self):
		return "Reserva de %s a %s" %(unicode(self.idCliente),unicode(self.idVehiculo))

class Mantenimiento(models.Model):
	idMantenimiento = models.AutoField(primary_key=True)
	idVechiulo = models.ForeignKey(Vehiculo)
	fecha = models.DateField()
	descripcion = models.CharField(max_length=200)
	costo = models.IntegerField()
	tipo = models.CharField(max_length=15) #correctivo o preventivo
	def __unicode__(self):
		return "Mantenimiento %s de %s" %(self.tipo,unicode(self.idVehiculo))

class Voucher(models.Model):
	codigoAutorizacion = models.CharField(max_length=15,primary_key=True)
	idCliente = models.ForeignKey(ClienteAlquiler)
	montoVoucher = models.IntegerField()
	numTarjetaCredito = models.CharField(max_length=15)
	fechaVencTarjeta = models.DateField()
	codigoVerifTarjeta = models.CharField(max_length=15)
	nombreBanco = models.CharField(max_length=15)
	def __unicode__(self):
		return "Voucher de %s codigo: %s" %(unicode(self.idCliente),self.codigoAutorizacion)

class Contrato(models.Model):
	idContrato = models.AutoField(primary_key=True)
	idVehiculo = models.ForeignKey(Vehiculo)	
	idVoucher = models.ForeignKey(Voucher)
	fecha = models.DateTimeField()
	def __unicode__(self):
		return "Contrato de %s por %s" %(unicode(self.idCliente),unicode(self.idVehiculo))

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

class InventarioVehiculo(models.Model):
	idInventarioVehiculo = models.AutoField(primary_key=True)

class DatosAlquiler(models.Model):
	idDatosAlquiler = models.AutoField(primary_key=True)
	idContrato = models.ForeignKey(Contrato)
	idReserva = models.ForeignKey(Reserva) #puede ser nulo
	idInventario = models.ForeignKey(InventarioVehiculo)
	#estado (abierto, cerrado)
	tarifaEstablecida = models.IntegerField()
	tarifaAplicada = models.IntegerField()
	fechaAlquiler = models.DateTimeField()
	fechaDevolucion = models.DateTimeField()
	totalDias = models.IntegerField()
	kmInicial = models.IntegerField()
	kmFinal = models.IntegerField()
	valorAlquiler = models.IntegerField()
	metodoPago = models.CharField(max_length=10)
	class Meta:
		verbose_name_plural=u'Datos Alquiler'

class Factura(models.Model):
	numFactura = models.AutoField(primary_key=True)
	idDatatosAlquiler = models.ForeignKey(DatosAlquiler)
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
	