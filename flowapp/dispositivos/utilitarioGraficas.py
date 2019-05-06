import pygal
from datetime import date, datetime


def graficar_bar_diagrama(total_consumo, consumo_limite):

    diagrama_bar = pygal.HorizontalBar(height=300)
    diagrama_bar.title = 'Contraste de Consumo en C.C'
    diagrama_bar.add('Consumo Limite', consumo_limite, rounded_bars=15)
    diagrama_bar.add({
        'title': 'Consumo Actual',
        'tooltip': 'Este es el consumo actual'
    }, [{
        'value': total_consumo,
        'xlink': {'href': 'https://www.somostriodos.com/app/uploads/sites/4/2014/09/INFOGRAF%C3%8DA-CONSUMO-AGua.png'}
    }], rounded_bars=15)
    diagrama_bar.render()
    diagrama_renderizado = diagrama_bar.render_data_uri()

    return (diagrama_renderizado)


def graficar_torta_diagrama(total_consumo, consumo_limite):

    diagrama_torta = pygal.Pie(height=450)
    diagrama_torta.title = 'Diagrama Relación Consumo/Restante en %'
    diagrama_torta.add('Consumido', 100*total_consumo/consumo_limite)
    diagrama_torta.add('Restante', 100-(100*total_consumo/consumo_limite))

    diagrama_torta.render()
    diagrama_renderizado = diagrama_torta.render_data_uri()
    return (diagrama_renderizado)


def graficar_date_diagrama(list_consumos):

    dateline = pygal.DateLine(x_label_rotation=25)
    lista_labels = []
    lista_informacion_consumo = []
    for consumo in list_consumos:
        lista_labels.append(datetime.timestamp(consumo.date))
        lista_informacion_consumo.append(
            (datetime.timestamp(consumo.date), consumo.quantity))

    dateline.x_labels = lista_labels
    dateline.add("Consumo", lista_informacion_consumo)
    dateline.render()
    diagrama_renderizado = dateline.render_data_uri()
    return (diagrama_renderizado)


def graficar_consumo_dia(lista_consumos_dia):
    lista_dias=[]
    lista_consumos=[]

    for etiqueta in lista_consumos_dia:
        lista_dias.append(etiqueta[0].strftime('%Y-%m-%d')+" "+etiqueta[0].strftime("%A"))
        lista_consumos.append(etiqueta[1])

    diagrama_barra_vertical = pygal.Bar()
    diagrama_barra_vertical.title = 'Consumo por días'
    #diagrama_barra_vertical.x_labels = lista_dias

    for informacion in lista_consumos_dia:
        diagrama_barra_vertical.add(informacion[0].strftime('%Y-%m-%d')+" "+informacion[0].strftime("%A"), informacion[1])

    diagrama_barra_vertical.render()
    diagrama_renderizado = diagrama_barra_vertical.render_data_uri()

    return (diagrama_renderizado)
