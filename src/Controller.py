

from Utils import *


class Controller:
    def __init__(self, cache, bus):
        self.cache = cache  # Caché a la que está asociado el controlador
        self.bus = bus
        self.processors_list = []
        self.nodes_quantity = 2
        self.tmp = None

    # Metodo para leer la cache local

    def read(self, sender, address, remote=False):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)

        if hit:
            # Si el bloque está, se cambia el estado y se envia.
            if remote:
                if block.state == State.MODIFIED:
                    # Si está en M y lo leen pasa a O
                    block.set(address, State.OWNED)

            if not remote:
                text = f' ✔️  Read Hit!   Cache {sender.id}    block: {block.id}    address: {address}    data: {block.data}'
                print(f"\033[{GREEN}{text}\033[0m")

            return [True, block]

        else:
            # Si no esta el block
            if not remote:
                text = f' ❌  Read Miss!   Cache {sender.id}   addr: {print_address_bin(address)}'
                print(f"\033[{RED}{text}\033[0m")

                # Si el bloque NO está en caché, se solicita a otro.
                self.processors_list = []
                self.bus.add_request(sender, MessageType.RdReq, address)
            return [False, None]

    # Metodo para escribir la cache local
    def write(self, sender, address, data):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)

        if hit:
            # Si el bloque está, se verifica el estado.
            prev = block.data

            # Si está en S, O y escribe pasa al estado M e invalida todo lo demás.
            if block.state in [State.SHARED, State.OWNED]:
                # Envia mensaje de invalidacion
                self.bus.add_request(sender, MessageType.Inv, address)

            block = self.cache.write_local(address, data)
            text = f' ✔️  Write Hit!   Cache {sender.id}    block: {block.id}    address: {address}    data: {prev}  ->  {block.data}'
            print(f"\033[{GREEN}{text}\033[0m")

        else:
            # Si el bloque no está, se invalidan los demas con esta direccion
            text = f' ❌  Write Miss!   Cache {sender.id}   addr: {print_address_bin(address)}'
            print(f"\033[{RED}{text}\033[0m")

            # Se realiza un request en esta direccion en los otros procesadores
            self.bus.add_request(sender, MessageType.Inv, address)

            # Guardar el valor de escritura
            self.tmp = data

    # Metodo para escribir una vez la invalidacion haya finalizado.
    def _process_invalidation_response(self, src_id, address, detail):
        
        text = f'   ❣️\tN{self.cache.id}          from\t N{src_id}   |  {detail}'
        print(f"\033[{CIAN}{text}\033[0m")

        # Si no se ha recibido mensaje de todos los procesadores, esperar.
        self.processors_list.append(src_id)
        if len(self.processors_list) == (self.nodes_quantity-1):
            # Escribo en el bloque siguiendo la politica de escritura.
            self.cache.write(address, self.tmp, State.MODIFIED)

    # Método para procesar un mensaje recibido
    def _process_message(self, sender, message_type, address, detail=None):
        if message_type == MessageType.RdReq:
            self._process_read_request(sender, address)
        elif message_type == MessageType.RdResp:
            self._process_read_response(sender, address, detail)
        elif message_type == MessageType.Inv:
            self._process_invalidation(sender, address)
        elif message_type == MessageType.InvResp:
            self._process_invalidation_response(sender, address, detail)

    # Método privado para procesar una solicitud de lectura

    def _process_read_request(self, sender, address):
        text = f' ▶  N{sender.id}   Read Request  ⟶   {print_address_bin(address)}'
        print(f"\033[{BLUE}{text}\033[0m")
        # Verificar si el bloque está en caché, es una consulta desde afuera.
        [hit, block] = self.read(sender, address, remote=True)

        if hit:
            # Si hit, se envía el bloque al procesador solicitante
            self.bus.add_response(
                self.cache.id, sender, MessageType.RdResp, address, block.data)

            if block.state == State.MODIFIED:
                # Si el bloque está en M, pasa a O
                block.state = State.OWNED

            elif block.state == State.EXCLUSIVE:
                # Si el bloque está en E, pasa a S
                block.state = State.SHARED

        else:
            # Si miss, se envia respuesta negativa
            self.bus.add_response(
                self.cache.id, sender, MessageType.RdResp, address, 'miss')

    def _process_read_response(self, src_id, address, detail):
        text = f'   ❣️\tN{self.cache.id}        from   \t N{src_id}   |  {print_address_bin(address)}   {detail}'
        # Si el mensaje es un miss
        if detail == 'miss':
            print(f"\033[{RED}{text}\033[0m")
            self.processors_list.append(src_id)
            if len(self.processors_list) == (self.nodes_quantity-1):
                # Si no se encuentra en ninguno de los procesadores
                # Se lee desde memoria y pasa a un estado exclusivo
                data = self.bus.read(address)
                self.cache.write(address, data, State.EXCLUSIVE)
            return

        # Si el mensaje es un hit
        print(f"\033[{GREEN}{text}\033[0m")
        # Escribo el dato consultado, con política de escritura
        block = self.cache.write(address, detail, State.SHARED)

        if block is None:
            print(f'El procesador {src_id} ha brindado el bloque.')
            return

        # Si todos los bloque están en Modified
        # Se escribe el dato en la memoria principal
        self.bus.write(block.address, block.data)
        block.state = State.INVALID  # Se invalida el bloque, luego se modifica nuevamente
        # Se guarda el nuevo bloque en estado compartido.
        block = self.cache.write(address, detail, State.SHARED)

        # Si la operacion es exitosa
        if block is None:
            print(
                f'Se escribe correctamente en el block en la primera posicion por ser todos los blocks modified')

    # Método privado para procesar un mensaje de invalidación

    def _process_invalidation(self, sender, address):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)

        if hit:
            # Si el bloque está, se analiza el estado.
            if block.state in [State.OWNED, State.MODIFIED]:
                # Si el bloque está en O O M, se hace WB
                text = f'    ⤵️    N{sender.id} anula a N{self.cache.id}\n        Write-Back!    Cache {self.cache.id}    {block}'
                print(f"\033[{GREEN}{text}\033[0m")
                self.bus.write(address, block.data)
            block.invalidate()

        self.bus.add_response(self.cache.id, sender,
                              MessageType.InvResp, address, block)
