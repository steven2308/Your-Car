# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo

def loginControl(request):
	try:
		username = request.POST['username']
		password = request.POST['password']
		usuario = authenticate(username=username, password=password)
		if usuario is not None and usuario.is_active:
			login(request, usuario)
			return HttpResponseRedirect('/inicio')
	except:
		return HttpResponseRedirect('/')
	loginFailed = True
	return render_to_response('inicio.html', locals(), context_instance = RequestContext(request))


def inicioControl(request):
	if request.user.is_authenticated():
		if request.user.is_superuser:
			return HttpResponseRedirect('/admin')
		else:
			usuario = request.user
			conectado= True
			return render_to_response('inicio.html',locals())
	else:
		conectado=False
		return render_to_response('login.html',locals())	

def vehiculosPrueba(request):
	vehiculos = Vehiculo.objects.all()	
	return render_to_response('vehiculos.html',locals())




