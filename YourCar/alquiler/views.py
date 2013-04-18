# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo, ClienteAlquiler
from YourCar.alquiler.parametros import parametros
from django.contrib.auth.models import User
import re

#Verificar que fecha es fecha, que poner en contrasena 
 	
def inicioControl(request):
	conectado=False
	nombre=""
	misionInicio= parametros["misionInicio"]
	visionInicio= parametros["visionInicio"]
	quienesSomosInicio= parametros["quienesSomosInicio"]
	if request.user.is_authenticated():
		conectado=True
		nombre=request.user.username
	return render_to_response ('inicio.html',locals(), context_instance = RequestContext(request))

def registroControl(request):	
	if not request.user.is_authenticated():		
			#Cargo los datos parametrizables que debo pasar al template.
		generos=parametros["generos"]
		tipoDocumentos=parametros["tipoDocumentos"]
		tipoPersonas=parametros["tipoPersonas"]			
		if request.method == 'POST':			
			#Tomo el nombre de usuario y el email
			nombreUsuario=request.POST["nombreUsuario"]
			email=request.POST["email"]			
			#Tomo el resto de los datos
			fechaNacimiento = request.POST['fechaNacimiento']
			telFijo = request.POST['telFijo']			
			telCelular = request.POST['telCelular']
			genero = request.POST['genero']			
			tipoPersona = request.POST['tipoPersona']
			tipoDocumento = request.POST['tipoDocumento']		
			numDocumento = request.POST['numDocumento']
			#Inicializo datos opcionales			
			paisResidencia= request.POST['paisResidencia']
			ciudadResidencia= request.POST['ciudadResidencia']
			dirResidencia= request.POST['dirResidencia']
			nombrePersonaContacto=""
			telContacto="0"
			direccionContacto=""
			#Tomo los datos opcionales que el usuario haya ingresado			
			if request.POST['nombrePersonaContacto']: nombrePersonaContacto = request.POST['nombrePersonaContacto']
			if request.POST['telContacto']: telContacto = request.POST['telContacto']
			if request.POST['direccionContacto']: direccionContacto = request.POST['direccionContacto']

			#Valido errores			
			errorUser=(User.objects.filter(username=nombreUsuario) or  not re.match("^([a-zA-z0-9_]{8,20})$",nombreUsuario))
			errorContrasena= (request.POST["contrasena"]!=request.POST["contrasena2"])
			errorEmail= (User.objects.filter(email=email) or not re.match(r"^[A-Za-z0-9\._-]+@[A-Za-z0-9]+\.[a-zA-Z]+$", email))
			errorTels = (not re.match("^([0-9]{7,12})$",telFijo) or not re.match("^([0-9]{10,12})$",telCelular) or (len(telContacto)>1 and not re.match("^([0-9]{7,12})$",telContacto)))
			errorGenero= (genero not in (parametros["generos"]))
			errorTipoPersona= (tipoPersona not in (parametros["tipoPersonas"]))
			errorTipoDocumento= (tipoDocumento  not in (parametros["tipoDocumentos"]))						
			errorNumDocumento=  ((ClienteAlquiler.objects.filter(numDocumento=numDocumento)) or not re.match("^([a-zA-z0-9_-]{6,20})$",numDocumento))
			errorDatosResidencia= (not paisResidencia or not ciudadResidencia or not dirResidencia)
			errorCamposVacios = (len(nombreUsuario)==0 or len(request.POST["contrasena"])==0)

			if (errorUser or errorContrasena or errorEmail or errorGenero or errorTipoPersona or errorTipoDocumento or errorTels or errorNumDocumento or errorDatosResidencia or errorCamposVacios):
				return render_to_response('registro.html', locals(), context_instance = RequestContext(request))

			#Guardo el usuario			
			usuario = User.objects.create_user(username=nombreUsuario, email=email, password=request.POST["contrasena"])
			usuario.first_name = request.POST['nombre']
			usuario.last_name = request.POST['apellido']
			usuario.save()

			#Guardo el cliente de alquiler
			cliente = ClienteAlquiler(user = usuario, fechaNacimiento = fechaNacimiento, telFijo = telFijo,
				telCelular = telCelular, genero = genero, tipoPersona = tipoPersona, tipoDocumento = tipoDocumento,
				numDocumento = numDocumento, paisResidencia = paisResidencia, ciudadResidencia = ciudadResidencia,
				dirResidencia = dirResidencia, nombrePersonaContacto = nombrePersonaContacto, telContacto= telContacto,
				direccionContacto=direccionContacto)
			cliente.save()			
			return HttpResponseRedirect('/')
		else:			
			return render_to_response('registro.html', locals(), context_instance = RequestContext(request))
	else:
		conectado = True
		nombreUsuario = request.user.username
		return render_to_response('registro.html', locals(), context_instance = RequestContext(request))

def loginControl(request):
	try:
		username = request.POST['username']
		password = request.POST['password']		
		if '@' in username:			
			correo = username
			username = User.objects.get(email=correo).username				
		usuario = authenticate(username=username, password=password)
		if usuario is not None and usuario.is_active:
			login(request, usuario)
			usuario = request.user
			conectado= True
			if request.user.is_superuser:
				return HttpResponseRedirect('/admin')
			elif request.user.is_staff:
				return HttpResponseRedirect('/alertas')
			return HttpResponseRedirect('/vehiculos')			
	except:
		return HttpResponseRedirect('/')
	loginFailed = True
	return render_to_response('inicio.html', locals(), context_instance = RequestContext(request))

def vehiculosControl(request):
	#si request.user.is_staff
    #Redirect /opcionesVehiculosAdmin: AgregarVehiculo, Vehiculos 
    #si no
    #Redirect /opcionesVehiculosCliente: Vehiculos (opcion de enviar a cotizacion)
	vehiculos = Vehiculo.objects.all()	
	return render_to_response('inventarioVehiculos.html',locals(), context_instance = RequestContext(request))
		
def cotizarControl(request):
	#Logica de control
	return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))

def agregarVehiculoControl(request):
	if request.user.is_authenticated():
		if request.user.is_staff:
			#Cargo datos parametrizables
			cajasDeCambios=parametros["cajasDeCambios"]
			tipoDeDirecciones=parametros["tipoDeDirecciones"]
			estadosVehiculo=parametros["estadosVehiculo"]
			tiposTraccion=parametros["tiposTraccion"]
			if request.method == 'POST':
				#Cargo datos requeridos del auto
				placa = request.POST["placa"]
				marca = request.POST["marca"] 
				referencia = request.POST["referencia"]
				gama = request.POST["gama"]
				descripcionBasica = request.POST["descripcionBasica"]
				numDePasajeros = request.POST["numDePasajeros"]
				cilindraje = request.POST["cilindraje"]
				color = request.POST["color"]
				cajaDeCambios = request.POST["cajaDeCambios"] 
				limiteKilometraje = request.POST["limiteKilometraje"]
				tarifa = request.POST["tarifa"]
				estado = request.POST["estado"]
				fechaVencSOAT = request.POST["fechaVencSOAT"]
				fechaVencSeguroTodoRiesgo = request.POST["fechaVencSeguroTodoRiesgo"]
				fechaVencRevisionTecMec = request.POST["fechaVencRevisionTecMec"]
				fechaVencCambioAceite = request.POST["fechaVencCambioAceite"]
				#Datos Opcionales
				tipoDeFrenos = request.POST["tipoDeFrenos"]
				airbags = request.POST["airbags"]
				tipoDeDireccion = request.POST["tipoDeDireccion"]
				tipoDeTraccion = request.POST["tipoDeTraccion"]
				modelo = request.POST["modelo"]
				valorGarantia = request.POST["valorGarantia"]
				kilometraje = request.POST["kilometraje"]

				#Control de errores
				errorPlaca = (Vehiculo.objects.filter(placa=placa) or not re.match("^([A-Z0-9]{6})$",placa))
				errorNumDePasajeros = not re.match("^[0-9]{1,2}$",numDePasajeros)
				errorCajaDeCambios = (cajaDeCambios not in parametros["cajasDeCambios"])
				errorEstado = (estado not in parametros["estadosVehiculo"])
				errorTipoDeDireccion = (tipoDeDireccion not in parametros["tipoDeDirecciones"])
				errorTipoDeTraccion = (tipoDeTraccion not in parametros["tiposTraccion"])
				errorCamposVaciosVeh = (len(placa)==0 or len(marca)==0 or len(referencia)==0 or len(gama)==0 or len(descripcionBasica)==0 or len(numDePasajeros)==0 or len(cilindraje)==0 or len(color)==0 or len(limiteKilometraje)==0 or len(tarifa)==0 or len(fechaVencSOAT)==0 or len(fechaVencCambioAceite)==0 or len(fechaVencRevisionTecMec)==0 or len(fechaVencSeguroTodoRiesgo)==0)

				if (errorPlaca or errorNumDePasajeros or errorCajaDeCambios or errorEstado or errorTipoDeDireccion or errorTipoDeTraccion or errorCamposVacios):
					return render_to_response('agregarVehiculo.html', locals(), context_instance = RequestContext(request))

				vehiculo = Vehiculo(placa = placa, marca = marca, referencia = referencia, gama = gama, descripcionBasica = descripcionBasica, numDePasajeros = numDePasajeros, cilindraje = cilindraje, color = color, cajaDeCambios = cajaDeCambios, limiteKilometraje = limiteKilometraje, tarifa = tarifa, estado = estado, fechaVencSOAT = fechaVencSOAT, fechaVencSeguroTodoRiesgo = fechaVencSeguroTodoRiesgo, fechaVencRevisionTecMec = fechaVencRevisionTecMec, fechaVencCambioAceite = fechaVencCambioAceite, tipoDeFrenos = tipoDeFrenos, airbags = airbags, tipoDeDireccion = tipoDeDireccion, tipoDeTraccion = tipoDeTraccion, modelo = modelo, valorGarantia = valorGarantia, kilometraje = kilometraje)
				vehiculo.save()

				HttpResponseRedirect('inventarioVehiculos.html')
			else:
				return render_to_response('agregarVehiculo.html', locals(), context_instance = RequestContext(request))
			errorStaff=True
	noAutorizado=True
	return render_to_response('inicio.html',locals(), context_instance = RequestContext(request)) #no esta conectado

def estadisticasControl(request):
	#Logica de control
	return render_to_response('estadisticas.html',locals(), context_instance = RequestContext(request))

def alertasControl(request):
	if request.user.is_authenticated():
		if request.user.is_staff:
			# alertas = cargarAlertas()
			return render_to_response ('alertas.html',locals(),context_instance=RequestContext(request))
		else:
			onlyAdmin=True
	onlyLogged=True
	return render_to_response ('noAutorizado.html',locals(),context_instance=RequestContext(request))

def voucherControl(request):
	#Logica de control
	return render_to_response('voucher.html',locals(), context_instance = RequestContext(request))

def reservasControl(request):
	#Logica de control
	return render_to_response('reservas.html',locals(), context_instance = RequestContext(request))

def agregarReservaControl(request):
	#Logica de control
	return render_to_response('agregarReserva.html',locals(), context_instance = RequestContext(request))

# Controlador del Cierre de Sesion
def logoutControl(request):
    logout(request)
    return HttpResponseRedirect('/')