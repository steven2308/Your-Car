# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo, ClienteAlquiler
from YourCar.alquiler.parametros import parametros
from django.contrib.auth.models import User

#Verificar que fecha es fecha y que datos son obligatorios (tambien altera templates)

def inicioControl(request):
	conectado=False
	nombre=""
	if request.user.is_authenticated():
		conectado=True
		nombre=request.user.username
	return render_to_response ('inicio.html',locals(), context_instance = RequestContext(request))

def registroControl(request):	
	if not request.user.is_authenticated():				
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
			paisResidencia = request.POST['paisResidencia']
			ciudadResidencia = request.POST['ciudadResidencia']
			dirResidencia = request.POST['dirResidencia']
			nombrePersonaContacto = request.POST['nombrePersonaContacto']
			telContacto = request.POST['telContacto']
			direccionContacto = request.POST['direccionContacto']

			#Valido errores			
			errorUser=(User.objects.filter(username=nombreUsuario))
			errorContrasena= (request.POST["contrasena"]!=request.POST["contrasena2"])
			errorEmail= (User.objects.filter(email=email))			
			errorTels = (not telFijo.isdigit() or not telCelular.isdigit() or (len(telContacto)>0 and not telContacto.isdigit()))
			errorGenero= (genero not in (parametros["generos"]))
			errorTipoPersona= (tipoPersona not in (parametros["tipoPersonas"]))
			errorTipoDocumento= (tipoDocumento  not in (parametros["tipoDocumentos"]))						
			errorNumDocumento=  (not numDocumento.isdigit() or (ClienteAlquiler.objects.filter(numDocumento=numDocumento)))
			errorCamposVacios = (len(nombreUsuario)==0 or len(request.POST["contrasena"]))

			if (errorUser or errorContrasena or errorEmail or errorGenero or errorTipoPersona or errorTipoDocumento or errorTels or errorNumDocumento or errorCamposVacios):
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
			generos=parametros["generos"]
			tipoDocumentos=parametros["tipoDocumentos"]
			tipoPersonas=parametros["tipoPersonas"]
			return render_to_response('registro.html', locals(), context_instance = RequestContext(request))
	else:
		conectado = True
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
	return render_to_response('vehiculos.html',locals(), context_instance = RequestContext(request))
		
def cotizarControl(request):
	#Logica de control
	return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))

def agregarVehiculoControl(request):
	if request.user.is_authenticated():
		if request.user.is_staff:
			if request.method == 'POST':
				placa = request.POST["placa"]
				marca = request.POST["marca"] 
				referencia = request.POST["referencia"]
				gama = request.POST["gama"]
				descripcionBasica = request.POST["descripcionBasica"]
				tipoDeFrenos = request.POST["tipoDeFrenos"] #no
				numDePasajeros = request.POST["numDePasajeros"]
				cilindraje = request.POST["cilindraje"]
				color = request.POST["color"]
				cajaDeCambios = request.POST["cajaDeCambios"] 
				airbags = request.POST["airbags"] #no
				tipoDeDireccion = request.POST["tipoDeDireccion"] #mecanica, hidraulica, electronica
				traccion = request.POST["traccion"] #no  OPCIONEs delantera trasera 4x4
				modelo = request.POST["modelo"] #no
				valorGarantia = request.POST["valorGarantia"] #no
				estado = request.POST["estado"] #Disponible, reservado, rentado, en mantenimiento
				kilometraje = request.POST["kilometraje"] #no
				limiteKilometraje = request.POST["limiteKilometraje"]
				tarifa = request.POST["tarifa"]
				fechaVencSOAT = request.POST["fechaVencSOAT"]
				fechaVencSeguroTodoRiesgo = request.POST["fechaVencSeguroTodoRiesgo"]
				fechaVencRevisionTecMec = request.POST["fechaVencRevisionTecMec"]
				fechaVencCambioAceite = request.POST["fechaVencCambioAceite"]
				HttpResponseRedirect('vehiculos.html')
			else:
				cajasDeCambios=parametros["cajasDeCambios"]
				tipoDeDirecciones=parametros["tipoDeDirecciones"]
				estadosVehiculo=parametros["estadosVehiculo"]
				tiposTraccion=parametros["tiposTraccion"]
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