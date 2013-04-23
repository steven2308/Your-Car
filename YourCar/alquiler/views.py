# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo, ClienteAlquiler, Mantenimiento, Voucher
from YourCar.alquiler.parametros import parametros
from django.contrib.auth.models import User
import re, math
from datetime import datetime

#Correcciones:
#Verificar que fecha es fecha
#Visualizar voucher
#Ver listado de historial de mantenimiento
#Traer fechas en modificar
#agregar foto

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
			#Tomo los datos
			nombreUsuario=request.POST["nombreUsuario"]
			email=request.POST["email"]
			fechaNacimiento = request.POST['fechaNacimiento']
			telFijo = request.POST['telFijo']
			telCelular = request.POST['telCelular']
			genero = request.POST['genero']
			tipoPersona = request.POST['tipoPersona']
			tipoDocumento = request.POST['tipoDocumento']
			numDocumento = request.POST['numDocumento']
			paisResidencia= request.POST['paisResidencia']
			ciudadResidencia= request.POST['ciudadResidencia']
			dirResidencia= request.POST['dirResidencia']
			#Inicializo datos opcionales
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
			usuario.first_name = request.POST['nombres']
			usuario.last_name = request.POST['apellidos']
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
	misionInicio= parametros["misionInicio"]
	visionInicio= parametros["visionInicio"]
	quienesSomosInicio= parametros["quienesSomosInicio"]
	return render_to_response('inicio.html', locals(), context_instance = RequestContext(request))

def verVehiculosControl(request):
	is_staff = request.user.is_staff
	gamas=parametros["gamas"]
	if request.method=="POST":
		query = {}
		if request.POST["ascDesc"]=="True":
			order = request.POST["orderBy"]
		else:
			order = "-"+request.POST["orderBy"]
		#Tomo los datos
		gama=request.POST["gama"]
		marca=request.POST["marca"]
		modelo=request.POST["modelo"]
		numDePasajeros=""
		cilindraje=""
		cajaDeCambios=""
		try:
			numDePasajeros=request.POST["numDePasajeros"]
			cilindraje=request.POST["cilindraje"]
			cajaDeCambios=request.POST["cajaDeCambios"]
		except:
			pass
		#Los datos que no son vacios los agrego al query
		if gama:
			query["gama__iexact"]=gama
		if marca:
			query["marca__icontains"]=marca
		if modelo and re.match("^([0-9]{4})$",modelo):
			query["modelo__icontains"]=modelo
		if numDePasajeros and re.match("^([0-9]{1,2})$",numDePasajeros):
			query["numDePasajeros"]=numDePasajeros
		if cilindraje and re.match("^([0-9]{4})$",cilindraje):
			query["cilindraje"]=cilindraje
		if cajaDeCambios:
			query["cajaDeCambios__icontains"]=cajaDeCambios

		#Si la consulta no es vacia la hago
		if query:
			vehiculos= Vehiculo.objects.filter(**query).order_by(order)
			filtrados=True
		else:
			vehiculos = Vehiculo.objects.all().order_by(order)
		#mensaje=request.POST["orderBy"]
		#return render_to_response ('pruebas.html',locals(), context_instance = RequestContext(request))
		return render_to_response('inventarioVehiculos.html',locals(), context_instance = RequestContext(request))
	vehiculos = Vehiculo.objects.all()
	return render_to_response('inventarioVehiculos.html',locals(), context_instance = RequestContext(request))

def detallesVehiculoControl(request):
	if request.method == 'POST':
		try:
			placa=request.POST["placa"].upper()
			vehiculo = Vehiculo.objects.get(placa=placa)
			is_staff = request.user.is_staff
			return render_to_response('detallesVehiculo.html',locals(), context_instance = RequestContext(request))
		except:
			return HttpResponseRedirect('/vehiculos')
	return HttpResponseRedirect('/vehiculos')

def historialMantenimientoControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			try:
				placa=request.POST["placa"].upper()
				vehiculo = Vehiculo.objects.get(placa=placa)
				mantenimientos = Mantenimiento.objects.filter(idVehiculo=vehiculo)
				vehiculoCargado = True
				return render_to_response('historialMantenimiento.html',locals(), context_instance = RequestContext(request))
			except:
				return HttpResponseRedirect('/vehiculos/historialMantenimiento')
		else:
			mantenimientos = Mantenimiento.objects.all()
			return render_to_response('historialMantenimiento.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def agregarHistorialMantenimientoControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		tipos=parametros["tiposMantenimiento"]
		#Si me enviaron datos intento guardarlos
		if request.method == 'POST':
			try:
				#Tomo datos
				placa=request.POST["placa"].upper()
				vehiculo = Vehiculo.objects.get(placa=placa)
				fecha = request.POST["fecha"]
				descripcion = ""
				costo = request.POST["costo"]
				tipo = request.POST["tipo"]

				#Tomo dato opcional
				if request.POST["descripcion"]:
					descripcion= request.POST["descripcion"]

				#Hago validaciones
				errorPlaca = not Vehiculo.objects.filter(placa=placa) or not re.match("^([A-Z]{3}[0-9]{3})$",placa)
				errorTipo = tipo not in tipos
				errorCosto = not re.match("^([0-9]{3,10})$",costo)

				#Si hay errores vuelvo al formulario y los informo
				if (errorPlaca or errorTipo or errorCosto):
					return render_to_response('agregarHistorialMantenimiento.html',locals(), context_instance = RequestContext(request))

				#Si no hay errores guardo el mantenimiento y vuelvo al historial
				mantenimiento = Mantenimiento(idVehiculo=vehiculo,fecha=fecha, descripcion=descripcion, costo=costo, tipo=tipo)
				mantenimiento.save()
				exito=True
			except:
				pass
			return render_to_response('agregarHistorialMantenimiento.html',locals(), context_instance = RequestContext(request))
		#Sino es post cargo el formulario
		else:
			try:
				placa=request.GET["placaActual"]
			except:
				pass
			return render_to_response('agregarHistorialMantenimiento.html',locals(), context_instance = RequestContext(request))
	#Sino esta autenticado ni es staff envio a pagina de error
	else:
		return HttpResponseRedirect('/404')

def eliminarHistorialMantenimientoControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		#Si me envian el dato lo tomo e intento borrar
		if request.method == 'POST':
			try:
				idMantenimiento=request.POST["idMantenimiento"]
				mantenimiento=Mantenimiento.objects.get(pk=idMantenimiento)
				mantenimiento.delete()
			except:
				pass
		#En cualquier caso vuelvo a la pagina de  historial.
		return HttpResponseRedirect('/vehiculos/historialMantenimiento')
	else:
		return HttpResponseRedirect('/404')

def cotizarControl(request):
	if request.method == 'POST':
		try:
			#Tomo datos
			placa=request.POST["placa"].upper()
			vehiculo = Vehiculo.objects.get(placa=placa)
			fechaIni = request.POST["fechaIni"]
			fechaFin = request.POST["fechaFin"]
			horaIni = request.POST["horaIni"]
			horaFin = request.POST["horaFin"]

			#Calculo dias y diferencia
			dtIni = datetime.strptime(fechaIni+" "+horaIni, '%Y-%m-%d %H:%M')
			dtFin = datetime.strptime(fechaFin+" "+horaFin, '%Y-%m-%d %H:%M')
			diferencia =  dtFin-dtIni

			#Hago validaciones
			errorPlaca = not Vehiculo.objects.filter(placa=placa) or not re.match("^([A-Z]{3}[0-9]{3})$",placa)
			errorFechas = dtIni > dtFin or datetime.now()> dtIni
			#Si hay errores vuelvo al formulario y los informo
			if (errorPlaca or errorFechas):
				return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))

			#Calculos
			diasReal = diferencia.days
			dias = diasReal
			segs  = diferencia.seconds
			horasReal = math.floor(segs/3600)
			horas=horasReal
			mins = (segs%3600)/60
			if mins>=30:
				horas+=1
			if(horas>6):
				dias+=1
				horas=0
			tarifaDia = vehiculo.tarifa
			totalPorDias = dias*tarifaDia
			tarifaHora = math.floor(tarifaDia/24)
			totalPorHoras = horas*tarifaHora
			tarifaDia = vehiculo.tarifa
			limiteKilometraje = vehiculo.limiteKilometraje
			total=totalPorDias+totalPorHoras

			#formateo resultados
			tarifaDia = intWithCommas(tarifaDia)
			tarifaHora = intWithCommas(tarifaHora)
			totalPorDias = intWithCommas(totalPorDias)
			totalPorHoras = intWithCommas(totalPorHoras)
			total= intWithCommas(total)
			cotizado=True

		except:
			pass
		return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))
	#Sino es post cargo el formulario
	else:
		try:
			placa=request.GET["placaActual"]
		except:
			pass
		return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))

def intWithCommas(x):
	try:
	    if x < 0:
	        return '-' + intWithCommas(-x)
	    result = ''
	    while x >= 1000:
	        x, r = divmod(x, 1000)
	        result = ".%03d%s" % (r, result)
	    return "%d%s" % (x, result)
	except:
		return x

def agregarVehiculoControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		#Cargo datos parametrizables
		cajasDeCambios=parametros["cajasDeCambios"]
		tipoDeDirecciones=parametros["tipoDeDirecciones"]
		estadosVehiculo=parametros["estadosVehiculo"]
		tiposTraccion=parametros["tiposTraccion"]
		tiposDeFrenos=parametros["tiposDeFrenos"]
		gamas=parametros["gamas"]
		if request.method == 'POST':
			#Cargo datos requeridos del auto
			placa = request.POST["placa"].upper()
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
			foto = request.POST["foto"]
			fechaVencSOAT = request.POST["fechaVencSOAT"]
			fechaVencSeguroTodoRiesgo = request.POST["fechaVencSeguroTodoRiesgo"]
			fechaVencRevisionTecMec = request.POST["fechaVencRevisionTecMec"]
			fechaVencCambioAceite = request.POST["fechaVencCambioAceite"]
			foto = request.POST["foto"]
			modificar = ""
			#inicializo datos opcionales
			tipoDeFrenos = ""
			airbags = "0"
			tipoDeDireccion = ""
			tipoDeTraccion = ""
			modelo = "0"
			valorGarantia = "0"
			kilometraje = "0"

			#tomo datos ingresados por el usuario
			if request.POST['tipoDeFrenos']: tipoDeFrenos = request.POST['tipoDeFrenos']
			if request.POST['airbags']: airbags = request.POST['airbags']
			if request.POST['tipoDeDireccion']: tipoDeDireccion = request.POST['tipoDeDireccion']
			if request.POST['tipoDeTraccion']: tipoDeTraccion = request.POST['tipoDeTraccion']
			if request.POST['modelo']: modelo = request.POST['modelo']
			if request.POST['valorGarantia']: valorGarantia = request.POST['valorGarantia']
			if request.POST['kilometraje']: kilometraje = request.POST['kilometraje']
			#verifico si estoy modificando
			try:
				modificar = request.POST["modificar"]
			except:
				pass
			#Control de errores
			if modificar:
				errorPlaca = not re.match("^([A-Z]{3}[0-9]{3})$",placa)
			else:
				errorPlaca = ((Vehiculo.objects.filter(placa=placa)) or not re.match("^([A-Z]{3}[0-9]{3})$",placa))
			errorTipoDeFrenos = (tipoDeFrenos not in parametros["tiposDeFrenos"])
			errorNumDePasajeros = not re.match("^[0-9]{1,2}$",numDePasajeros)
			errorGama = (gama not in parametros["gamas"])
			errorAirbags = not re.match("^([0-9]{1,2})$",airbags)
			errorModelo = not re.match("^([0-9]{4})$",modelo) and modelo != "0"
			errorValorGarantia = not re.match("^([0-9]{5,7})$",valorGarantia) and valorGarantia != "0"
			errorKilometraje = not re.match("^([0-9]{1,6})$",kilometraje)
			errorCajaDeCambios = (cajaDeCambios not in parametros["cajasDeCambios"])
			errorEstado = (estado not in parametros["estadosVehiculo"])
			errorTipoDeDireccion = (tipoDeDireccion not in parametros["tipoDeDirecciones"])
			errorTipoDeTraccion = (tipoDeTraccion not in parametros["tiposTraccion"])
			errorFoto = not foto
			errorCamposVaciosVeh = (len(placa)==0 or len(marca)==0 or len(referencia)==0 or len(gama)==0 or len(descripcionBasica)==0 or len(numDePasajeros)==0 or len(cilindraje)==0 or len(color)==0 or len(limiteKilometraje)==0 or len(tarifa)==0 or len(fechaVencSOAT)==0 or len(fechaVencCambioAceite)==0 or len(fechaVencRevisionTecMec)==0 or len(fechaVencSeguroTodoRiesgo)==0)

			#manejo de errores
			if (errorTipoDeFrenos or errorPlaca or errorNumDePasajeros or errorGama or errorAirbags or errorModelo or errorValorGarantia or errorKilometraje or errorCajaDeCambios or errorEstado or errorTipoDeDireccion or errorTipoDeTraccion or errorFoto or errorCamposVaciosVeh):
				return render_to_response('agregarVehiculo.html', locals(), context_instance = RequestContext(request))

			#guardar vehiculo
			vehiculo = Vehiculo(placa = placa, marca = marca, referencia = referencia, gama = gama, descripcionBasica = descripcionBasica, numDePasajeros = numDePasajeros, cilindraje = cilindraje, color = color, cajaDeCambios = cajaDeCambios, limiteKilometraje = limiteKilometraje, tarifa = tarifa, estado = estado, fechaVencSOAT = fechaVencSOAT, fechaVencSeguroTodoRiesgo = fechaVencSeguroTodoRiesgo, fechaVencRevisionTecMec = fechaVencRevisionTecMec, fechaVencCambioAceite = fechaVencCambioAceite, tipoDeFrenos = tipoDeFrenos, airbags = airbags, tipoDeDireccion = tipoDeDireccion, tipoDeTraccion = tipoDeTraccion, modelo = modelo, valorGarantia = valorGarantia, kilometraje = kilometraje, foto=foto)
			vehiculo.save()
			return HttpResponseRedirect('/vehiculos')
		else:
			return render_to_response('agregarVehiculo.html', locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def modificarVehiculoControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'POST':
		cajasDeCambios=parametros["cajasDeCambios"]
		tipoDeDirecciones=parametros["tipoDeDirecciones"]
		estadosVehiculo=parametros["estadosVehiculo"]
		tiposTraccion=parametros["tiposTraccion"]
		tiposDeFrenos=parametros["tiposDeFrenos"]
		gamas=parametros["gamas"]
		try:
			placa=request.POST["placa"].upper()
			vehiculo = Vehiculo.objects.get(placa=placa)
			return render_to_response('modificarVehiculo.html',locals(), context_instance = RequestContext(request))
		except:
			HttpResponseRedirect('/vehiculos')
	return HttpResponseRedirect('/')

def eliminarVehiculoControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'POST':
		try:
			placa=request.POST["placa"]
			vehiculo = Vehiculo.objects.get(placa=placa)
			vehiculo.delete()
		except:
			pass
		return HttpResponseRedirect('/vehiculos')
	else:
		return HttpResponseRedirect('/404')

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

def agregarVoucherControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			#Tomo los datos
			codigoAutorizacion=request.POST["codigoAutorizacion"]
			idCliente=request.POST["idCliente"]
			montoVoucher = request.POST['montoVoucher']
			numTarjetaCredito = request.POST['numTarjetaCredito']
			fechaVencTarjeta = request.POST['fechaVencTarjeta']
			codigoVerifTarjeta = request.POST['codigoVerifTarjeta']
			nombreBanco = request.POST['nombreBanco']

			#Valido errores
			errorcodigoAutorizacion =(Voucher.objects.filter(codigoAutorizacion=codigoAutorizacion)) #Or pattern?
			erroridCliente=False
			try:
				cliente=ClienteAlquiler.objects.get(numDocumento=idCliente)
			except:
				erroridCliente = True
			errormontoVoucher = (not re.match(r"^[0-9]{4,8}$", montoVoucher))
			errornumTarjetaCredito  = False #or pattern?
			errorcodigoVerifTarjeta = False #or pattern?
			errorCamposVacios = (len(codigoAutorizacion)==0 or len(numTarjetaCredito)==0 or len(codigoVerifTarjeta)==0 or len(nombreBanco)==0)

			if (errorcodigoAutorizacion or erroridCliente or errormontoVoucher or errornumTarjetaCredito or errorcodigoVerifTarjeta or errorCamposVacios):
				return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))

			#Guardo el voucher
			voucher = Voucher(codigoAutorizacion= codigoAutorizacion,idCliente = cliente,montoVoucher = montoVoucher,numTarjetaCredito = numTarjetaCredito,fechaVencTarjeta = fechaVencTarjeta,codigoVerifTarjeta = codigoVerifTarjeta,nombreBanco = nombreBanco)
			voucher.save()
			exito=True
			return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))
		else:
			return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def voucherControl(request):
	return HttpResponseRedirect('/404')

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

def notFoundControl(request):
	return render_to_response('404.html',locals(),context_instance = RequestContext(request))
