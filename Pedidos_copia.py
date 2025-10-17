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
                print(f'No hay existencias de {producto}')


    productos_cantidades_enviar = dict(zip(lista_productos_enviar,lista_cantidades_enviar))
    productos_cantidades_pedir = dict(zip(lista_productos_pedir,lista_cantidades_pedir))

    return productos_cantidades_enviar, productos_cantidades_pedir



### ACTUALIZAR ALMACÉN: La función resta todo lo que hemos enviado desde almacén. Primero cargamos las cantidades
### de almacén, el diccionario de productos a enviar y el almacen_completo (el .json inicial). Para cada producto
### en la lista de enviar, si este está en la lista almacén actualizamos la cantidad.
### Después, en el almacén completo recorremos cada módulo y su stock, y si este coincide con algún producto
### de los que enviamos, actualizamos su valor por el actualizado calculado antes, y printeamos el estado.
### Finalmente actualizamos el .json.

def actualizar_almacén(pedido_id):

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



### PLANIFICAR ENVÍO: Cargamos el archivo de envíos, el archivo de pedidos y pedimos las listas con los productos
### a envíar y pedir del pedido_id. Creamos un diccionario que empieza poniendo el pedido_id que se está planificando
### y otro diccionario datos donde irán las partes de los envíos.
### Recorremos todos los pedidos en pedidos.json y cuando coincida con el que hemos dado guardamos su fecha en una variable,
### en caso de no haber fecha cogemos la de hoy (evitamos error).
### Si hay objetos en la lista de pedir a fábrica (len > 0), añadimos una parte llamada fábrica y ponemos la fecha de pedido,
### la de envío (+10 días) y ponemos la lista de las cantidades a pedir. (PRODUCTOS QUE PEDIMOS)
### Si hay objetos en la lista de enviar ya (len > 0), añadimos una parte llamada stock y ponemos la fecha de pedido,
### la de envío (+3 días) y ponemos la lista de las cantidades a enviar. (PRODUCTOS QUE TENEMOS Y ENVIAMOS).
### Finalmente dumpeamos en nuestro .json de pedidos

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

    envios_archivo.append(envio)

    dump_json('envio.json', envios_archivo)

    return envio

planificar_envio('P001')