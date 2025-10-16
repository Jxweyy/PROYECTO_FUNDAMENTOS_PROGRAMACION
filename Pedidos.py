import json
from datetime import datetime, timedelta
#### CARGAR LOS DATOS

############## CARGAR RUTA DE PEDIDO TENIENDO EN CUENTA ERROR

def cargar_pedido(ruta_archivo):
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
    

#DATOS DE PEDIDOS
def cargar_pedidos(ruta_archivo):
    try:
        data = json.load(open(ruta_archivo))
        print('he funcionado')
    except:
        print('no he funcionado')
        data = []
    return data


#DATOS DE ALMACEN
def cargar_datos_almacen(almacen):
    try:
        data = json.load(open(almacen))
        print('he funcionado')
    except:
        print('no he funcionado')
        data = {}
    return data


#ACTUALIZAR JSON
def dump_json(ruta, dump):   
    with open(ruta, 'w') as archivo:
        json.dump(dump, archivo, indent=4, ensure_ascii=False)  


#LISTA DE PEDIDOS SIN PROCESAR

def pedidos_sin_procesar():
    pedidos = cargar_pedidos('pedido.json')
    lista_pedidos_sin_procesar = []

    for n in range(len(pedidos)):
        lista_pedidos_sin_procesar.append(pedidos[n]['pedido_id'])

    return lista_pedidos_sin_procesar


#LISTA DE PEDIDOS PROCESADOS

def pedidos_procesados():
    pedidos_procesados = cargar_pedidos('pedidos_procesados.json')
    lista_pedidos_procesados = []

    for n in range(len(pedidos_procesados)):
        lista_pedidos_procesados.append(pedidos_procesados[n]['pedido_id'])

    return lista_pedidos_procesados

#CARGAR NUEVO PEDIDO

def cargar_pedido_nuevo(ruta):    

    pedidos = cargar_pedidos('pedido.json')

    pedido_nuevo = cargar_pedido(ruta)

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



# cargar_pedido_nuevo('Pedidos\pedido_test_3.json')


#########################################
#Lista con pedidos y cantidades
def productos_cantidades_pedido_seleccionado(pedido_id):
    pedidos = cargar_pedidos('pedido.json')
    

    productos_pedido_seleccionado = []
    cantidades_pedido_seleccionado = []
    for i in range(len(pedidos)):
        if pedido_id == pedidos[i]['pedido_id']:
          for j in range(len(pedidos[i]['productos'])):
            productos_pedido_seleccionado.append(pedidos[i]['productos'][j]['codigo'])
            cantidades_pedido_seleccionado.append(pedidos[i]['productos'][j]['unidades'])

    productos_cantidades_pedido_seleccionado = dict(zip(productos_pedido_seleccionado, cantidades_pedido_seleccionado))

    return productos_cantidades_pedido_seleccionado

################################################
#Lista de Products con sus stocks

def firulais():

    almacen = cargar_datos_almacen('almacen.json')

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

##################
def leer_pedido_y_verificar_stock(pedido_id):
    datos_almacen = firulais()
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
                print(f'no hay suficientes unidades de producto {producto} en almacén, hay que pedir {diferencia} unidades')
        else:
                lista_productos_pedir.append(producto)
                lista_cantidades_pedir.append(productos_cantidades_pedido[producto])
                print(f'No hay existencias de {producto}')


    productos_cantidades_enviar = dict(zip(lista_productos_enviar,lista_cantidades_enviar))
    productos_cantidades_pedir = dict(zip(lista_productos_pedir,lista_cantidades_pedir))
    dave = [productos_cantidades_enviar, productos_cantidades_pedir]
    print(productos_cantidades_pedir)
    return dave, productos_cantidades_enviar

leer_pedido_y_verificar_stock('P002')



#########################
def actualizar_almacén(pedido_id):
    almacen = firulais()
    dave, productos_cantidades_enviar = leer_pedido_y_verificar_stock(pedido_id)
    almacen_completo = cargar_datos_almacen('almacen.json')


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

# actualizar_almacén('P001')



####minabo duro

    

#PROCESAR PEDIDO

def procesar_pedido(pedido_id):

    pedidos = cargar_pedidos('pedido.json')

    pedidos_procesados = cargar_pedidos('pedidos_procesados.json')

    for n in range(len(pedidos)):
        if pedidos[n]['pedido_id'] == pedido_id:
                eliminado = pedidos.pop(n)
                pedidos_procesados.append(eliminado)
                break
        # break porque al quitar el pedido el len disminuye

    dump_json('pedido.json', pedidos)
    dump_json('pedidos_procesados.json', pedidos_procesados)

# procesar_pedido('P001')



def planificar_envio(pedido_id, dave):
    dave, productos_cantidades_enviar = leer_pedido_y_verificar_stock(pedido_id)
   
    pedidos = cargar_pedidos('pedido.json')
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
    if len(dave[1]) > 0:
        fecha_envio = fecha_base + timedelta(days=10)
        print('Hay productos que pedir a fábrica, la fecha de envío será en 10 días')
    # Su no hace falta pedir a fábrica, el envio es en 3 días
    else:
        fecha_envio = fecha_base + timedelta(days=3)
        print('Todo disponible, la fecha de envío será en 3 días')

    envio = {
        "pedido_id": pedido_id,
        "fecha_envio": fecha_envio.strftime("%Y-%m-%d"),
        "envio_almacen": dave[0],
        "pedir_fabrica": dave[1]}

    archivo_envio = f"Envios_envio_{pedido_id}.json"

    with open(archivo_envio, 'w', encoding='utf-8') as f:
        json.dump(envio, f, ensure_ascii=False, indent=2)

    return envio

# planificar_envio('P001', "A")