import json
from datetime import datetime, timedelta


### CARGAR JSON: Pide la ruta de archivo, hace bucle para que si la ruta da error la pida hasta que esté bien
### o se pulse C para volver a la interfaz.

def cargar_json(ruta_archivo):

    while(True):
        try:
            data = json.load(open(ruta_archivo))
            return data
        except:
            ruta_archivo = input("Error, introduzca la ruta de nuevo o pulse C para cancelar y volver al inicio: ")
            if ruta_archivo.upper() == "C":
                return []
                # mostrar_interfaz()
            else:
                continue



### ACTUALIZAR JSON: Pide la ruta del archivo a actualizar y el archivo que se va a dumpear.

def dump_json(ruta, dump):   

    with open(ruta, 'w') as archivo:
        json.dump(dump, archivo, indent=4, ensure_ascii=False)  



### LISTA PEDIDOS SIN PROCESAR: Carga pedidos.json, luego se genera una lista vacía donde se introducen
### cada 'P00X' del archivo con un for que lo recorre y los va agregando a esa lista vacía.

def pedidos_sin_procesar():

    pedidos = cargar_json('pedido.json')
    lista_pedidos_sin_procesar = []

    for n in range(len(pedidos)):
        lista_pedidos_sin_procesar.append(pedidos[n]['pedido_id'])

    return lista_pedidos_sin_procesar



### LISTA PEDIDOS PROCESADOS: Misma lógica que la función pedidos_sin_procesar, solo que con los procesados.

def pedidos_procesados():

    pedidos_procesados = cargar_json('pedidos_procesados.json')
    lista_pedidos_procesados = []

    for n in range(len(pedidos_procesados)):
        lista_pedidos_procesados.append(pedidos_procesados[n]['pedido_id'])

    return lista_pedidos_procesados



### CARGAR NUEVO PEDIDO: Se carga tanto el archivo de pedidos como el pedido nuevo (ruta que pide la función)
### y además se cargan las listas tanto de procesados como no procesados para que no haya duplicados. Usamos
### un for que entraría en cada pedido en caso de que nos llegue un archivo con más de un pedido. Posteriormente
### se compara si existe en alguna de las listas para que no se vuelva a meter, y si no está duplicado, se 
### agrega a la lista de pedidos y se llama a la función para actualizar el .json.

def cargar_pedido_nuevo(ruta):    

    pedidos = cargar_json('pedido.json')

    pedido_nuevo = cargar_json(ruta)

    lista_no_procesados = pedidos_sin_procesar()

    lista_procesados = pedidos_procesados()

    for n in range(len(pedido_nuevo)):

        if pedido_nuevo[n]['pedido_id'] not in lista_no_procesados:
            pedidos.append(pedido_nuevo[n])

            dump_json('pedido.json', pedidos)

            print(f'Pedido {pedido_nuevo[n]['pedido_id']} no está procesado. Añadido a pedidos sin procesar.')
        elif pedido_nuevo[n]['pedido_id'] in lista_procesados:
            print(f'Pedido {pedido_nuevo[n]['pedido_id']} ya está procesado.')
        elif pedido_nuevo[n]['pedido_id'] in lista_no_procesados:
            print(f'Pedido {pedido_nuevo[n]['pedido_id']} ya está añadido a no procesados.')



### LISTA PEDIDOS CANTIDADES: Se carga el archivo de pedidos. La idea de la función es sacar del pedido que se
### introduzca una lista de lo que se pide con sus cantidades. Se generan dos listas vacías de producto y cantidades.
### Se recorre toda la lista de pedidos y si este coincide con el proporcionado a la función se recorre cada producto
### del que se saca el producto y la cantidad. Posteriormente se usa .zip para unirlas en un diccionario.

def productos_cantidades_pedido_seleccionado(pedido_id):
    pedidos = cargar_json('pedido.json')
    

    productos_pedido_seleccionado = []
    cantidades_pedido_seleccionado = []

    for i in range(len(pedidos)):
        if pedido_id == pedidos[i]['pedido_id']:
          for j in range(len(pedidos[i]['productos'])):
            productos_pedido_seleccionado.append(pedidos[i]['productos'][j]['codigo'])
            cantidades_pedido_seleccionado.append(pedidos[i]['productos'][j]['unidades'])

    productos_cantidades_pedido_seleccionado = dict(zip(productos_pedido_seleccionado, cantidades_pedido_seleccionado))

    return productos_cantidades_pedido_seleccionado



### LISTA PEDIDOS STOCKS: Se trata de sacar en un mismo diccionario TODOS los productos y cantidades del almacén.
### Se carga el almacén, y se hacen dos listas de producto y stock (cantidad). Recorremos cada módulo y dentro de cada
### uno recorremos todo el stock, del que sacamos los productos (keys) y el stock (values). Se usa finalmente
### .zip para tener un diccionario del almacén con productos y cantidades.

def productos_cantidades_almacen():

    almacen = cargar_json('almacen.json')

    producto = []
    stock = []

    for n in almacen['almacen'].keys(): 
        for j in almacen['almacen'][n]['stock'].keys():
            producto.append(j)
    for n in almacen['almacen'].keys(): 
        for j in almacen['almacen'][n]['stock'].values():
            stock.append(j)
    producto_stock = dict(zip(producto,stock))
    
    return producto_stock



### LEER PEDIDO Y VERIFICAR STOCK: La idea es que dado un pedido_id que se le da a la función, comprobar si tenemos
### los productos solicitados en el almacén o si bien hay que pedirlos. Cargamos el diccionario del almacén total y
### el diccionario de productos y cantidades del pedido_id. Se generan 4 listas. Recorremos los productos, y si este
### está en el almacén (keys):
### - Si la cantidad en almacén es mayor que pedido, se agrega el producto y su cantidad a las listas de cantidades
### y productos enviar.
### - Si la cantidad es menor, se calcula la diferencia entre lo pedido y del almacén. La cantidad en almacén va
### de nuevo a productos y cantidades para envíar, y la diferencia va a la lista de pedir (junto con el producto).
### Finalmente los productos de lo que no tenemos nada en almacén van a las listas de pedir. Hacemos .zip.

def leer_pedido_y_verificar_stock(pedido_id):

    datos_almacen = productos_cantidades_almacen()
    productos_cantidades_pedido = productos_cantidades_pedido_seleccionado(pedido_id)

    lista_productos_enviar = []
    lista_productos_pedir = []

    lista_cantidades_enviar = []
    lista_cantidades_pedir = []

    for producto in productos_cantidades_pedido.keys():
        if producto in datos_almacen.keys():
            
            if productos_cantidades_pedido[producto] < datos_almacen[producto]:
                print(f'Tenemos las cantidades de {producto} ')
                lista_productos_enviar.append(producto)
                lista_cantidades_enviar.append(productos_cantidades_pedido[producto])
            else:
                diferencia = productos_cantidades_pedido[producto] - datos_almacen[producto]
                lista_productos_pedir.append(producto)
                lista_cantidades_pedir.append(diferencia)
                lista_productos_enviar.append(producto)
                lista_cantidades_enviar.append(datos_almacen[producto])
                print(f'No hay suficientes unidades de producto {producto} en almacén, hay que pedir {diferencia} unidades')
        else:
                lista_productos_pedir.append(producto)
                lista_cantidades_pedir.append(productos_cantidades_pedido[producto])
                print(f'No hay existencias de {producto}. Pedimos {productos_cantidades_pedido[producto]}.')


    productos_cantidades_enviar = dict(zip(lista_productos_enviar,lista_cantidades_enviar))
    productos_cantidades_pedir = dict(zip(lista_productos_pedir,lista_cantidades_pedir))

    return productos_cantidades_enviar, productos_cantidades_pedir



### ACTUALIZAR ALMACÉN RESTAR: La función resta todo lo que hemos enviado desde almacén. Primero cargamos las cantidades
### de almacén, el diccionario de productos a enviar y el almacen_completo (el .json inicial). Para cada producto
### en la lista de enviar, si este está en la lista almacén actualizamos la cantidad.
### Después, en el almacén completo recorremos cada módulo y su stock, y si este coincide con algún producto
### de los que enviamos, actualizamos su valor por el actualizado calculado antes, y printeamos el estado.

def actualizar_almacén_restar(pedido_id):

    almacen = productos_cantidades_almacen()
    productos_cantidades_enviar, productos_cantidades_pedir = leer_pedido_y_verificar_stock(pedido_id)
    almacen_completo = cargar_json('almacen.json')


    for n in productos_cantidades_enviar.keys():
        if n in almacen.keys():
           almacen[n] = almacen[n]-productos_cantidades_enviar[n]



    for i in almacen_completo['almacen'].keys():

            for j in almacen_completo['almacen'][i]['stock'].keys():
                for k in productos_cantidades_enviar.keys():
                    if j == k:
                        almacen_completo['almacen'][i]['stock'][j] = almacen[k]
                        print(f'El producto {j} viene del modulo: {i} y tras el envío quedan {almacen_completo['almacen'][i]["stock"]} unidades')

    dump_json('almacen.json', almacen_completo)

    return almacen_completo, productos_cantidades_pedir




### FÁRMACOS TEMPERATURA: Recorremos todos los productos de fármacos y sus temperaturas, las metemos cada una a
### una lista y posteriormente las unimos en un diccionario.

def farmacos_temperatura():

    farmacos = cargar_json('farmacos.json')

    lista_farmacos = []

    lista_farmacos_temperatura = []


    for i in farmacos.keys():
        for j in farmacos[i].keys():
            lista_farmacos.append(i)
            lista_farmacos_temperatura.append(farmacos[i]['temperatura_requerida'])

    farmacos_temperatura = dict(zip(lista_farmacos, lista_farmacos_temperatura))

    return farmacos_temperatura



### ACTUALIZAR ALMACÉN SUMAR RESTAR: Cargamos cantidades almacén y temperaturas fármacos, también el almacén completo y el
### diccionario de productos a pedir (proveniente de función de almacén restar, que de paso resta la cantidad que enviamos de almacén). ç
### Recorremos los productos a pedir y los fármacos, si coinciden, guardamos la cantidad a pedir extra
### para almacén, el producto que es y su temperatura. Posteriormente, recorremos todos los módulos, y si la temperatura
### coincide con la requerida, calculamos el espacio total, el actual para ver cuantos productos caben:
### - Si el espacio del módulo es 0, entonces vamos al siguiente.
### - Si el espacio es mayor a lo que pedimos, es que entra todo así que entra todo a ese módulo.
### - Si el espacio es menor a lo que pedimos, entra la cantidad que haya restante (espacio disponible), y se continua al siguiente
### módulo compatible.
### Finalmente si esa cantidad restante no ha entrado en ninguno de los módulos, se printea y finalmente se hace dump.

def actualizar_almacén_sumar_restar(pedido_id):

    farmacos_temp = farmacos_temperatura()
    x, productos_cantidades_pedir = actualizar_almacén_restar(pedido_id)
    # restamos primero las cantidades que tenemos y enviamos.
    almacen_completo = cargar_json('almacen.json')
    # aquí cogemos la lista de productos a pedir (leer_y_verificar stock dentro de esta), y la lista de productos a pedir.
    # importante tener cargar el almacén luego porque si no no tenemos el restado
    for i in productos_cantidades_pedir:
        for j in farmacos_temp:
            if i == j:
                cantidad_almacén_extra = int(productos_cantidades_pedir[i] * 0.10) # pedimos un 10% más de lo que tenemos que pedir
                print(f'Añadimos {cantidad_almacén_extra} extra de {i} para nuestro almacén.')
                producto = i
                temperatura = farmacos_temp[j]
                for k in almacen_completo['almacen'].keys():
                    if almacen_completo['almacen'][k]['temperatura'] == temperatura:

                        capacidad_maxima = almacen_completo['almacen'][k]['capacidad_maxima']
                        capacidad_actual = sum(almacen_completo['almacen'][k]['stock'].values())
                        espacio_disponible = capacidad_maxima - capacidad_actual

                        if espacio_disponible <= 0:
                            print(f'Capacidad del módulo {k} llena. Pasando al siguiente compatible.')
                            continue
                            # Módulo lleno: por tanto pasamos al siguiente

                        if espacio_disponible >= cantidad_almacén_extra:
                            stock_actual = almacen_completo['almacen'][k]['stock'].get(producto, 0)
                            # get para que si no existe, lo añada al diccionario con valor 0, si no nos da error
                            almacen_completo['almacen'][k]['stock'][producto] = stock_actual + cantidad_almacén_extra
                            print(f'Añadido {cantidad_almacén_extra} unidades de {producto} a módulo {k}. Estado: {almacen_completo['almacen'][k]["stock"]}')
                            cantidad_almacén_extra = 0
                            break
                            # ya hemos metido todos los productosç
                                                   
                        elif espacio_disponible <= cantidad_almacén_extra:
                            stock_actual = almacen_completo['almacen'][k]['stock'].get(producto, 0)
                            # get para que si no existe, lo añada al diccionario con valor 0, si no nos da error
                            almacen_completo['almacen'][k]['stock'][producto] = stock_actual + espacio_disponible
                            # espacio disponible es la cantidad que podemos añadir sin sobrepasar el tope
                            cantidad_almacén_extra = cantidad_almacén_extra - espacio_disponible
                            # cantidad restante despúes de haber metido todo lo que podiamos al MOD, continua al siguiente
                            print(f'Añadido {espacio_disponible} unidades de {producto} a módulo {k}. Quedan {cantidad_almacén_extra} por añadir. Estado: {almacen_completo['almacen'][k]["stock"]}  Modulo lleno. Siguiente.')
                            continue

                if cantidad_almacén_extra > 0:
                        print(f'Quedan {cantidad_almacén_extra} de {producto} por añadir. Todos los módulos llenos.')

    dump_json('almacen.json', almacen_completo)



### PROCESAR PEDIDO: Cargamos tanto el .json de pedidos como el del pedidos procesados, y recorremos cada uno
### de los pedidos. Si este coincide con el que se ha introducido, se elimina ese pedido y se guarda en una variable,
### para luego agregarlo al .json de pedidos procesados. Finalmente llamamos a la función dump para actualizar y guardar
### los dos .json.

def procesar_pedido(pedido_id):

    pedidos = cargar_json('pedido.json')

    pedidos_procesados = cargar_json('pedidos_procesados.json')

    for n in range(len(pedidos)):
        if pedidos[n]['pedido_id'] == pedido_id:
                eliminado = pedidos.pop(n)
                pedidos_procesados.append(eliminado)
                break
        # break porque al quitar el pedido el len disminuye, si no nos da error de out of index.

    dump_json('pedido.json', pedidos)
    dump_json('pedidos_procesados.json', pedidos_procesados)



### PLANIFICAR ENVÍO:

def planificar_envio(pedido_id):

    envios_archivo = cargar_json('envio.json')

    pedidos = cargar_json('pedido.json')

    productos_cantidades_enviar, productos_cantidades_pedir = leer_pedido_y_verificar_stock(pedido_id)
    
    envio = {
        "Pedido_id": pedido_id,
        "Datos": {}
    }
    
    fecha_pedido = None
    # definimos fecha de envio para cada pedido recorriendo el json de pedidos
    for i in pedidos:
        if i['pedido_id'] == pedido_id:
            fecha_pedido = i['fecha']
    # por si acaso, si no se encuentra la fecha del pedido, a tomar por saco. Se usa la de hoy
    if fecha_pedido is None:
        print('No se ha encontrado la fecha del pedido, se utilizará la de hoy')
        fecha_base = datetime.today()
    else:
        fecha_base = datetime.strptime(fecha_pedido, "%Y-%m-%d")
    # si no hay productos a pedir a fábrica, entonces el envío es en 10 días
    if len(productos_cantidades_pedir) > 0:
        fecha_envio = fecha_base + timedelta(days=10)
        print('Hay productos que pedir a fábrica, la fecha de envío será en 10 días')
        envio['Datos']['Fábrica'] = {
            "fecha_pedido": fecha_base.strftime("%Y-%m-%d"),
            "fecha_envio": fecha_envio.strftime("%Y-%m-%d"),
            "envio_almacen": productos_cantidades_pedir}

    # Su no hace falta pedir a fábrica, el envio es en 3 días
    if len(productos_cantidades_enviar) > 0:
        fecha_envio = fecha_base + timedelta(days=3)
        print('Todo disponible, la fecha de envio sera en 3 dias')
        envio['Datos']['Stock'] = {
            "fecha_pedido": fecha_base.strftime("%Y-%m-%d"),
            "fecha_envio": fecha_envio.strftime("%Y-%m-%d"),
            "envio_stock": productos_cantidades_enviar}
    # strftime("%Y-%m-%d") porque si no no se puede meter a .json
    archivo_envio = f"Envios_envio_{pedido_id}.json"

    envios_archivo.append(envio)

    dump_json('envio.json', envios_archivo)

    return envio

