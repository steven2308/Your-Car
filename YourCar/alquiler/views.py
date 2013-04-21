# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo, ClienteAlquiler
from django.contrib.auth.models import User

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
			usuario = User.objects.create_user(username=request.POST["nombreUsuario"], email=request.POST["email"], password=request.POST["contrasena"])
			usuario.first_name = request.POST['nombre']
			usuario.last_name = request.POST['apellido']
			usuario.save()
			fechaNacimiento = request.POST['fechaNacimiento']
			telFijo = request.POST['telFijo']
			telCelular = request.POST['telCelular']
			genero = request.POST['genero']
			tipoPersona = request.POST['tipoPersona']
			tipoDocumento  = request.POST['tipoDocumento']
			numDocumento = request.POST['numDocumento']
			paisResidencia = request.POST['paisResidencia']
			ciudadResidencia = request.POST['ciudadResidencia']
			dirResidencia = request.POST['dirResidencia']
			nombrePersonaContacto = request.POST['nombrePersonaContacto']
			telContacto = request.POST['telContacto']
			direccionContacto = request.POST['direccionContacto']
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
	#Logica de control
	vehiculos = Vehiculo.objects.all()	
	return render_to_response('vehiculos.html',locals(), context_instance = RequestContext(request))
		
def cotizarControl(request):
	#Logica de control
	return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))

def agregarVehiculoControl(request):
	#Logica de control
	return render_to_response('agregarVehiculo.html',locals(), context_instance = RequestContext(request))

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