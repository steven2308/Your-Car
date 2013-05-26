from parametros import parametros
def nombreEmpresa(request):
    nombreEmpresa=parametros["nombreEmpresa"]
    return {
        'nombreEmpresa': nombreEmpresa,
    }