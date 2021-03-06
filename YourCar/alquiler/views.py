# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from django.contrib.auth import login, authenticate, logout
from YourCar.alquiler.models import Vehiculo, ClienteAlquiler, ClientePotencial, Mantenimiento, Voucher, Reserva, Contrato,ConductorAutorizado, DatosAlquiler, ChecklistVehiculo, Factura, CobroAdicional, Proveedor, Servicio
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
		servicios=Servicio.objects.all()
		#Si me enviaron datos intento guardarlos
		if request.method == 'POST':
			#try:
				#Tomo datos
				placa=request.POST["placa"].upper()
				vehiculo = Vehiculo.objects.get(placa=placa)
				fecha = request.POST["fecha"]
				descripcion = ""
				costo = request.POST["costo"]
				tipo = request.POST["tipo"]
				servicio = request.POST["servicio"]

				#Tomo dato opcional
				if request.POST["descripcion"]:
					descripcion= request.POST["descripcion"]

				#Hago validaciones
				errorPlaca = not Vehiculo.objects.filter(placa=placa) or not re.match("^([A-Z]{3}[0-9]{3})$",placa)
				errorFecha= not fechaCorrecta(fecha)
				errorTipo = tipo not in tipos
				errorCosto = not re.match("^([0-9]{3,10})$",costo)
				errorDescripcion = len(descripcion)>200
				errorServicio = False
				try:
					idServicio = int(servicio.split(".")[0])
					servicioEncontrado = Servicio.objects.get(idServicio=idServicio)
				except:
					errorServicio = True

				#Si hay errores vuelvo al formulario y los informo
				if (errorPlaca or errorFecha or errorTipo or errorCosto or errorDescripcion or errorServicio):
					return render_to_response('agregarHistorialMantenimiento.html',locals(), context_instance = RequestContext(request))

				#Si no hay errores guardo el mantenimiento y vuelvo al historial
				mantenimiento = Mantenimiento(idVehiculo=vehiculo,fecha=fecha, descripcion=descripcion, costo=costo, tipo=tipo, servicio=servicioEncontrado)
				mantenimiento.save()
				exito=True
			#except:
				#pass
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
		try:
			#Tomo datos
			placa=request.POST["placa"].upper()
			fechaIni = request.POST["fechaIni"]
			fechaFin = request.POST["fechaFin"]
			horaIni = request.POST["horaIni"]
			horaFin = request.POST["horaFin"]
			lugarRecogida = request.POST["lugarRecogida"]
			lugarEntrega = request.POST["lugarEntrega"]

			try:
				if request.user.is_authenticated() and not request.user.is_staff:
					email = request.user.email
				elif not request.user.is_authenticated() and request.POST["email"]:
					email = request.POST["email"]
				clientePotencial = ClientePotencial(email=email)
				clientePotencial.save()
			except:
				pass

			is_authenticated=False
			if request.user.is_authenticated(): is_authenticated=True

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
			cotizacion = cotizar(dtIni,dtFin,costoRecogida,costoEntrega,vehiculo.tarifa,vehiculo.limiteKilometraje)
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
		is_authenticated=False
		if request.user.is_authenticated(): is_authenticated=True
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
			errorCilindraje = not re.match("^([0-9]{1,10})$",cilindraje)
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
			if (errorTipoDeFrenos or errorPlaca or errorNumDePasajeros or errorGama or errorAirbags or errorModelo or errorValorGarantia or errorKilometraje or errorCilindraje or errorCajaDeCambios or errorEstado or errorTipoDeDireccion or errorTipoDeTraccion or errorFoto or errorCamposVaciosVeh or errorFechas or errorEnteros or errorLongDatos):
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
			franquicia = request.POST['franquicia']

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
			errorCamposVacios = (len(codigoAutorizacion)==0 or len(numTarjetaCredito)==0 or len(codigoVerifTarjeta)==0 or len(nombreBanco)==0 or len(franquicia)==0)
			errorCamposLargos = len(nombreBanco)>20 or len(franquicia)>20

			if (errorcodigoAutorizacion or erroridCliente or errormontoVoucher or errornumTarjetaCredito or errorcodigoVerifTarjeta or errorFecha or errorCamposVacios or errorCamposLargos):
				return render_to_response('agregarVoucher.html', locals(), context_instance = RequestContext(request))

			#Guardo el voucher
			voucher = Voucher(codigoAutorizacion= codigoAutorizacion,idCliente = cliente,montoVoucher = montoVoucher,numTarjetaCredito = numTarjetaCredito,fechaVencTarjeta = fechaVencTarjeta,codigoVerifTarjeta = codigoVerifTarjeta,nombreBanco = nombreBanco,franquicia = franquicia)
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
			errorHoras = not re.match('[0-9]{2}:[0-9]{2}',horaInicio) or  not re.match('[0-9]{2}:[0-9]{2}',horaFin)
			if not errorFormatoFechas and not errorHoras:
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
			if (errorIdCliente or errorIdVehiculo or errorPagada or errorFormatoFechas or errorFechas or errorLugares or errorHoras):
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
		try:
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
			cotizacion = cotizar(dtIni,dtFin,costoRecogida, costoEntrega, vehiculo.tarifa, vehiculo.limiteKilometraje)
			cotizado=True
			if reserva.fotoPago:
				hayFoto=True
			return render_to_response('detallesReserva.html',locals(), context_instance = RequestContext(request))
		except:
			errorIdReserva=True
			return render_to_response('detallesReserva.html',locals(), context_instance = RequestContext(request))
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
			try:
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
				parametros["nombreEmpresa"] = request.POST["nombreEmpresa"]
				parametros["nitEmpresa"] = request.POST["nitEmpresa"]
				parametros["IVA"] = request.POST["IVA"]
				parametros["costoGalon"] = request.POST["costoGalon"]
				parametros["lavada"] = ast.literal_eval(request.POST["lavada"])
				parametros["servicios"] = ast.literal_eval(request.POST["servicios"])
				exito=True
				param=parametros
				newInfo = "parametros = "+str(parametros).replace(': u"',': "').replace('"(','(').replace(')",','),').replace(')"}',')}')
				paramFile=open('YourCar\\alquiler\parametros2.py','a')
				paramFile.write(newInfo)
				paramFile.close()
				os.remove("YourCar\\alquiler\parametros.py")
				os.rename("YourCar\\alquiler\parametros2.py","YourCar\\alquiler\parametros.py")
			except:
				pass
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
		hora = str((tt[3]+19)%24) #Resto 5 (por el gmt) de manera modular
		if len(hora)==1:
			hora="0"+hora
		mins = str(tt[4])
		if len(mins)==1:
			mins="0"+mins
		return "%s:%s"%(hora,mins)
	except:
		return fecha

def cotizar(dtIni, dtFin,costoRecogida,costoEntrega,tarifaDia,limiteKilometraje,galonesGasolina=0,costoGalon=0,costoLavada=0,porcentajeIVA=0,totalOtrosCobros=0):
	if not costoGalon:
		costoGalon=int(parametros["costoGalon"])
	if not porcentajeIVA:
		porcentajeIVA=int(parametros["IVA"])
	diferencia =  dtFin-dtIni
	diasReal = diferencia.days
	dias = diasReal
	segs  = diferencia.seconds
	horasReal = math.floor(segs/3600)
	horas=int(horasReal)
	mins = (segs%3600)/60
	if mins>=30:
		horas+=1
	if(horas>6):
		dias+=1
		horas=0
	totalPorDias = dias*tarifaDia
	tarifaHora = math.floor(tarifaDia/24)
	totalPorHoras = horas*tarifaHora
	kmPorHora = math.floor(limiteKilometraje/24)
	maxKms = limiteKilometraje*dias+kmPorHora*horas
	totalPorGasolina = galonesGasolina*costoGalon
	total=totalPorDias+totalPorHoras+costoEntrega+costoRecogida+totalPorGasolina+costoLavada+totalOtrosCobros
	iva = total/(1+(porcentajeIVA/100))
	subtotal = total-iva


	#guardo todo en un diccionario y lo retorno (los datos numericos los formateo con comas.)
	cotizacion = {}
	cotizacion["diasReal"]= diasReal
	cotizacion["horasReal"] = horasReal
	cotizacion["dias"] = dias
	cotizacion["horas"] = horas
	cotizacion["tarifaDia"] = tarifaDia
	cotizacion["limiteKilometraje"] = limiteKilometraje
	cotizacion["maxKms"]=maxKms
	cotizacion["costoRecogida"] = intWithCommas(costoRecogida)
	cotizacion["costoEntrega"] = intWithCommas(costoEntrega)
	cotizacion["tarifaHora"] = intWithCommas(tarifaHora)
	cotizacion["tarifaDia"] = intWithCommas(tarifaDia)
	cotizacion["totalPorHoras"] = intWithCommas(totalPorHoras)
	cotizacion["totalPorDias"] = intWithCommas(totalPorDias)
	cotizacion["costoGalon"] = intWithCommas(costoGalon)
	cotizacion["totalPorGasolina"] = intWithCommas(totalPorGasolina)
	cotizacion["costoLavada"] = intWithCommas(costoLavada)
	cotizacion["total"] = intWithCommas(total)
	cotizacion["iva"] = intWithCommas(iva)
	cotizacion["subtotal"] = intWithCommas(subtotal)
	return cotizacion

def contratosControl(request,pagina=1):
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
			conductores = ConductorAutorizado.objects.filter(idContrato=contrato)
			return render_to_response('detallesContrato.html',locals(), context_instance = RequestContext(request))
		except:
			errorIdContrato=True
		return HttpResponseRedirect('/contratos')
	return HttpResponseRedirect('/404')

def agregarContratosControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			idVehiculo = request.POST["idVehiculo"]
			idVoucher = request.POST["idVoucher"]
			fechaInicio = request.POST["fechaInicio"]
			fechaFin = request.POST["fechaFin"]
			horaInicio = request.POST["horaInicio"]
			horaFin = request.POST["horaFin"]

			errorIdCliente = False
			errorIdVoucher = False
			errorIdVehiculo = False
			errorFechas = False
			errorHoras = not re.match('[0-9]{2}:[0-9]{2}',horaInicio) or  not re.match('[0-9]{2}:[0-9]{2}',horaFin)
			errorFormatoFechas = not fechaCorrecta(fechaInicio) or not fechaCorrecta(fechaFin)
			if not errorFormatoFechas and not errorHoras:
				dtIni = datetime.strptime(fechaInicio+" "+horaInicio, '%Y-%m-%d %H:%M')
				dtFin = datetime.strptime(fechaFin+" "+horaFin, '%Y-%m-%d %H:%M')
				#manejo de errores
				errorFechas = dtIni > dtFin or datetime.now()> dtIni
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
			if (errorIdCliente or errorIdVoucher or errorIdVehiculo or errorFormatoFechas or errorFechas or errorHoras):
				return render_to_response('agregarContrato.html', locals(), context_instance = RequestContext(request))

			#Si no, guardo el contrato
			contrato = Contrato(idVehiculo = vehiculo, idVoucher = voucher, fechaInicio = dtIni, fechaFin = dtFin)
			contrato.save()
			request.method="GET"
			return detallesContratoControl(request,idContrato=contrato.idContrato,addSuccess=True)
		else:
			try:
				idVoucher = request.GET["idVoucher"]
			except:
				pass
			return render_to_response('agregarContrato.html',locals(), context_instance = RequestContext(request))
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

def alquileresControl (request,pagina=1):
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
			if idContrato and re.match("^([1-9]{1,5})$",idContrato):
				query["idContrato"]=idContrato
			if metodoPago:
				query["metodoPago__icontains"]=metodoPago

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
	lugaresCostos = parametros["lugaresCostos"]
	lugares = lugaresCostos.keys
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			idContrato = request.POST["idContrato"]
			metodoPago = request.POST["metodoPago"]
			tarifaAplicada = request.POST["tarifaAplicada"]
			fechaAlquiler = request.POST["fechaAlquiler"] 
			horaAlquiler = request.POST["horaAlquiler"]
			fechaDevolucion = request.POST["fechaDevolucion"]
			horaDevolucion = request.POST["horaDevolucion"]
			kmFinal = request.POST["kmFinal"]
			lugarRecogida = request.POST["lugarRecogida"]
			lugarEntrega = request.POST["lugarEntrega"]
			modificarDatosAlquiler=""
			idDatosAlquiler=0

			if request.POST["idReserva"]: 
				idReserva = request.POST["idReserva"]
			else:
				idReserva = None

			#en caso de que sea una modificacion
			try:
				modificarDatosAlquiler=request.POST["modificarDatosAlquiler"]
				idDatosAlquiler=request.POST["idDatosAlquiler"]
			except:
				pass

			#manejo de errores
			errorIdContrato=False
			errorIdContratoExists=False
			errorIdReserva=False
			errorIdReservaExists=False
			errorContratoReserva=False
			try:
				contrato = Contrato.objects.get(idContrato=idContrato)
			except:
				errorIdContrato=True

			kmInicial = contrato.idVehiculo.kilometraje
			tarifaEstablecida = contrato.idVehiculo.tarifa
			try:
				if idReserva == None:
					reserva = None
				else:
					reserva = Reserva.objects.get(idReserva=idReserva)
			except:
				errorIdReserva=True
			if not errorIdReserva and reserva != None:
				if ((contrato.idVehiculo != reserva.idVehiculo) and (contrato.fechaInicio != reserva.fechaInicio) and (contrato.fechaFin != reserva.fechaFin)):
					errorContratoReserva=True

			#evalua si el contrato y/0 la reserva ya se encuentra asociado a otros datos de alquiler
			try:
				DatosAlquiler.objects.get(idContrato=contrato)
				if not modificarDatosAlquiler: errorIdContratoExists=True
			except:
				pass
			try:
				r=DatosAlquiler.objects.get(idReserva=reserva)
			except:
				r=None
			if reserva != None and r: 
				errorIdReservaExists=True

			errorLugares=False
			try:
				costoRecogida=int(lugaresCostos[lugarRecogida])
				costoEntrega=int(lugaresCostos[lugarEntrega])
			except:
				errorLugares = True
			errorKmInicial = not (kmInicial >= 0 and kmInicial <= 999999)
			errorKmFinal = not re.match("^([0-9]{1,6})$",kmFinal)
			errorKm = kmInicial > int(kmFinal)
			errorMetodoPago = (metodoPago not in parametros["metodosPago"])
			errorFormatoFechas = not fechaCorrecta(fechaAlquiler) or not fechaCorrecta(fechaDevolucion)
			errorHoras = not re.match('[0-9]{2}:[0-9]{2}',horaAlquiler) or  not re.match('[0-9]{2}:[0-9]{2}',horaDevolucion)
			if not errorFormatoFechas and not errorHoras:
				fechaAlq = datetime.strptime(fechaAlquiler+" "+horaAlquiler, '%Y-%m-%d %H:%M')
				fechaDev = datetime.strptime(fechaDevolucion+" "+horaDevolucion, '%Y-%m-%d %H:%M')
				errorFechas = fechaAlq > fechaDev or datetime.now() > fechaAlq
			diferencia = fechaDev-fechaAlq
			diasReal = diferencia.days
			dias = diasReal
			totalDias=dias

			if (errorIdContrato or errorIdContratoExists or errorIdReserva or errorIdReservaExists or errorContratoReserva or errorFechas or errorFormatoFechas or errorHoras or errorKmInicial or errorKmFinal or errorKm or errorMetodoPago or errorLugares):
				return render_to_response('agregarDatosAlquiler.html', locals(), context_instance = RequestContext(request))

			if modificarDatosAlquiler:
				datosAlquiler = DatosAlquiler(idDatosAlquiler=idDatosAlquiler,idContrato=contrato, idReserva=reserva, metodoPago=metodoPago, tarifaEstablecida=tarifaEstablecida, tarifaAplicada=tarifaAplicada, fechaAlquiler=fechaAlq, fechaDevolucion=fechaDev, totalDias=totalDias, kmInicial=kmInicial, kmFinal=kmFinal, lugarRecogida=lugarRecogida, lugarEntrega=lugarEntrega, cierre=False)
			else:
				datosAlquiler = DatosAlquiler(idContrato=contrato, idReserva=reserva, metodoPago=metodoPago, tarifaEstablecida=tarifaEstablecida, tarifaAplicada=tarifaAplicada, fechaAlquiler=fechaAlq, fechaDevolucion=fechaDev, totalDias=totalDias, kmInicial=kmInicial, kmFinal=kmFinal, lugarRecogida=lugarRecogida, lugarEntrega=lugarEntrega, cierre=False)
			datosAlquiler.save()
			request.method = 'GET'
			if not modificarDatosAlquiler:
				return detallesDatosAlquilerControl(request, idDatosAlquiler=datosAlquiler.idDatosAlquiler, addSuccess=1)
			else:
				return detallesDatosAlquilerControl(request, idDatosAlquiler=datosAlquiler.idDatosAlquiler, addSuccess=2)
		else:
			try:
				idContrato =  request.GET["idContrato"]
				contrato = Contrato.objects.get(idContrato=idContrato)
				tarifaEstablecida = contrato.idVehiculo.tarifa
				kmInicial = contrato.idVehiculo.kilometraje
				fechaAlquiler = formatearFecha(contrato.fechaInicio)
				horaAlquiler = formatearHora(contrato.fechaInicio)
				fechaDevolucion = formatearFecha(contrato.fechaFin)
				horaDevolucion = formatearHora(contrato.fechaFin)
				strFecha = str(contrato.fechaInicio)
			except:
				pass
			try:
				idReserva = request.GET["idReserva"]
				reserva = Reserva.objects.get(idReserva=idReserva)
				tarifaEstablecida = reserva.idVehiculo.tarifa
				kmInicial = reserva.idVehiculo.kilometraje
				fechaAlquiler = formatearFecha(reserva.fechaInicio)
				horaAlquiler = formatearHora(reserva.fechaInicio)
				fechaDevolucion = formatearFecha(reserva.fechaFin)
				horaDevolucion = formatearHora(reserva.fechaFin)
				lugarRecogida=reserva.lugarRecogida
				lugarEntrega=reserva.lugarEntrega
			except:
				pass

			metodosPago = parametros["metodosPago"]
			return render_to_response('agregarDatosAlquiler.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def modificarDatosAlquilerControl(request):
	lugaresCostos = parametros["lugaresCostos"]
	lugares = lugaresCostos.keys
	if request.user.is_authenticated() and request.user.is_staff and request.method == 'GET':
		idDatosAlquiler = request.GET["idDatosAlquiler"]
		try:
			datosAlquiler=DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
		except:
			return HttpResponseRedirect('/alquiler')
		idContrato = datosAlquiler.idContrato.idContrato
		if datosAlquiler.idReserva != None:
			idReserva = datosAlquiler.idReserva.idReserva
		else:
			idReserva=None
		metodosPago=parametros["metodosPago"]
		metodoPago = datosAlquiler.metodoPago
		tarifaEstablecida = datosAlquiler.tarifaEstablecida
		tarifaAplicada = datosAlquiler.tarifaAplicada
		fechaAlquiler=formatearFecha(datosAlquiler.fechaAlquiler)
		horaAlquiler=formatearHora(datosAlquiler.fechaAlquiler)
		fechaDevolucion=formatearFecha(datosAlquiler.fechaDevolucion)
		horaDevolucion=formatearHora(datosAlquiler.fechaDevolucion)
		kmInicial =datosAlquiler.kmInicial
		kmFinal = datosAlquiler.kmFinal
		lugarRecogida=datosAlquiler.lugarRecogida
		lugarEntrega=datosAlquiler.lugarEntrega
		return render_to_response('modificarDatosAlquiler.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def detallesDatosAlquilerControl(request, idDatosAlquiler, addSuccess=0):
	if request.user.is_authenticated() and request.user.is_staff:
		try:
			datosAlquiler = DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			contrato = datosAlquiler.idContrato
			vehiculo = contrato.idVehiculo
		except:
			return HttpResponseRedirect('/alquiler')

		checklistSalidaVehiculo=None
		checklistRetornoVehiculo=None
		checklist1=None
		checklist2=None
		try:
			checklistSalidaVehiculo = ChecklistVehiculo.objects.get(idDatosAlquiler=datosAlquiler, cierre=False)
			checklistSalidaExists=True
		except:
			checklistSalidaExists=False
		try:
			checklistRetornoVehiculo = ChecklistVehiculo.objects.get(idDatosAlquiler=datosAlquiler, cierre=True)
			checklistRetornoExists=True
		except:
			checklistRetornoExists=False

		try:
			checklist1=model_to_dict(checklistSalidaVehiculo, exclude=["idChecklistVehiculo", "idDatosAlquiler", "cierre"])
			checklist2=model_to_dict(checklistRetornoVehiculo, exclude=["idChecklistVehiculo", "idDatosAlquiler", "cierre"])
			keys=checklist1.keys()
		except:
			pass

		registro=[]
		if checklist1 and checklist2:
			for k in keys:
				if checklist1[k] != checklist2[k]:
					if checklist1[k] == 1: 
						s="Si"
					elif checklist1[k] == 0:
						s="No"
					if checklist2[k] == 1: 
						r="Si"
					elif checklist2[k] == 0:
						r="No"
					reg="Salida: "+s+" Retorno: "+r
				else:
					reg="Sin cambios "
				registro.append(reg)

		return render_to_response('detallesDatosAlquiler.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def cierreDatosAlquilerControl(request):
	lugaresCostos = parametros["lugaresCostos"]
	lugares = lugaresCostos.keys
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			idDatosAlquiler = request.POST["idDatosAlquiler"]
			idContrato = request.POST["idContrato"]
			metodoPago = request.POST["metodoPago"] #c
			tarifaEstablecida = request.POST["tarifaEstablecida"]
			tarifaAplicada = request.POST["tarifaAplicada"] #c
			fechaAlquiler = request.POST["fechaAlquiler"] #c
			horaAlquiler = request.POST["horaAlquiler"] #c
			fechaDevolucion = request.POST["fechaDevolucion"] #c
			horaDevolucion = request.POST["horaDevolucion"] #c
			kmInicial = request.POST["kmInicial"]
			kmFinal = request.POST["kmFinal"] #c
			lugarRecogida=request.POST["lugarRecogida"]
			lugarEntrega=request.POST["lugarEntrega"]

			if request.POST["idReserva"]: 
				idReserva = request.POST["idReserva"]
			else:
				idReserva = None

			try:
				contrato = Contrato.objects.get(idContrato=idContrato)
			except:
				pass
			try:
				if idReserva == None:
					reserva = None
				else:
					reserva = Reserva.objects.get(idReserva=idReserva)
			except:
				pass

			errorLugares=False
			try:
				costoRecogida=int(lugaresCostos[lugarRecogida])
				costoEntrega=int(lugaresCostos[lugarEntrega])
			except:
				errorLugares = True
			errorKmInicial = not re.match("^([0-9]{1,6})$",kmInicial)
			errorKmFinal = not re.match("^([0-9]{1,6})$",kmFinal)
			errorMetodoPago = (metodoPago not in parametros["metodosPago"])
			errorFormatoFechas = not fechaCorrecta(fechaAlquiler) or not fechaCorrecta(fechaDevolucion)
			errorHoras = not re.match('[0-9]{2}:[0-9]{2}',horaAlquiler) or  not re.match('[0-9]{2}:[0-9]{2}',horaDevolucion)
			if not errorFormatoFechas and not errorHoras:
				fechaAlq = datetime.strptime(fechaAlquiler+" "+horaAlquiler, '%Y-%m-%d %H:%M')
				fechaDev = datetime.strptime(fechaDevolucion+" "+horaDevolucion, '%Y-%m-%d %H:%M')
				errorFechas = fechaAlq > fechaDev or datetime.now() > fechaAlq
			diferencia = fechaDev-fechaAlq
			diasReal = diferencia.days
			dias = diasReal
			totalDias=dias
			valorAlquiler=0

			if (errorFechas or errorFormatoFechas or errorHoras or errorKmInicial or errorKmFinal or errorMetodoPago or errorLugares):
				return render_to_response('cierreDatosAlquiler.html', locals(), context_instance = RequestContext(request))

			datosAlquiler = DatosAlquiler(idDatosAlquiler=idDatosAlquiler, idContrato=contrato, idReserva=reserva, metodoPago=metodoPago, tarifaEstablecida=tarifaEstablecida, tarifaAplicada=tarifaAplicada, fechaAlquiler=fechaAlq, fechaDevolucion=fechaDev, totalDias=totalDias, kmInicial=kmInicial, kmFinal=kmFinal, lugarRecogida=lugarRecogida, lugarEntrega=lugarEntrega, cierre=True)
			datosAlquiler.save()
			vehiculo = Vehiculo(placa = contrato.idVehiculo.placa, marca = contrato.idVehiculo.marca, referencia = contrato.idVehiculo.referencia, gama = contrato.idVehiculo.gama, descripcionBasica = contrato.idVehiculo.descripcionBasica, numDePasajeros = contrato.idVehiculo.numDePasajeros, cilindraje = contrato.idVehiculo.cilindraje, color = contrato.idVehiculo.color, cajaDeCambios = contrato.idVehiculo.cajaDeCambios, limiteKilometraje = contrato.idVehiculo.limiteKilometraje, tarifa = contrato.idVehiculo.tarifa, estado = contrato.idVehiculo.estado, fechaVencSOAT = contrato.idVehiculo.fechaVencSOAT, fechaVencSeguroTodoRiesgo = contrato.idVehiculo.fechaVencSeguroTodoRiesgo, fechaVencRevisionTecMec = contrato.idVehiculo.fechaVencRevisionTecMec, fechaVencCambioAceite = contrato.idVehiculo.fechaVencCambioAceite, tipoDeFrenos = contrato.idVehiculo.tipoDeFrenos, airbags = contrato.idVehiculo.airbags, tipoDeDireccion = contrato.idVehiculo.tipoDeDireccion, tipoDeTraccion = contrato.idVehiculo.tipoDeTraccion, modelo = contrato.idVehiculo.modelo, valorGarantia = contrato.idVehiculo.valorGarantia, kilometraje = kmFinal, foto=contrato.idVehiculo.foto)
			vehiculo.save()
			request.method = 'GET'
			return checklistVehiculoControl(request, idDatosAlquilerCerrando=idDatosAlquiler)
		else:
			try:
				idDatosAlquiler=request.GET["idDatosAlquiler"]
				datosAlquiler=DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			except:
				pass
			idContrato=datosAlquiler.idContrato.idContrato
			if datosAlquiler.idReserva != None:
				idReserva = datosAlquiler.idReserva.idReserva
			else:
				idReserva = None
			metodosPago=parametros["metodosPago"]
			metodoPago=datosAlquiler.metodoPago
			tarifaEstablecida=datosAlquiler.tarifaEstablecida
			tarifaAplicada=datosAlquiler.tarifaAplicada
			fechaAlquiler=formatearFecha(datosAlquiler.fechaAlquiler)
			horaAlquiler=formatearHora(datosAlquiler.fechaAlquiler)
			fechaDevolucion=formatearFecha(datosAlquiler.fechaDevolucion)
			horaDevolucion=formatearHora(datosAlquiler.fechaDevolucion)
			kmInicial=datosAlquiler.kmInicial
			kmFinal=datosAlquiler.kmFinal
			lugarRecogida=datosAlquiler.lugarRecogida
			lugarEntrega=datosAlquiler.lugarEntrega
			return render_to_response('cierreDatosAlquiler.html', locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def checklistVehiculoControl(request, idDatosAlquilerCerrando=0):
	if request.user.is_authenticated and request.user.is_staff:
		if request.method == 'POST':
			idDatosAlquiler = request.POST["idDatosAlquiler"]
			documentosDelAuto = request.POST["documentosDelAuto"]
			radio = request.POST["radio"]
			tapetes = request.POST["tapetes"]
			llantaDeRepuesto = request.POST["llantaDeRepuesto"]
			gato = request.POST["gato"]
			cruceta = request.POST["cruceta"]
			nivelAceiteDelMotorFrenos = request.POST["nivelAceiteDelMotorFrenos"]
			nivelRefrigerante = request.POST["nivelRefrigerante"]
			latoneriaYPintura = request.POST["latoneriaYPintura"]
			tapizado = request.POST["tapizado"]
			cinturonesDeSeguridad = request.POST["cinturonesDeSeguridad"]
			controlesInternos = request.POST["controlesInternos"]
			instrumentosDelPanel = request.POST["instrumentosDelPanel"]
			pito = request.POST["pito"]
			relojConHoraCorrecta = request.POST["relojConHoraCorrecta"]
			limpiabrisas = request.POST["limpiabrisas"]
			liquidoDeLimpiabrisas = request.POST["liquidoDeLimpiabrisas"]
			seguroCentral = request.POST["seguroCentral"]
			elevaVidrios = request.POST["elevaVidrios"]
			aireAcondicionado = request.POST["aireAcondicionado"]
			cojineria = request.POST["cojineria"]
			lucesInternas = request.POST["lucesInternas"]
			lucesMediasDelanterasYTraseras = request.POST["lucesMediasDelanterasYTraseras"]
			lucesAltasYBajas = request.POST["lucesAltasYBajas"]
			direccionalesDelantesYTraseras = request.POST["direccionalesDelantesYTraseras"]
			luzDeFreno = request.POST["luzDeFreno"]
			luzDeReversa = request.POST["luzDeReversa"]
			antenaDeRadio = request.POST["antenaDeRadio"]
			rines = request.POST["rines"]
			farolasYStops = request.POST["farolasYStops"]
			exploradoras = request.POST["exploradoras"]
			retrovisores = request.POST["retrovisores"]
			cristalesVidrios = request.POST["cristalesVidrios"]
			chapas = request.POST["chapas"]
			llaves = request.POST["llaves"]
			kitCarretera = request.POST["kitCarretera"]
			
			try:
				datosAlquiler=DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			except:
				errorIdDatosAlquiler = True

			#manejo errores
			errorChecklistExists=False
			checklist1=None
			checklist2=None
			try:
				checklist1 = ChecklistVehiculo.objects.get(idDatosAlquiler=datosAlquiler, cierre=False)
				checklist2 = ChecklistVehiculo.objects.get(idDatosAlquiler=datosAlquiler, cierre=True)
			except:
				pass

			if ((checklist1 and checklist2) or (checklist1 and not datosAlquiler.cierre) or (checklist2 and datosAlquiler.cierre)):
				errorChecklistExists=True

			if (errorChecklistExists):
				return render_to_response('checklistVehiculo.html', locals(), context_instance = RequestContext(request))

			#checklistVehiculo=ChecklistVehiculo(idDatosAlquiler=datosAlquiler, cierre=datosAlquiler.cierre, documentosDelAuto=documentosDelAuto)
			checklistVehiculo=ChecklistVehiculo(idDatosAlquiler=datosAlquiler, cierre=datosAlquiler.cierre, documentosDelAuto=documentosDelAuto, radio=radio, tapetes=tapetes, llantaDeRepuesto=llantaDeRepuesto, gato=gato, cruceta=cruceta, nivelAceiteDelMotorFrenos=nivelAceiteDelMotorFrenos, nivelRefrigerante=nivelRefrigerante, latoneriaYPintura=latoneriaYPintura, tapizado=tapizado, cinturonesDeSeguridad=cinturonesDeSeguridad, controlesInternos=controlesInternos, instrumentosDelPanel=instrumentosDelPanel, pito=pito, relojConHoraCorrecta=relojConHoraCorrecta, limpiabrisas=limpiabrisas, liquidoDeLimpiabrisas=liquidoDeLimpiabrisas, seguroCentral=seguroCentral, elevaVidrios=elevaVidrios, aireAcondicionado=aireAcondicionado, cojineria=cojineria, lucesInternas=lucesInternas, lucesMediasDelanterasYTraseras=lucesMediasDelanterasYTraseras, lucesAltasYBajas=lucesAltasYBajas, direccionalesDelantesYTraseras=direccionalesDelantesYTraseras, luzDeFreno=luzDeFreno, luzDeReversa=luzDeReversa, antenaDeRadio=antenaDeRadio, rines=rines, farolasYStops=farolasYStops, exploradoras=exploradoras, retrovisores=retrovisores, cristalesVidrios=cristalesVidrios, chapas=chapas, llaves=llaves, kitCarretera=kitCarretera)
			checklistVehiculo.save()
			request.method = 'GET'
			return detallesDatosAlquilerControl(request, idDatosAlquiler=datosAlquiler.idDatosAlquiler, addSuccess=3)
		else:
			if idDatosAlquilerCerrando != 0:
				idDatosAlquiler=idDatosAlquilerCerrando
				cierre=True
			else:
				idDatosAlquiler=request.GET["idDatosAlquiler"]
				cierre=False
			try:
				datosAlquiler=DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			except:
				pass

			errorCierre=False
			if cierre != datosAlquiler.cierre:
				errorCierre=True
			if cierre:
				try:
					checklistVehiculo=ChecklistVehiculo.objects.get(idDatosAlquiler=datosAlquiler)
					documentosDelAuto=checklistVehiculo.documentosDelAuto
					radio=checklistVehiculo.radio
					tapetes=checklistVehiculo.tapetes
					llantaDeRepuesto=checklistVehiculo.llantaDeRepuesto
					gato=checklistVehiculo.gato
					cruceta=checklistVehiculo.cruceta
					nivelAceiteDelMotorFrenos=checklistVehiculo.nivelAceiteDelMotorFrenos
					nivelRefrigerante=checklistVehiculo.nivelRefrigerante
					latoneriaYPintura=checklistVehiculo.latoneriaYPintura
					tapizado=checklistVehiculo.tapizado
					cinturonesDeSeguridad=checklistVehiculo.cinturonesDeSeguridad
					controlesInternos=checklistVehiculo.controlesInternos
					instrumentosDelPanel=checklistVehiculo.instrumentosDelPanel
					pito=checklistVehiculo.pito
					relojConHoraCorrecta=checklistVehiculo.relojConHoraCorrecta
					limpiabrisas=checklistVehiculo.limpiabrisas
					liquidoDeLimpiabrisas=checklistVehiculo.liquidoDeLimpiabrisas
					seguroCentral=checklistVehiculo.seguroCentral
					elevaVidrios=checklistVehiculo.elevaVidrios
					aireAcondicionado=checklistVehiculo.aireAcondicionado
					cojineria=checklistVehiculo.cojineria
					lucesInternas=checklistVehiculo.lucesInternas
					lucesMediasDelanterasYTraseras=checklistVehiculo.lucesMediasDelanterasYTraseras
					lucesAltasYBajas=checklistVehiculo.lucesAltasYBajas
					direccionalesDelantesYTraseras=checklistVehiculo.direccionalesDelantesYTraseras
					luzDeFreno=checklistVehiculo.luzDeFreno
					luzDeReversa=checklistVehiculo.luzDeReversa
					antenaDeRadio=checklistVehiculo.antenaDeRadio
					rines=checklistVehiculo.rines
					farolasYStops=checklistVehiculo.farolasYStops
					exploradoras=checklistVehiculo.exploradoras
					retrovisores=checklistVehiculo.retrovisores
					cristalesVidrios=checklistVehiculo.cristalesVidrios
					chapas=checklistVehiculo.chapas
					llaves=checklistVehiculo.llaves
					kitCarretera=checklistVehiculo.kitCarretera
				except:
					pass
			return render_to_response('checklistVehiculo.html', locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def listaClientesPasadosControl(request, pagina=1):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method=="POST":
			query = {}
			if request.POST["ascDesc"]=="True":
				order = request.POST["orderBy"]
			else:
				order = "-"+request.POST["orderBy"]
			listaFacturas = Factura.objects.all().order_by(order)
			clientesPasados=paginar(listaFacturas,pagina)
			return render_to_response('listaClientesPasados.html',locals(), context_instance = RequestContext(request))
		listaFacturas = Factura.objects.all()
		clientesPasados=paginar(listaFacturas,pagina)
		return render_to_response('listaClientesPasados.html',locals(), context_instance = RequestContext(request))
		return HttpResponseRedirect('/404')

def listaClientesPotencialesControl(request, pagina=1):
	if request.user.is_authenticated() and request.user.is_staff:
		#listaClientesPotenciales = ClientePotencial.objects.all()
		listaClientesPotenciales = ClientePotencial.objects.values('email').distinct()
		clientesPotenciales=paginar(listaClientesPotenciales,pagina)
		return render_to_response('listaClientesPotenciales.html',locals(), context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/404')

def facturasControl(request,pagina=1):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method=="POST":
			query = {}
			if request.POST["ascDesc"]=="True":
				order = request.POST["orderBy"]
			else:
				order = "-"+request.POST["orderBy"]
			#Tomo los datos
			numFactura=request.POST["numFactura"]
			#Los datos que no son vacios los agrego al query
			if numFactura:
				query["numFactura"]=numFactura
			#Si la consulta no es vacia la hago
			if query:
				listaFacturas= Factura.objects.filter(**query).order_by(order)
				filtrados=True
			else:
				listaFacturas = Factura.objects.all().order_by(order)
			facturas=paginar(listaFacturas,pagina)
			return render_to_response('facturas.html',locals(), context_instance = RequestContext(request))
		#sino es un post cargo todos
		listaFacturas = Factura.objects.all()
		facturas=paginar(listaFacturas,pagina)
		return render_to_response('facturas.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def detallesFacturaControl(request,numFactura, addSuccess=False,addCobroSuccess=False):
	if request.user.is_authenticated() and request.user.is_staff:
		nit = parametros["nitEmpresa"]
		servicios=parametros["servicios"]
		errorNumFactura=False
		try:
			factura = Factura.objects.get(numFactura=numFactura)
		except:
			errorNumFactura=True
		if not errorNumFactura:
			datosAlquiler = factura.idDatosAlquiler
			contrato = datosAlquiler.idContrato
			voucher = contrato.idVoucher
			cliente = voucher.idCliente
			user = cliente.user
			vehiculo = contrato.idVehiculo
			conductores = ConductorAutorizado.objects.filter(idContrato=contrato)
			cobrosAdicionales =CobroAdicional.objects.filter(numFactura=numFactura)
			totalOtrosCobros = 0
			for c in cobrosAdicionales:
				totalOtrosCobros+= int(c.total)
			cotizacion = cotizar(datosAlquiler.fechaAlquiler,datosAlquiler.fechaDevolucion,factura.costoRecogida, factura.costoEntrega, factura.tarifa, factura.limiteKilometraje,factura.galonesGasolina,factura.costoGalon,factura.costoLavada,factura.porcentajeIVA,totalOtrosCobros)
			if factura.galonesGasolina and factura.costoGalon:
				cobrarGasolina = True
			if factura.costoLavada:
				cobrarLavada = True
			if factura.costoRecogida:
				cobrarRecogida = True
			if factura.costoEntrega:
				cobrarEntrega = True
			return render_to_response('detallesFactura.html',locals(), context_instance = RequestContext(request))
		return HttpResponseRedirect('/facturas')
	return HttpResponseRedirect('/404')

def agregarFacturaControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		lavada = parametros["lavada"]
		costoGalon = parametros["costoGalon"]
		lugaresCostos = parametros["lugaresCostos"]
		lugares = lugaresCostos.keys
		if request.method == 'POST':
			idDatosAlquiler = request.POST["idDatosAlquiler"]
			fecha = request.POST["fecha"]
			tarifa = request.POST["tarifa"]
			limiteKilometraje = request.POST["limiteKilometraje"]
			galonesGasolina = request.POST["galonesGasolina"]
			costoGalon = request.POST["costoGalon"]
			tamanyoLavada = request.POST["tamanyoLavada"]
			lugarRecogida = request.POST["lugarRecogida"]
			lugarEntrega = request.POST["lugarEntrega"]
			costoLavada = 0
			porcentajeIVA = parametros["IVA"]
			errorDatosAlquiler = False
			errorTamanyoLavada = False
			errorLugares = False
			errorContrato = False
			errorVehiculo = False
			errorVoucher = False
			errorCliente = False
			errorFecha = not fechaCorrecta(fecha)
			errorNumeros = not re.match("^([0-9]{1,9})$",tarifa) or not re.match("^([0-9]{1,9})$",limiteKilometraje) or not re.match("^([0-9]{1,9})$",galonesGasolina) or not re.match("^([0-9]{1,9})$",costoGalon)
			try:
				costoLavada = int(lavada[tamanyoLavada])
			except:
				errorTamanyoLavada = True
			try:
				costoRecogida = int(lugaresCostos[lugarRecogida])
			except:
				errorLugares = True
			try:
				costoEntrega = int(lugaresCostos[lugarEntrega])
			except:
				errorLugares = True
			try:
				datosAlquiler = DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
			except:
				errorDatosAlquiler = True
			try:
				contrato= datosAlquiler.idContrato
			except:
				errorContrato = True
			try:
				vehiculo=contrato.idVehiculo
			except:
				errorVehiculo = True
			try:
				voucher=contrato.idVoucher
			except:
				errorVoucher = True
			try:
				cliente= voucher.idCliente
			except:
				errorCliente = True
			#Si hay errores retorno a la pagina
			if (errorDatosAlquiler or errorContrato or errorVehiculo or errorVoucher or errorCliente or errorFecha or errorNumeros or errorTamanyoLavada or errorLugares):
				return render_to_response('agregarFactura.html', locals(), context_instance = RequestContext(request))

			#Si no, guardo la factura
			factura = Factura(idDatosAlquiler = datosAlquiler, fecha = fecha, tarifa = tarifa, limiteKilometraje = limiteKilometraje, galonesGasolina = galonesGasolina, costoGalon = costoGalon, costoRecogida = costoRecogida, costoEntrega = costoEntrega, costoLavada = costoLavada, porcentajeIVA = porcentajeIVA)
			factura.save()
			request.method="GET"
			return detallesFacturaControl(request,numFactura=factura.numFactura,addSuccess=True)
		else:
			try:
				idDatosAlquiler = request.GET["idDatosAlquiler"]
			except:
				pass
			try:
				datosAlquiler = DatosAlquiler.objects.get(idDatosAlquiler=idDatosAlquiler)
				tarifa = datosAlquiler.tarifaAplicada
				lugarRecogida = datosAlquiler.lugarRecogida
				lugarEntrega = datosAlquiler.lugarEntrega
			except:
				errorDatosAlquiler = True
			try:
				contrato= datosAlquiler.idContrato
			except:
				errorContrato = True
			try:
				vehiculo=contrato.idVehiculo
				limiteKilometraje = vehiculo.limiteKilometraje
			except:
				errorVehiculo = True
			try:
				voucher=contrato.idVoucher
			except:
				errorVoucher = True
			try:
				cliente= voucher.idCliente
			except:
				errorCliente = True
			return render_to_response('agregarFactura.html', locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def agregarCobroControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		servicios=parametros["servicios"]
		if request.method == 'POST':
			numFactura = request.POST["numFactura"]
			servicio = request.POST["servicio"]
			descripcion = request.POST["descripcion"]
			costoUnidad = request.POST["costoUnidad"]
			cantidad = request.POST["cantidad"]

			#Posibles errores
			errorNumFactura = False
			errorServicio = False
			errorNumeros = not re.match("^([0-9]{1,9})$",costoUnidad) or not re.match("^([0-9]{1,9})$",cantidad)
			errorDescripcion = len(descripcion)>200
			try:
				servicios[servicio]
			except:
				errorServicio = True
			try:
				factura = Factura.objects.get(numFactura = numFactura)
			except:
				errorNumFactura = True
			#Si hay errores retorno a la pagina
			if (errorNumFactura or errorServicio or errorNumeros or errorDescripcion):
				return render_to_response('agregarCobro.html', locals(), context_instance = RequestContext(request))

			#Si no, guardo el cobro
			total = int(costoUnidad)*int(cantidad)
			idServicio = int(servicios[servicio])
			cobroAdicional = CobroAdicional(numFactura = factura, idServicio = idServicio, servicio = servicio, descripcion = descripcion, costoUnidad = costoUnidad, cantidad = cantidad, total = total)
			cobroAdicional.save()
			request.method="GET"
			return detallesFacturaControl(request,numFactura=numFactura,addCobroSuccess=True)
		else:
			errorNumFactura = False
			try:
				numFactura = request.GET["numFactura"]
			except:
				errorNumFactura = True
			return render_to_response('agregarCobro.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def proveedoresControl(request,pagina=1):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method=="POST":
			query = {}
			if request.POST["ascDesc"]=="True":
				order = request.POST["orderBy"]
			else:
				order = "-"+request.POST["orderBy"]
			#Tomo los datos
			idProveedor=request.POST["idProveedor"]
			nombre=request.POST["nombre"]
			#Los datos que no son vacios los agrego al query
			if idProveedor:
				query["idProveedor"]=idProveedor
			if nombre:
				query["nombre__icontains"]=nombre
			#Si la consulta no es vacia la hago
			if query:
				listaProveedores= Proveedor.objects.filter(**query).order_by(order)
				filtrados=True
			else:
				listaProveedores = Proveedor.objects.all().order_by(order)
		else:
			listaProveedores = Proveedor.objects.all()
		proveedores=paginar(listaProveedores,pagina)
		return render_to_response('proveedores.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def detallesProveedorControl(request,idProveedor, addSuccess=False,addServicioSuccess=False):
	if request.user.is_authenticated() and request.user.is_staff:
		errorIdProveedor=False
		try:
			proveedor = Proveedor.objects.get(idProveedor=idProveedor)
		except:
			errorIdProveedor=True
		if not errorIdProveedor:
			servicios = Servicio.objects.filter(idProveedor=proveedor)
			return render_to_response('detallesProveedor.html',locals(), context_instance = RequestContext(request))
		return HttpResponseRedirect('/proveedores')
	return HttpResponseRedirect('/404')

def agregarProveedorControl(request):
	if request.user.is_authenticated() and request.user.is_staff:
		if request.method == 'POST':
			nombre = request.POST["nombre"]
			descripcion = request.POST["descripcion"]
			nombrePersonaContacto = request.POST["nombrePersonaContacto"]
			telCelular = request.POST["telCelular"]
			telFijo = request.POST["telFijo"]
			calificacion = request.POST["calificacion"]
			tipo = request.POST["tipo"]
			idProveedor=""
			if tipo=="modificar":
				modificar=True
				idProveedor = request.POST["idProveedor"]

			errorDatosVacios = len(nombre)==0 or len(descripcion)==0
			errorDatosLargos = len(nombre)>20 or len(descripcion)>200 or len(nombrePersonaContacto)>20
			errorTels = not re.match("^([0-9]{7,12})$",telFijo) or (len(telCelular)>1 and not re.match("^([0-9]{10,12})$",telCelular))
			errorCalificacion = not re.match("^[0-5]$",calificacion)

			if (errorDatosVacios or errorDatosLargos or errorTels or errorCalificacion):
				return render_to_response('agregarProveedor.html', locals(), context_instance = RequestContext(request))
			if tipo=="agregar":
				proveedor = Proveedor(nombre = nombre,descripcion = descripcion,nombrePersonaContacto = nombrePersonaContacto,telCelular = telCelular,telFijo = telFijo,calificacion = calificacion)
				proveedor.save()
			elif tipo=="modificar":
				proveedor = Proveedor(idProveedor = idProveedor, nombre = nombre,descripcion = descripcion,nombrePersonaContacto = nombrePersonaContacto,telCelular = telCelular,telFijo = telFijo,calificacion = calificacion)
				proveedor.save()
			return detallesProveedorControl(request,idProveedor=proveedor.idProveedor,addSuccess=True)

		else:
			errorIdProveedor = False
			try:
				tipo = request.GET["tipo"]
			except:
				tipo = ""
			if tipo=="modificar":
				modificar=True
				idProveedor = request.GET["idProveedor"]
				try:
					proveedor = Proveedor.objects.get(idProveedor=idProveedor)
				except:
					errorIdProveedor=True
				if not errorIdProveedor:
					nombre = proveedor.nombre
					descripcion = proveedor.descripcion
					nombrePersonaContacto = proveedor.nombrePersonaContacto
					telCelular = proveedor.telCelular
					telFijo = proveedor.telFijo
					calificacion = proveedor.calificacion
			return render_to_response('agregarProveedor.html', locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')

def agregarServicio(request):
	if request.user.is_authenticated() and request.user.is_staff:
		errorIdProveedor = False
		if request.method == 'POST':
			idProveedor = request.POST["idProveedor"]
			servicio = request.POST["servicio"]
			costo = request.POST["costo"]
			#Posibles errores
			errorServicio = len(servicio)==0 or len(servicio)>20
			errorCosto = not re.match("^[0-9]{3,10}$",costo)
			try:
				proveedor = Proveedor.objects.get(idProveedor=idProveedor)
			except:
				errorIdProveedor = True
			#Si hay errores retorno a la vista
			if (errorServicio or errorCosto or errorIdProveedor):
				return render_to_response('agregarServicio.html', locals(), context_instance = RequestContext(request))
			#Si no, guardo el servicio
			servicio = Servicio(idProveedor = proveedor, servicio = servicio, costo = costo)
			servicio.save()
			request.method="GET"
			return detallesProveedorControl(request,idProveedor=idProveedor,addServicioSuccess=True)
		else:
			try:
				idProveedor = request.GET["idProveedor"]
				proveedor = Proveedor.objects.get(idProveedor=idProveedor)
			except:
				errorIdProveedor = True
			return render_to_response('agregarServicio.html',locals(), context_instance = RequestContext(request))
	return HttpResponseRedirect('/404')
