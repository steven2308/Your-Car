# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo, ClienteAlquiler, Mantenimiento, Voucher, Reserva, Contrato,ConductorAutorizado, DatosAlquiler
from YourCar.alquiler.parametros import parametros
from django.contrib.auth.models import User
from django.core.paginator import Paginator,EmptyPage,InvalidPage
import re, math, os, ast
from datetime import datetime

def inicioControl(request, registerSuccess=False):
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
			nombres = request.POST['nombres']
			apellidos = request.POST['apellidos']
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
			errorFecha= not fechaCorrecta(fechaNacimiento)
			errorTels = (not re.match("^([0-9]{7,12})$",telFijo) or not re.match("^([0-9]{10,12})$",telCelular) or (len(telContacto)>1 and not re.match("^([0-9]{7,12})$",telContacto)))
			errorGenero= (genero not in (parametros["generos"]))
			errorTipoPersona= (tipoPersona not in (parametros["tipoPersonas"]))
			errorTipoDocumento= (tipoDocumento  not in (parametros["tipoDocumentos"]))
			errorNumDocumento=  ((ClienteAlquiler.objects.filter(numDocumento=numDocumento)) or not re.match("^([a-zA-z0-9_-]{6,20})$",numDocumento))
			errorDatosResidencia= (not paisResidencia or not ciudadResidencia or not dirResidencia)
			errorLongDatosResidencia= (len(paisResidencia)>20 or len(ciudadResidencia)>20 or len(dirResidencia)>40)
			errorLongDatosOpcionales= (len(nombrePersonaContacto)>20 or len(direccionContacto)>40)
			errorCamposVacios = (len(nombreUsuario)==0 or len(request.POST["contrasena"])==0 or len(nombres)==0 or len(apellidos)==0)

			if (errorUser or errorContrasena or errorEmail or errorFecha or errorGenero or errorTipoPersona or errorTipoDocumento or errorTels or errorNumDocumento or errorDatosResidencia or errorCamposVacios or errorLongDatosResidencia or errorLongDatosOpcionales):
				return render_to_response('registro.html', locals(), context_instance = RequestContext(request))

			#Guardo el usuario
			usuario = User.objects.create_user(username=nombreUsuario, email=email, password=request.POST["contrasena"])
			usuario.first_name = nombres
			usuario.last_name = apellidos
			usuario.save()

			#Guardo el cliente de alquiler
			cliente = ClienteAlquiler(user = usuario, fechaNacimiento = fechaNacimiento, telFijo = telFijo,
				telCelular = telCelular, genero = genero, tipoPersona = tipoPersona, tipoDocumento = tipoDocumento,
				numDocumento = numDocumento, paisResidencia = paisResidencia, ciudadResidencia = ciudadResidencia,
				dirResidencia = dirResidencia, nombrePersonaContacto = nombrePersonaContacto, telContacto= telContacto,
				direccionContacto=direccionContacto)
			cliente.save()
			return inicioControl(request,registerSuccess=True)
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
				return HttpResponseRedirect('/vehiculos')
			return HttpResponseRedirect('/vehiculos')
	except:
		return HttpResponseRedirect('/')
	loginFailed = True
	misionInicio= parametros["misionInicio"]
	visionInicio= parametros["visionInicio"]
	quienesSomosInicio= parametros["quienesSomosInicio"]
	return render_to_response('inicio.html', locals(), context_instance = RequestContext(request))

def verVehiculosControl(request,  pagina=1, addSuccess=False):
	is_staff = request.user.is_staff
	gamas=parametros["gamas"]
	estadosVehiculo=parametros["estadosVehiculo"]
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
		estado=""
		cajaDeCambios=""
		try:
			numDePasajeros=request.POST["numDePasajeros"]
			estado=request.POST["estado"]
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
		if estado and estado in estadosVehiculo:
			query["estado__iexact"]=estado
		if cajaDeCambios:
			query["cajaDeCambios__icontains"]=cajaDeCambios

		#Si la consulta no es vacia la hago
		if query:
			listaVehiculos= Vehiculo.objects.filter(**query).order_by(order)
			filtrados=True
		else:
			listaVehiculos = Vehiculo.objects.all().order_by(order)
		vehiculos=paginar(listaVehiculos,pagina)
		return render_to_response('inventarioVehiculos.html',locals(), context_instance = RequestContext(request))
	#sino es un post cargo todos
	listaVehiculos = Vehiculo.objects.all()
	vehiculos=paginar(listaVehiculos,pagina)
	return render_to_response('inventarioVehiculos.html',locals(), context_instance = RequestContext(request))

def detallesVehiculoControl(request,placa):
	try:
		#placa=request.POST["placa"].upper()
		vehiculo = Vehiculo.objects.get(placa=placa.upper())
		is_staff = request.user.is_staff
		is_authenticated = request.user.is_authenticated
		return render_to_response('detallesVehiculo.html',locals(), context_instance = RequestContext(request))
	except:
		return HttpResponseRedirect('/vehiculos')

def historialMantenimientoControl(request, pagina=1):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			try:
				placa=request.POST["placa"].upper()
				vehiculo = Vehiculo.objects.get(placa=placa)
				lista_mantenimientos = Mantenimiento.objects.filter(idVehiculo=vehiculo)
				mantenimientos=paginar(lista_mantenimientos,pagina)
				vehiculoCargado = True
				return render_to_response('historialMantenimiento.html',locals(), context_instance = RequestContext(request))
			except:
				return HttpResponseRedirect('/vehiculos/historialMantenimiento')
		else:
			lista_mantenimientos = Mantenimiento.objects.all()
			mantenimientos=paginar(lista_mantenimientos,pagina)
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
				errorFecha= not fechaCorrecta(fecha)
				errorTipo = tipo not in tipos
				errorCosto = not re.match("^([0-9]{3,10})$",costo)
				errorDescripcion = len(descripcion)>200

				#Si hay errores vuelvo al formulario y los informo
				if (errorPlaca or errorFecha or errorTipo or errorCosto or errorDescripcion):
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
	lugaresCostos = parametros["lugaresCostos"]
	lugares = lugaresCostos.keys
	logged = request.user.is_authenticated()
	if request.method == 'POST':
		#try:
			#Tomo datos
			placa=request.POST["placa"].upper()
			fechaIni = request.POST["fechaIni"]
			fechaFin = request.POST["fechaFin"]
			horaIni = request.POST["horaIni"]
			horaFin = request.POST["horaFin"]
			lugarRecogida = request.POST["lugarRecogida"]
			lugarEntrega = request.POST["lugarEntrega"]

			#Hago validaciones
			errorLugares = False
			errorPlaca = not Vehiculo.objects.filter(placa=placa) or not re.match("^([A-Z]{3}[0-9]{3})$",placa)
			errorFechas1 =  not fechaCorrecta(fechaIni) or not fechaCorrecta(fechaFin)
			errorHoras = not re.match('[0-9]{2}:[0-9]{2}',horaIni) or  not re.match('[0-9]{2}:[0-9]{2}',horaFin)
			errorFechas2 = False
			try:
				costoRecogida=int(lugaresCostos[lugarRecogida])
				costoEntrega=int(lugaresCostos[lugarEntrega])
			except:
				errorLugares = True
			#Si las fechas y las horas tienen un formato correcto verifico la logica
			if not errorFechas1 and not errorHoras:
				#Calculo dias y diferencia
				dtIni = datetime.strptime(fechaIni+" "+horaIni, '%Y-%m-%d %H:%M')
				dtFin = datetime.strptime(fechaFin+" "+horaFin, '%Y-%m-%d %H:%M')
				#La fecha inicial debe ser menor a la final y mayor a la actual
				errorFechas2 = dtIni > dtFin or datetime.now()> dtIni
			#Si hay errores vuelvo al formulario y los informo
			if (errorPlaca or errorFechas1 or errorFechas2 or errorHoras or errorLugares):
				return render_to_response('cotizar.html',locals(), context_instance = RequestContext(request))
			vehiculo = Vehiculo.objects.get(placa=placa)
			#Calculos
			cotizacion = cotizar(dtIni,dtFin,costoRecogida,costoEntrega,vehiculo)
			cotizado=True
		#except:
		#	pass
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
			fechaVencSOAT = request.POST["fechaVencSOAT"]
			fechaVencSeguroTodoRiesgo = request.POST["fechaVencSeguroTodoRiesgo"]
			fechaVencRevisionTecMec = request.POST["fechaVencRevisionTecMec"]
			fechaVencCambioAceite = request.POST["fechaVencCambioAceite"]
			modificar = ""

			#inicializo datos opcionales
			tipoDeFrenos = ""
			airbags = "0"
			tipoDeDireccion = ""
			tipoDeTraccion = ""
			modelo = "0"
			valorGarantia = "0"
			kilometraje = "0"

			try:
				modificar = request.POST["modificar"]
			except:
				pass

			if modificar:
				try:
					foto = request.FILES["foto"]
				except:
					foto = Vehiculo.objects.get(placa=placa).foto
			else:
				foto = request.FILES["foto"]

			if request.POST['tipoDeFrenos']: tipoDeFrenos = request.POST['tipoDeFrenos']
			if request.POST['airbags']: airbags = request.POST['airbags']
			if request.POST['tipoDeDireccion']: tipoDeDireccion = request.POST['tipoDeDireccion']
			if request.POST['tipoDeTraccion']: tipoDeTraccion = request.POST['tipoDeTraccion']
			if request.POST['modelo']: modelo = request.POST['modelo']
			if request.POST['valorGarantia']: valorGarantia = request.POST['valorGarantia']
			if request.POST['kilometraje']: kilometraje = request.POST['kilometraje']

			#Control de errores
			if modificar:
				errorPlaca = not re.match("^([A-Z]{3}[0-9]{3})$",placa)
			else:
				errorPlaca = ((Vehiculo.objects.filter(placa=placa)) or not re.match("^([A-Z]{3}[0-9]{3})$",placa))
				errorFoto = not foto
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
			errorFoto = False
			errorCamposVaciosVeh = (len(placa)==0 or len(marca)==0 or len(referencia)==0 or len(gama)==0 or len(descripcionBasica)==0 or len(numDePasajeros)==0 or len(cilindraje)==0 or len(color)==0 or len(limiteKilometraje)==0 or len(tarifa)==0 or len(fechaVencSOAT)==0 or len(fechaVencCambioAceite)==0 or len(fechaVencRevisionTecMec)==0 or len(fechaVencSeguroTodoRiesgo)==0)
			errorFechas= not fechaCorrecta(fechaVencSOAT) or not fechaCorrecta(fechaVencSeguroTodoRiesgo) or not fechaCorrecta(fechaVencRevisionTecMec) or not fechaCorrecta(fechaVencCambioAceite)
			errorEnteros= False
			try:
				errorEnteros = int(cilindraje)>2000000000 or int(tarifa)>2000000000 or int(kilometraje)>2000000000 or int(limiteKilometraje)>2000000000
			except:
				errorEnteros = True
			errorLongDatos = len(marca)>15 or len (referencia)>15 or len(color)>15 or len(descripcionBasica)>100
			#manejo de errores
			if (errorTipoDeFrenos or errorPlaca or errorNumDePasajeros or errorGama or errorAirbags or errorModelo or errorValorGarantia or errorKilometraje or errorCajaDeCambios or errorEstado or errorTipoDeDireccion or errorTipoDeTraccion or errorFoto or errorCamposVaciosVeh or errorFechas or errorEnteros or errorLongDatos):
				errorExist = True
				return render_to_response('agregarVehiculo.html', locals(), context_instance = RequestContext(request))

			#guardar vehiculo
			vehiculo = Vehiculo(placa = placa, marca = marca, referencia = referencia, gama = gama, descripcionBasica = descripcionBasica, numDePasajeros = numDePasajeros, cilindraje = cilindraje, color = color, cajaDeCambios = cajaDeCambios, limiteKilometraje = limiteKilometraje, tarifa = tarifa, estado = estado, fechaVencSOAT = fechaVencSOAT, fechaVencSeguroTodoRiesgo = fechaVencSeguroTodoRiesgo, fechaVencRevisionTecMec = fechaVencRevisionTecMec, fechaVencCambioAceite = fechaVencCambioAceite, tipoDeFrenos = tipoDeFrenos, airbags = airbags, tipoDeDireccion = tipoDeDireccion, tipoDeTraccion = tipoDeTraccion, modelo = modelo, valorGarantia = valorGarantia, kilometraje = kilometraje, foto=foto)
			vehiculo.save()
			request.method="GET"
			return verVehiculosControl(request,addSuccess=True)
		else:
			return render_to_response('agregarVehiculo.html', locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def modificarVehiculoControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'GET':
		cajasDeCambios=parametros["cajasDeCambios"]
		tipoDeDirecciones=parametros["tipoDeDirecciones"]
		estadosVehiculo=parametros["estadosVehiculo"]
		tiposTraccion=parametros["tiposTraccion"]
		tiposDeFrenos=parametros["tiposDeFrenos"]
		gamas=parametros["gamas"]
		try:
			placa=request.GET["placa"]
			vehiculo = Vehiculo.objects.get(placa=placa)
			fechaVencSOAT = formatearFecha(vehiculo.fechaVencSOAT)
			fechaVencSeguroTodoRiesgo = formatearFecha(vehiculo.fechaVencSeguroTodoRiesgo)
			fechaVencRevisionTecMec = formatearFecha(vehiculo.fechaVencRevisionTecMec)
			fechaVencCambioAceite = formatearFecha(vehiculo.fechaVencCambioAceite)
			#return render_to_response('pruebas.html',locals(), context_instance = RequestContext(request))
			return render_to_response('modificarVehiculo.html',locals(), context_instance = RequestContext(request))
		except:
			HttpResponseRedirect('/vehiculos')
	return HttpResponseRedirect('/')

def eliminarVehiculoControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'GET':
		try:
			placa=request.GET["placa"]
			vehiculo = Vehiculo.objects.get(placa=placa)
			vehiculo.delete()
		except:
			pass
		return HttpResponseRedirect('/vehiculos')
	else:
		return HttpResponseRedirect('/404')

def eliminarReservaControl(request):
	if request.user.is_authenticated() and request.method == 'GET':
		try:
			idReserva=request.GET["idReserva"]
			reserva = Reserva.objects.get(idReserva=idReserva)
			reserva.delete()
		except:
			pass
		return HttpResponseRedirect('/reservas')
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
			errorcodigoAutorizacion =(Voucher.objects.filter(codigoAutorizacion=codigoAutorizacion)) or not re.match("^([0-9]{4,6})$",codigoAutorizacion)
			erroridCliente=False
			try:
				cliente=ClienteAlquiler.objects.get(numDocumento=idCliente)
			except:
				erroridCliente = True
			errormontoVoucher = (not re.match("^[0-9]{4,8}$", montoVoucher))
			errornumTarjetaCredito  = not re.match("^([0-9]{15,16})$",numTarjetaCredito)
			errorcodigoVerifTarjeta = not re.match("^([0-9]{3,4})$",codigoVerifTarjeta)
			errorFecha = not fechaCorrecta(fechaVencTarjeta)
			errorCamposVacios = (len(codigoAutorizacion)==0 or len(numTarjetaCredito)==0 or len(codigoVerifTarjeta)==0 or len(nombreBanco)==0)
			errorNombreBanco = len(nombreBanco)>20

			if (errorcodigoAutorizacion or erroridCliente or errormontoVoucher or errornumTarjetaCredito or errorcodigoVerifTarjeta or errorFecha or errorCamposVacios or errorNombreBanco):
				return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))

			#Guardo el voucher
			voucher = Voucher(codigoAutorizacion= codigoAutorizacion,idCliente = cliente,montoVoucher = montoVoucher,numTarjetaCredito = numTarjetaCredito,fechaVencTarjeta = fechaVencTarjeta,codigoVerifTarjeta = codigoVerifTarjeta,nombreBanco = nombreBanco)
			voucher.save()
			exito=True
			return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))
		else:
			return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def voucherControl(request, pagina=1):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			try:
				busqueda = request.POST["busqueda"]
				buscarPor= request.POST["buscarPor"]
				query={}
				#Identifico por que parametro voy a buscar el voucher y lo agrego al diccionario de queries
				if buscarPor == "codigoAutorizacion":
					query["codigoAutorizacion__iexact"] = busqueda
				elif buscarPor == "idCliente":
					#cliente = ClienteAlquiler.objects.get(numDocumento=busqueda)
					query["idCliente"] = busqueda
				elif buscarPor == "numTarjetaCredito":
					query["numTarjetaCredito__iexact"] = busqueda
				if query:
					lista_vouchers = Voucher.objects.filter(**query)
					voucherCargado = True
				else:
					lista_vouchers = Voucher.objects.all()
				vouchers=paginar(lista_vouchers,pagina)
				return render_to_response('voucher.html',locals(), context_instance = RequestContext(request))
			except:
				enExcept=True
				return render_to_response('verVoucher.html',locals(), context_instance = RequestContext(request))
				#return HttpResponseRedirect('/voucher/')
		else:
			noEsPost=True
			lista_vouchers = Voucher.objects.all()
			vouchers=paginar(lista_vouchers,pagina)
			return render_to_response('verVoucher.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def eliminarVoucherControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'POST':
		try:
			codigoAutorizacion=request.POST["codigoAutorizacion"]
			voucher = Voucher.objects.get(codigoAutorizacion=codigoAutorizacion)
			voucher.delete()
		except:
			pass
		return HttpResponseRedirect('/voucher')
	else:
		return HttpResponseRedirect('/404')

def verReservasControl(request, pagina=1):
	if request.user.is_authenticated():
		is_staff = request.user.is_staff
		cliente=None
		if request.method == 'POST':
			query = {}
			idCliente = ""
			if request.POST["idCliente"]: idCliente = request.POST["idCliente"]
			idVehiculo = request.POST["idVehiculo"]
			order = request.POST["orderBy"]

			if request.user.is_staff and idCliente:
				query["idCliente"]=idCliente
			#si es un usuario, solo muestra las reservas que le corresponden a su id
			else:
				if not request.user.is_staff:
					cliente = ClienteAlquiler.objects.get(user=request.user)
					idCliente = cliente.numDocumento
					if idCliente: query["idCliente"]=idCliente

			if idVehiculo:
				query["idVehiculo"]=idVehiculo

			if query:
				listaReservas= Reserva.objects.filter(**query).order_by(order)
			else:
				listaReservas=Reserva.objects.all().order_by(order)
			reservas=paginar(listaReservas,pagina)
			return render_to_response('verReservas.html',locals(), context_instance = RequestContext(request))
		else:
			if not request.user.is_staff:
				query = {}
				cliente = ClienteAlquiler.objects.get(user=request.user)
				idCliente = cliente.numDocumento
				if idCliente: query["idCliente"]=idCliente
				if query: lista_reservas = Reserva.objects.filter(**query)
				reservas=paginar(lista_reservas,pagina)
				return render_to_response('verReservas.html',locals(), context_instance = RequestContext(request))
			else:
				lista_reservas = Reserva.objects.all()
				reservas=paginar(lista_reservas,pagina)
				return render_to_response('verReservas.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def agregarReservaControl(request):
	estadosPago=parametros["estadosPago"]
	lugaresCostos = parametros["lugaresCostos"]
	lugares = lugaresCostos.keys
	if request.user.is_authenticated():
		if request.method == 'POST':
			idVehiculo = request.POST["idVehiculo"]
			idCliente = request.POST["idCliente"]
			fechaInicio = request.POST["fechaInicio"]
			fechaFin = request.POST["fechaFin"]
			horaInicio = request.POST["horaInicio"]
			horaFin = request.POST["horaFin"]
			lugarRecogida = request.POST["lugarRecogida"]
			lugarEntrega = request.POST["lugarEntrega"]
			pagada = False
			datosDePago = ""
			fotoPago = None

			errorFormatoFechas = not fechaCorrecta(fechaInicio) or not fechaCorrecta(fechaFin)
			if not errorFormatoFechas:
				dtIni = datetime.strptime(fechaInicio+" "+horaInicio, '%Y-%m-%d %H:%M')
				dtFin = datetime.strptime(fechaFin+" "+horaFin, '%Y-%m-%d %H:%M')
				#manejo de errores
				errorFechas = dtIni > dtFin or datetime.now()> dtIni
			errorLugares = False
			errorIdCliente = False
			errorIdVehiculo = False
			errorPagada=False
			try:
				costoRecogida=int(lugaresCostos[lugarRecogida])
				costoEntrega=int(lugaresCostos[lugarEntrega])
			except:
				errorLugares = True
			try:
				cliente=ClienteAlquiler.objects.get(numDocumento=idCliente)
			except:
				errorIdCliente = True
			try:
				vehiculo=Vehiculo.objects.get(placa=idVehiculo)
			except:
				errorIdVehiculo = True
			if (datosDePago=="" and fotoPago==None and pagada==True): 
				errorPagada=True
			if not request.user.is_staff:
				usuario = ClienteAlquiler.objects.get(user=request.user)
				if idCliente != usuario.numDocumento: errorIdCliente=True
			if (errorIdCliente or errorIdVehiculo or errorPagada or errorFormatoFechas or errorFechas or errorLugares):
				return render_to_response('agregarReserva.html', locals(), context_instance = RequestContext(request))

			#guardo la reserva
			reserva = Reserva(idVehiculo = vehiculo, idCliente = cliente, fechaInicio = dtIni, fechaFin = dtFin, lugarRecogida = lugarRecogida, lugarEntrega = lugarEntrega,  pagada = False, datosDePago = "", fotoPago = None)
			reserva.save()
			return HttpResponseRedirect('/reservas')
		else:
			try:
				idVehiculo = request.GET["placa"]
				fechaInicio = formatearFecha(request.GET["fechaIni"])
				fechaFin = formatearFecha(request.GET["fechaFin"])
				horaInicio = formatearHora(request.GET["horaIni"])
				horaFin = formatearHora(request.GET["horaFin"])
				lugarRecogida = request.GET["lugarRecogida"]
				lugarEntrega = request.GET["lugarEntrega"]
			except:
				pass
			is_staff = request.user.is_staff
			if not request.user.is_staff:
					cliente = ClienteAlquiler.objects.get(user=request.user)
					numDocumento = cliente.numDocumento
			return render_to_response('agregarReserva.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def detallesReservaControl(request,idReserva):
	lugaresCostos = parametros["lugaresCostos"]
	if request.user.is_authenticated():
		#try:
			errorIdReserva=False
			reserva=Reserva.objects.get(idReserva=idReserva)
			if not request.user.is_staff:
				clienteReserva=reserva.idCliente
				clienteActual=ClienteAlquiler.objects.get(user=request.user)
				if clienteReserva.numDocumento != clienteActual.numDocumento:
					errorIdReserva=True
			is_staff=request.user.is_staff
			#Tomo los datos necesarios para la cotizacion
			vehiculo = reserva.idVehiculo
			dtIni = reserva.fechaInicio
			dtFin = reserva.fechaFin
			lugarRecogida = reserva.lugarRecogida
			lugarEntrega = reserva.lugarEntrega
			costoRecogida=int(lugaresCostos[lugarRecogida])
			costoEntrega=int(lugaresCostos[lugarEntrega])
			cotizacion = cotizar(dtIni,dtFin,costoRecogida, costoEntrega, vehiculo)
			cotizado=True
			if reserva.fotoPago:
				hayFoto=True
			return render_to_response('detallesReserva.html',locals(), context_instance = RequestContext(request))
		#except:
		#	errorIdReserva=True
		#	return render_to_response('detallesReserva.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/reservas')

def modificarReservaControl(request):
	lugaresCostos = parametros["lugaresCostos"]
	lugares = lugaresCostos.keys
	if request.user.is_authenticated():
		if request.method == 'POST':
			idVehiculo = request.POST["idVehiculo"]
			idCliente = request.POST["idCliente"]
			fechaInicio = request.POST["fechaInicio"]
			fechaFin = request.POST["fechaFin"]
			horaInicio = request.POST["horaInicio"]
			horaFin = request.POST["horaFin"]
			lugarRecogida = request.POST["lugarRecogida"]
			lugarEntrega = request.POST["lugarEntrega"]
			idReserva = request.POST["idReserva"]

			if request.user.is_staff:
				if request.POST["pagada"] == 'Si': 
					pagada = True
					try:
						vehiculo=Vehiculo.objects.get(placa=idVehiculo)
						vehiculo.estado = "Reservado"
						vehiculo.save()
					except:
						pass
				else:
					pagada = False
			else:
				pagada=False

			try:
				fotoPago = request.FILES["fotoPago"]
			except:
				fotoPago = Reserva.objects.get(idReserva=idReserva).fotoPago

			try:
				datosDePago = request.POST["datosDePago"]
			except:
				datosDePago = Reserva.objects.get(idReserva=idReserva).fotoPago

			dtIni = datetime.strptime(fechaInicio+" "+horaInicio, '%Y-%m-%d %H:%M')
			dtFin = datetime.strptime(fechaFin+" "+horaFin, '%Y-%m-%d %H:%M')

			#errores

			errorLugares = False
			errorFechas = dtIni > dtFin or datetime.now()> dtIni
			errorIdCliente=False
			errorIdVehiculo=False
			errorPagada=False
			try:
				costoRecogida=int(lugaresCostos[lugarRecogida])
				costoEntrega=int(lugaresCostos[lugarEntrega])
			except:
				errorLugares = True
			try:
				cliente=ClienteAlquiler.objects.get(numDocumento=idCliente)
			except:
				errorIdCliente = True
			try:
				vehiculo=Vehiculo.objects.get(placa=idVehiculo)
				vehiculo.estado = "Reservado"
			except:
				errorIdVehiculo = True
			if (datosDePago=="" and fotoPago==None and pagada==True): 
				errorPagada=True
			if not request.user.is_staff:
				usuario = ClienteAlquiler.objects.get(user=request.user)
				if idCliente != usuario.numDocumento: errorIdCliente=True
			if (errorPagada or errorIdCliente or errorIdVehiculo or errorFechas or errorLugares):
				return render_to_response('modificarReserva.html', locals(), context_instance = RequestContext(request))

			#reemplazo la reserva
			reserva = Reserva(idReserva=idReserva, idVehiculo = vehiculo, idCliente = cliente, fechaInicio = dtIni, fechaFin = dtFin, lugarRecogida = lugarRecogida, lugarEntrega = lugarEntrega, pagada = pagada, datosDePago = datosDePago, fotoPago = fotoPago)
			reserva.save()
			return HttpResponseRedirect('/reservas')
		else:
			estadosPago=parametros["estadosPago"]
			idReserva=request.GET["idReserva"]
			reserva=Reserva.objects.get(idReserva=idReserva)
			fechaInicio = formatearFecha(reserva.fechaInicio)
			fechaFin = formatearFecha(reserva.fechaFin)
			horaInicio = formatearHora(reserva.fechaInicio)
			horaFin = formatearHora(reserva.fechaFin)
			lugarRecogida = reserva.lugarRecogida
			lugarEntrega = reserva.lugarEntrega
			pagada = reserva.pagada
			if request.user.is_staff:
				is_staff = True
			else:
				cliente = ClienteAlquiler.objects.get(user=request.user)
				numDocumento = cliente.numDocumento
				is_staff=False
			if pagada == True and not is_staff: yaPagada = True
			return render_to_response('modificarReserva.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/reservas')

# Controlador del Cierre de Sesion
def logoutControl(request):
    logout(request)
    return HttpResponseRedirect('/')

def notFoundControl(request):
	return render_to_response('404.html',locals(),context_instance = RequestContext(request))

def fechaCorrecta(fecha):
	try:
		datetime.strptime(fecha, '%Y-%m-%d')
		return True
	except:
		return False

def paginar(lista,pagina):
	elementosPorPagina = parametros["numElementosPorPagina"]
	paginator= Paginator(lista,elementosPorPagina)
	#Si no me envian un numero lo envio a la primera
	try:
		pagina = int(pagina)
	except:
		pagina = 1
	#Intento traer la pagina solicitada, si no exite envio la ultima
	try:
		listaPaginada=paginator.page(pagina)
	except(EmptyPage,InvalidPage):
		listaPaginada=paginator.page(paginator.num_pages)
	return listaPaginada

def parametrizarControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			parametros["misionInicio"] = request.POST["misionInicio"]
			parametros["visionInicio"] = request.POST["visionInicio"]
			parametros["quienesSomosInicio"] = request.POST["quienesSomosInicio"]
			parametros["generos"] = request.POST["generos"]
			parametros["tipoPersonas"] = request.POST["tipoPersonas"]
			parametros["tipoDocumentos"] = request.POST["tipoDocumentos"]
			parametros["cajasDeCambios"] = request.POST["cajasDeCambios"]
			parametros["tipoDeDirecciones"] = request.POST["tipoDeDirecciones"]
			parametros["estadosVehiculo"] = request.POST["estadosVehiculo"]
			parametros["tiposTraccion"] = request.POST["tiposTraccion"]
			parametros["gamas"] = request.POST["gamas"]
			parametros["tiposMantenimiento"] = request.POST["tiposMantenimiento"]
			parametros["tiposDeFrenos"] = request.POST["tiposDeFrenos"]
			parametros["estadosPago"] = request.POST["estadosPago"]
			parametros["numElementosPorPagina"] = request.POST["numElementosPorPagina"]
			parametros["lugaresCostos"] = ast.literal_eval(request.POST["lugaresCostos"])
			exito=True
			param=parametros
			newInfo = "parametros = "+str(parametros).replace(': u"',': "').replace('"(','(').replace(')",','),\n').replace(')"}',')}')
			paramFile=open('YourCar\\alquiler\parametros2.py','a')
			paramFile.write(newInfo)
			paramFile.close()
			os.remove("YourCar\\alquiler\parametros.py")
			os.rename("YourCar\\alquiler\parametros2.py","YourCar\\alquiler\parametros.py")
			return render_to_response('parametrizar.html', locals(), context_instance = RequestContext(request))
		else:
			param=parametros
			return render_to_response('parametrizar.html', locals(), context_instance = RequestContext(request))
	else:
	 return HttpResponseRedirect('/404')

def formatearFecha(fecha):
	try:
		try:
			date = datetime.strptime(str(fecha)[:-15], '%Y-%m-%d')
		except:
			date = datetime.strptime(str(fecha), '%Y-%m-%d')
		tt = date.timetuple()
		anyo=tt[0]
		mes = str(tt[1])
		if len(mes)==1:
			mes="0"+mes
		dia = str(tt[2])
		if len(dia)==1:
			dia="0"+dia
		return "%s-%s-%s"%(anyo,mes,dia)
	except:
		return fecha

def formatearHora(fecha):
	try:
		date = datetime.strptime(str(fecha)[:-6], '%Y-%m-%d %H:%M:%S')
		tt = date.timetuple()
		hora = str(tt[3])
		if len(hora)==1:
			hora="0"+hora
		mins = str(tt[4])
		if len(mins)==1:
			mins="0"+mins
		return "%s:%s"%(hora,mins)
	except:
		return fecha

def cotizar(dtIni, dtFin,costoRecogida,costoEntrega,vehiculo):
	diferencia =  dtFin-dtIni
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
	kmPorHora = math.floor(limiteKilometraje/24)
	maxKms = limiteKilometraje*dias+kmPorHora*horas
	total=totalPorDias+totalPorHoras+costoEntrega+costoRecogida

	#formateo resultados
	costoRecogida = intWithCommas(costoRecogida)
	costoEntrega = intWithCommas(costoEntrega)
	tarifaDia = intWithCommas(tarifaDia)
	tarifaHora = intWithCommas(tarifaHora)
	totalPorDias = intWithCommas(totalPorDias)
	totalPorHoras = intWithCommas(totalPorHoras)
	total= intWithCommas(total)

	#guardo todo en un diccionario y lo retorno
	cotizacion = {}
	cotizacion["diasReal"]=diasReal
	cotizacion["horasReal"]=horasReal
	cotizacion["dias"]=dias
	cotizacion["horas"]=horas
	cotizacion["tarifaDia"]=tarifaDia
	cotizacion["limiteKilometraje"]=limiteKilometraje
	cotizacion["maxKms"]=maxKms
	cotizacion["costoRecogida"]=costoRecogida
	cotizacion["costoEntrega"]=costoEntrega
	cotizacion["tarifaHora"]=tarifaHora
	cotizacion["totalPorDias"]=totalPorDias
	cotizacion["totalPorHoras"]=totalPorHoras
	cotizacion["total"]=total
	return cotizacion

def contratosControl(request,pagina=1,addSuccess=False):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method=="POST":
			query = {}
			if request.POST["ascDesc"]=="True":
				order = request.POST["orderBy"]
			else:
				order = "-"+request.POST["orderBy"]
			#Tomo los datos
			idContrato=request.POST["idContrato"]
			idVoucher=request.POST["idVoucher"]
			idVehiculo=request.POST["idVehiculo"].upper()

			#Los datos que no son vacios los agrego al query
			if idContrato:
				query["idContrato"]=idContrato
			if idVoucher:
				query["idVoucher"]=idVoucher
			if idVehiculo and re.match("^([A-Z]{3}[0-9]{3})$",idVehiculo):
				query["idVehiculo"]=idVehiculo

			#squery = str(query)
			#return render_to_response('pruebas.html',locals(), context_instance = RequestContext(request))
			#Si la consulta no es vacia la hago
			if query:
				listacontratos= Contrato.objects.filter(**query).order_by(order)
				filtrados=True
			else:
				listacontratos = Contrato.objects.all().order_by(order)
			contratos=paginar(listacontratos,pagina)
			return render_to_response('contratos.html',locals(), context_instance = RequestContext(request))
		#sino es un post cargo todos
		listacontratos = Contrato.objects.all()
		contratos=paginar(listacontratos,pagina)
		return render_to_response('contratos.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def detallesContratoControl(request,idContrato,addSuccess=False, addDriverSuccess=False):
	lugaresCostos = parametros["lugaresCostos"]
	if request.user.is_authenticated() and request.user.is_staff:
		errorIdContrato=False
		try:
			contrato=Contrato.objects.get(idContrato=idContrato)
			voucher = contrato.idVoucher
			cliente = voucher.idCliente
			user = cliente.user
			vehiculo = contrato.idVehiculo
			fecha = contrato.fecha
			conductores = ConductorAutorizado.objects.filter(idContrato=contrato)
		except:
			errorIdContrato=True
			return HttpResponseRedirect('/contratos')
		return render_to_response('detallesContrato.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def agregarContratosControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			idVehiculo = request.POST["idVehiculo"]
			idVoucher = request.POST["idVoucher"]
			fecha = request.POST["fecha"]

			errorIdCliente = False
			errorIdVoucher = False
			errorIdVehiculo = False
			errorFecha= not fechaCorrecta(fecha)
			try:
				voucher = Voucher.objects.get(codigoAutorizacion=idVoucher)
			except:
				errorIdVoucher = True
			try:
				cliente= voucher.idCliente
			except:
				errorIdCliente = True
			try:
				vehiculo=Vehiculo.objects.get(placa=idVehiculo)
			except:
				errorIdVehiculo = True

			#Si hay errores retorno a la pagina
			if (errorIdCliente or errorIdVoucher or errorIdVehiculo or errorFecha):
				return render_to_response('agregarContrato.html', locals(), context_instance = RequestContext(request))

			#Si no, guardo el contrato
			contrato = Contrato(idVehiculo = vehiculo, idVoucher = voucher, fecha = fecha)
			contrato.save()
			request.method="GET"
			return detallesContratoControl(request,idContrato=contrato.idContrato,addSuccess=True)
		else:
			try:
				idVoucher = request.GET["idVoucher"]
				voucher = Voucher.objects.get(idVoucher=idVoucher)
				idCliente = voucher.idCliente
			except:
				pass
			return render_to_response('agregarContrato.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def eliminarContratosControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'POST':
		try:
			idContrato=request.POST["idContrato"]
			contrato = Contrato.objects.get(idContrato=idContrato)
			contrato.delete()
		except:
			pass
		return HttpResponseRedirect('/contratos')
	else:
		return HttpResponseRedirect('/404')

def agregarConductorControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			idContrato = request.POST["idContrato"]
			docIdentidad = request.POST["docIdentidad"]
			nombres = request.POST["nombres"]
			apellidos = request.POST["apellidos"]
			licencia = request.POST["licencia"]
			fechaNacimiento = request.POST["fechaNacimiento"]
			tipoSangre = request.POST["tipoSangre"]

			#Posibles errores
			errorIdContrato = False



			errorNumDocumento = len(docIdentidad)==0 or not re.match("^([a-zA-z0-9_-]{6,20})$",docIdentidad)
			errorCamposVacios = len(nombres)==0 or len(apellidos)==0 or len(licencia)==0 or len(tipoSangre)==0
			errorCamposLargos = len(nombres)>20 or len(apellidos)>20 or len(licencia)>20 or len(tipoSangre)>6
			errorConductorExistente = False
			if not errorNumDocumento:
				errorConductorExistente = ConductorAutorizado.objects.filter(docIdentidad=docIdentidad)
			errorFecha= not fechaCorrecta(fechaNacimiento)
			errorEdad = False
			if not errorFecha:
				fecha = datetime.strptime(fechaNacimiento, '%Y-%m-%d')
				errorEdad = not mayor21(fecha)
			try:
				contrato=Contrato.objects.get(idContrato=idContrato)
			except:
				errorIdContrato = True


			#Si hay errores retorno a la pagina
			if (errorIdContrato or errorNumDocumento or errorCamposVacios or errorCamposLargos or errorFecha or errorEdad or errorConductorExistente):
				return render_to_response('agregarConductor.html', locals(), context_instance = RequestContext(request))

			#Si no, guardo el conductor
			conductor = ConductorAutorizado(idContrato = contrato, docIdentidad = docIdentidad, nombres = nombres, apellidos = apellidos, licencia = licencia, fechaNacimiento = fechaNacimiento, tipoSangre = tipoSangre)
			conductor.save()
			request.method="GET"
			return detallesContratoControl(request,idContrato=idContrato,addDriverSuccess=True)
		else:
			errorIdContrato = False
			try:
				idContrato = request.GET["idContrato"]
			except:
				errorIdContrato = True
				idContrato = ""
			try:
				clienteConductor = request.GET["clienteconductor"]
				if clienteConductor and not errorIdContrato:
					contrato = Contrato.objects.get(idContrato=idContrato)
					cliente = contrato.idVoucher.idCliente
					user = cliente.user
					docIdentidad = cliente.numDocumento
					nombres = user.first_name
					apellidos = user.last_name
			except:
				pass
			return render_to_response('agregarConductor.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def mayor21(fecha):
	diferencia = datetime.now()-fecha
	return diferencia.days/365 >= 21

def alquileresControl (request,pagina=1,addSuccess=False):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			query = {}
			if request.POST["ascDesc"]=="True":
				order = request.POST["orderBy"]
			else:
				order = "-"+request.POST["orderBy"]
			#Tomo datos
			idDatosAlquiler=request.POST["idDatosAlquiler"]
			idContrato=request.POST["idContrato"]
			metodoPago=request.POST["metodoPago"]

			if idDatosAlquiler and re.match("^([1-9]{1,5})$",idDatosAlquiler):
				query["idDatosAlquiler"]=idDatosAlquiler
			if idContrato and re.math("^([1-9]{1,5})$",idContrato):
				query["idContrato"]=idContrato
			if metodoPago:
				query["metodoPago"]=metodoPago

			if query:
				listadodatosalquiler= DatosAlquiler.objects.filter(**query).order_by(order)
				filtrados=True
			else:
				listadodatosalquiler = DatosAlquiler.objects.all().order_by(order)
			listadatosalquiler = paginar(listadodatosalquiler,pagina)
			return render_to_response('alquileres.html',locals(), context_instance = RequestContext(request))
		listadodatosalquiler = DatosAlquiler.objects.all()
		listadatosalquiler=paginar(listadodatosalquiler,pagina)
		return render_to_response('alquileres.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def agregarDatosAlquilerControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			idContrato = request.POST["idContrato"]
			metodoPago = request.POST["metodoPago"]
			tarifaEstablecida = request.POST["tarifaEstablecida"]
			tarifaAplicada = request.POST["tarifaAplicada"]
			fechaAlquiler = request.POST["fechaAlquiler"]
			fechaDevolucion = request.POST["fechaDevolucion"] #que pasa si en el cierre la fecha de devolucion es distinta?
			totalDias = request.POST["totalDias"] #revisar cotizacion
			kmInicial = request.POST["kmInicial"]
			#kmFinal = 10
			#cierre=False
			#if cierre: 
			kmFinal = request.POST["kmFinal"]
			valorAlquiler = request.POST["valorAlquiler"]

			if request.POST["idReserva"]:
				idReserva = request.POST["idReserva"]

			if request.POST["idReserva"]: 
				idReserva = request.POST["idReserva"]
			else:
				idReserva = None

			#manejo de errores
			errorIdContrato=False
			errorIdContratoExists=False
			errorIdReserva=False
			errorIdReservaExists=False
			try:
				contrato = Contrato.objects.get(idContrato=idContrato)
			except:
				errorIdContrato=True
			try:
				if idReserva == None:
					reserva = None
				else:
					reserva = Reserva.objects.get(idReserva=idReserva)
			except:
				errorIdReserva=True
			#evalua si el contrato y/0 la reserva ya se encuentra asociado a otros datos de alquiler
			try:
				DatosAlquiler.objects.get(idContrato=contrato)
				errorIdContratoExists=True
			except:
				pass
			try:
				if idReserva != None: DatosAlquiler.objects.get(idReserva=reserva)
				errorIdReservaExists=True
			except:
				pass


			errorFechas = fechaDevolucion < fechaAlquiler
			errorFechaAlquiler = not fechaCorrecta(fechaAlquiler)
			errorFechaDevolucion = not fechaCorrecta(fechaDevolucion) #incluir que la fecha de devolucion debe ser despues de la de alquiler
			errorKmInicial = not re.match("^([0-9]{1,6})$",kmInicial)
			errorKmFinal = not re.match("^([0-9]{1,6})$",kmFinal)
			errorMetodoPago = (metodoPago not in parametros["metodosPago"])

			if (errorIdContrato or errorIdContratoExists or errorIdReserva or errorFechas or errorFechaAlquiler or errorFechaDevolucion or errorKmInicial or errorKmFinal or errorMetodoPago):
				return render_to_response('agregarDatosAlquiler.html', locals(), context_instance = RequestContext(request))

			datosAlquiler = DatosAlquiler(idContrato=contrato, idReserva=reserva, metodoPago=metodoPago, tarifaEstablecida=tarifaEstablecida, tarifaAplicada=tarifaAplicada, fechaAlquiler=fechaAlquiler, fechaDevolucion=fechaDevolucion, totalDias=totalDias, kmInicial=kmInicial, kmFinal=kmFinal, valorAlquiler=valorAlquiler)
			datosAlquiler.save()
			request.method = 'GET'
			return detallesDatosAlquilerControl(request, idDatosAlquiler=datosAlquiler.idDatosAlquiler, addSuccess=True)
		else:
			try:
				idContrato =  request.GET["idContrato"]
				contrato = Contrato.objects.get(idContrato=idContrato)
			except:
				pass
			metodosPago = parametros["metodosPago"]
			return render_to_response('agregarDatosAlquiler.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def detallesDatosAlquilerControl(request, idDatosAlquiler, addSuccess=False):
	if request.user.is_authenticated() and request.user.is_staff:
		try:
			datosAlquiler = DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			contrato = datosAlquiler.idContrato
			vehiculo = contrato.idVehiculo
		except:
			return HttpResponseRedirect('/alquiler')
		return render_to_response('detallesDatosAlquiler.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def eliminarDatosAlquilerControl(request):
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'POST':
		try:
			idDatosAlquiler = request.POST["idDatosAlquiler"]
			datosAlquiler = DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			datosAlquiler.delete()
		except:
			pass
		return HttpResponseRedirect('/alquiler')
	else:
		return HttpResponseRedirect('/404')
