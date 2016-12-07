    'name': 'Concrete Sale Order',
    'version': '1.0',
    'category': 'Generic Modules/Sale',
    'author': 'BIAS',
    'depends': ['sale'],
    'update_xml': [
        'sale_view.xml',
        'sale_workflow.xml',
        'product_view.xml',
                   ],
**********************************************
    English description
**********************************************
""" Add the following fields in Sales Order:

    * Sale Order/Delivery Time.- First delivery time.
    * Sale Order/Delivery Spacing.- Spacing between truck and truck (or delivery and delivery).
    * Sale Order/Truck Capacity.- Maximum truck load capacity.
    * Sale Order/Transfer Time.- Estimated transfer time (to get at which time has to leave the truck).
    * Sale Order Line/Departure Time.- The time at which the truck has to go to deliver on time the product.

With this information, the module will be able to calculate how many stock moves have to be done and the right time for trucks departure based in delivery information, when order is confirmed or button Compute is clicked module generated right number of stock moves.

The module calculates delivery time using the following formula:

    First Departure Time  = Delibery Time - Estimated Transfer Time
    Second Departure Time = First Departure Time + Spacing Between Truck
    Third Departure Time  = Second Departure Time + Spacing Between Truck
    And so on...

The number of deliveries is calculated whith the folowing formula:

    Delivery List = [ Load_Capacity * integer(Product_qty/Load_Capacity) + Product_qty - Load_Capacity*int(Product_qty/Load_Capacity) ]

    Load_Capacity = Maximum truck load capacity.
    Product_qty = Total product quantity in sale order.
    
On Sale Order confirmation, or when click button Compute, the concrete module will do the folowing:
    * Check if one or more order products belong to a category with Check_Delivery field set, if so, check if delivery_time, delivery_spacing, load_capacity, and transfer_time fields Truck Delivery Information Tab are set, if not, raise a error menssage 'Missing Truck Delivery Information !'.
    * If some product category have Check Delivery field set, then the concrete module create one sale order lines for each Truck Departure with product UOM / UOS quantities and departure time according delivery information defined in sale order. 
    * The corresponding date/time is set in stock moves and procurements.

"""
**********************************************
    Descripción en Español
**********************************************
""" Añade los siguientes campos a la Orden de Venta:

    * Pedido de Venta/Fecha de Entrega.- Hora de la primera entrega.
    * Pedido de Venta/Espaciado entre camiones.- Espaciado entre camión y camión (o entrega y entrega).
    * Pedido de Venta/Capacidad de Carga.- Capacidad máxima de carga del camión.
    * Pedido de Venta/Tiempo de Traslado.- Tiempo de Translado estimado (Sirve para ver a que hora tiene que salir el camión).
    * Línea de Pedido de Venta/Hora de Salida.- Hora a la que tiene que salir el camión para entregar a tiempo el producto.

Con esta información, el módulo será capaz de calcular el número de movimientos de stock que se tienen que hacer y el momento adecuado para que los camiónes partan con base en los parámetros de entrega, cuando la orden se confirma o se hace clic en el botón Calcular el módulo genera el número correcto de los movimientos de stock.

El módulo calcula la hora de salida utilizando la siguiente fórmula:

    Primera salida  = Fecha de entrega - Tiempo de traslado
    Segunda salida = Primera salida + Espaciado entre camiones
    Tercera salida = Segunda salida + Espaciado entre camiones
    Y asi sucesivamente...

El numero de salidas se calcula en base a la siguiente formula:

    Lista de Salidas = [ Load_Capacity * integer(Product_qty/Load_Capacity) + Product_qty - Load_Capacity*int(Product_qty/Load_Capacity) ]

    Load_Capacity = Capacidad máxima de carga del camión.
    Product_qty = Cantidad total de producto a embarcar.

Cuando se confirma un Pedido de Compra, o cuando se oprime el botón de Calcular, el módulo de concreto realizará lo siguiente:
    * Revisa si uno o más productos pertenecen a una categoría con el campo Revisar Entrega seleccionado, si es así, revisa los campos Fecha de Entrega, Espaciado entre camiones, Capacidad de Carga, y Tiempo de Traslado estan definidos, si no, se muestra el error "Falta información de entrega del pedido !".
    * Si algúna categoría de producto del pedido tiene el campo Revisar Entrega seleccionado el módulo crea una línea de pedido por cada salida de camión con un tiempo de entrega y una cantidad de producto acorde a los parametros de entrega definidos en el pedido de venta.
    * También pone la fecha/hora a Los movimientos de inventario y abastecimientos correspondientes.

"""
