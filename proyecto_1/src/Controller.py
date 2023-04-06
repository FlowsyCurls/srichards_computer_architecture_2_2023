from Utils import *


class Controller:
    def __init__(self, running, bus, cache, cache_frame):
        self.running = running
        self.cache = cache  # Caché a la que está asociado el controlador
        self.cache_frame = cache_frame
        self.bus = bus
        self.processors_list = []
        self.nodes_quantity = NUM_CPU
        self.tmp = None
        self.mem_action_done = False

    ######################################################
    #   PROCESAMIENTO DE ACCIONES LOCALES
    ######################################################

    # Metodo para leer la cache local
    def read(self, sender, address, remote=False):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)

        if hit:
            # Si el bloque está, se cambia el estado y se envia.
            if remote:
                if block.state == State.MODIFIED:
                    # Si está en M y lo leen pasa a O

                    self.write_animation(block, HIGHLIGHT_RQ)

            if not remote:
                text = f" ✔️  Read Hit!   Cache {sender.id}    block: {block.id}    {block.state}    addr: {print_address_bin(address)}    data: {print_data_hex(block.data)}"
                print(f"\033[{GREEN}{text}\033[0m")
                # Animacion de lectura de la cache local
                self.cache_frame.read(block=f"B{block.id}")
                time.sleep(CACHE_RD_DELAY)
                self.running = False
            return [True, block]

        else:
            # Si no esta el block
            if not remote:
                text = f" ❌  Read Miss!   Cache {sender.id}   addr: {print_address_bin(address)}"
                print(f"\033[{RED}{text}\033[0m")

                # Si el bloque NO está en caché, se solicita a otro.
                self.processors_list = []
                self.bus.add_request(sender, MessageType.RdReq, address)
            return [False, None]

    # Metodo para escribir la cache local
    def write(self, sender, address, data):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)
        # print("procesador", self.cache.id, 0)
        # Guardar el valor de escritura
        self.tmp = data
        # print("procesador", self.cache.id, 1)

        if hit:
            # Si el bloque está, se verifica el estado.
            prev = block.data
            # print("procesador", self.cache.id, 2)

            # Si está en S, O y escribe pasa al estado M e invalida todo lo demás.
            if block.state in [State.SHARED, State.OWNED]:
                # Envia mensaje de invalidacion
                self.processors_list = []
                self.bus.add_request(sender, MessageType.Inv, address, "noreply")
            # print("procesador", self.cache.id, 3)

            block = self.cache.write_local(address, self.tmp)
            text = f" ✔️  Write Hit!   Cache {sender.id}    block: {block.id}    addr: {print_address_bin(address)}    data: {print_data_hex(prev)}  ➜  {print_data_hex(block.data)}"
            print(f"\033[{GREEN}{text}\033[0m")
            # print("procesador", self.cache.id, 4)

            # Animacion de escritura de la cache local
            self.write_animation(block)

        else:
            # print("procesador", self.cache.id, 5)
            # Si el bloque no está, se invalidan los demas con esta direccion
            text = f" ❌  Write Miss!   Cache {sender.id}   addr: {print_address_bin(address)}    data: {print_data_hex(data)}"
            print(f"\033[{RED}{text}\033[0m")

            self.processors_list = []
            # Se realiza un request en esta direccion en los otros procesadores
            self.bus.add_request(sender, MessageType.Inv, address)
            # print("procesador", self.cache.id, 6)

    def write_animation(self, block, color=HIGHLIGHT_WRITE):
        # Animacion de escritura de la cache local
        self.cache_frame.write(
            block=f"B{block.id}",
            info=[
                None,
                block.state.name[0],
                print_address_bin(block.address),
                None,
                print_data_hex(block.data),
            ],
            color=color,
        )

        time.sleep(CACHE_WR_DELAY)
        self.running = False

    ######################################################
    #   PROCESAMIENTO DE MENSAJES REMOTOS
    ######################################################

    # Método para procesar un mensaje recibido
    def _process_message(self, sender, message_type, address, detail=None):
        if message_type == MessageType.RdReq:
            self._process_read_request(sender, address)
        elif message_type == MessageType.RdResp:
            self._process_read_response(sender, address, detail)
        elif message_type == MessageType.Inv:
            self._process_invalidation(sender, address, detail)
        elif message_type == MessageType.InvResp:
            self._process_invalidation_response(sender, address, detail)

    # Método privado para procesar una solicitud de lectura

    def _process_read_request(self, sender, address):
        text = f" ▶  N{sender.id}   Read Request  ⟶   {print_address_bin(address)}"
        print(f"\033[{BLUE}{text}\033[0m")
        # Verificar si el bloque está en caché, es una consulta desde afuera.
        [hit, block] = self.read(sender, address, remote=True)

        if hit:
            # Si hit, se envía el bloque al procesador solicitante
            self.bus.add_response(
                self.cache.id, sender, MessageType.RdResp, address, block.data
            )

            if block.state == State.MODIFIED:
                # Si el bloque está en M, pasa a O
                block.state = State.OWNED
                self.write_animation(block, HIGHLIGHT_RQ)

            elif block.state == State.EXCLUSIVE:
                # Si el bloque está en E, pasa a S
                block.state = State.SHARED
                self.write_animation(block, HIGHLIGHT_RQ)
        else:
            # Si miss, se envia respuesta negativa
            self.bus.add_response(
                self.cache.id, sender, MessageType.RdResp, address, "miss"
            )

    def _process_read_response(self, src_id, address, detail):
        # Print
        text = f"   ❣️\tN{self.cache.id}  from   N{src_id}   ⟵   {detail}"
        color = RED if detail == "miss" else YELLOW
        print(f"\033[{color}{text}\033[0m")
        # print("procesador", self.cache.id, "a")
        # Si el mensaje es un miss
        if detail == "miss":
            # print("procesador", self.cache.id, "b")
            self.processors_list.append(src_id)
            if len(self.processors_list) == (self.nodes_quantity - 1):
                # print("procesador", self.cache.id, "c")
                # Si no se encuentra en ninguno de los procesadores
                # Se lee desde memoria y pasa a un estado exclusivo
                # data = self.bus.read(address)
                # RD

                self.mem_action_done = False
                self.bus.add_mem_request(self, MessageType.RD, address)
                # print("procesador", self.cache.id, "d")
                while not self.mem_action_done:
                    time.sleep(CYCLE_DURATION)
                # print("procesador", self.cache.id, "e")
                data = self.tmp  # dato retornado de peticion de lectura a la memoria.
                [resp, block] = self.cache.write(address, data, State.EXCLUSIVE)
                # print("procesador", self.cache.id, "f")

                if resp is True:
                    print(f"El bloque se ha obtenido de memoria.\n")
                    # Animacion de escritura de la cache local
                    self.write_animation(block)

                else:
                    # Si la respuesta de escritura es falsa, entonces significa que solo hay bloques M u O, hay que invalidar para escribir
                    # WB section
                    self.mem_action_done = False
                    self.bus.add_mem_request(
                        self, MessageType.WB, block.address, block.data
                    )
                    while not self.mem_action_done:
                        time.sleep(CYCLE_DURATION)

                    # Se invalida el bloque, luego se modifica nuevamente
                    block.state = State.INVALID
                    # Se guarda el nuevo valor en estado compartido.
                    [resp, block] = self.cache.write(address, data, State.EXCLUSIVE)

                    # Si la operacion es exitosa
                    if resp is True:
                        print(
                            f"El procesador {src_id} ha brindado el bloque.\nCorrectamente escrito en el primer block del set (Ambos en estado M u O)"
                        )
                        # Animacion de escritura de la cache local
                        self.write_animation(block)
                    else:
                        print("ERROR 0")

            else:
                print("ERROR 1")

        else:
            # Si el mensaje es un hit de alguna de las cache
            # Escribo el dato consultado, con política de escritura
            [resp, block] = self.cache.write(address, detail, State.SHARED)

            if resp is True:
                print(f"El procesador {src_id} ha brindado el bloque.")
                # Animacion de escritura de la cache local
                self.write_animation(block)

            else:
                # Si la respuesta de escritura es falsa, entonces significa que solo hay bloques M u O, hay que invalidar para escribir
                # Si todos los bloque están en Modified
                # Se escribe el dato en la memoria principal

                # WB section
                self.mem_action_done = False
                self.bus.add_mem_request(
                    self, MessageType.WB, block.address, block.data
                )
                while not self.mem_action_done:
                    time.sleep(CYCLE_DURATION)

                # Se invalida el bloque, luego se modifica nuevamente
                block.state = State.INVALID
                # Se guarda el nuevo valor en estado compartido.
                [resp, block] = self.cache.write(address, detail, State.SHARED)

                # Si la operacion es exitosa
                if resp is True:
                    print(
                        f"El procesador {src_id} ha brindado el bloque.\nCorrectamente escrito en el primer block del set (Ambos en estado M u O)"
                    )
                    # Animacion de escritura de la cache local
                    self.write_animation(block)

    # Método privado para procesar un mensaje de invalidación

    def _process_invalidation(self, sender, address, detail):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)
        print("procesador", self.cache.id, "z")
        if hit:
            # Si el bloque está, se analiza el estado.
            if block.state in [State.OWNED, State.MODIFIED]:
                # print("procesador", self.cache.id, "y")

                # Si el bloque está en O o M, se hace WB
                text = f"    ⤵️    N{sender.id} anula a N{self.cache.id}\n        Write-Back!    Cache {self.cache.id}    {block}"
                print(f"\033[{CIAN}{text}\033[0m")
                # WB section
                self.mem_action_done = False
                self.bus.add_mem_request(self, MessageType.WB, address, block.data)
                # print("procesador", self.cache.id, "x")
                while not self.mem_action_done:
                    time.sleep(CYCLE_DURATION)
                    # print("procesador", self.cache.id, "w")
            block.invalidate()
            self.write_animation(block, HIGHLIGHT_INV)
            # print("procesador", self.cache.id, "v")

        if detail == "noreply":
            # print("procesador", self.cache.id, "u")
            self.running = False
            return

        self.bus.add_response(
            self.cache.id, sender, MessageType.InvResp, address, block
        )
        # print("procesador", self.cache.id, "t")
        self.running = False

    # Metodo para escribir una vez la invalidacion haya finalizado.

    def _process_invalidation_response(self, src_id, address, detail):
        if detail is not None:
            text = f"   ❣️\tN{self.cache.id}          from\t N{src_id}   |  Invalidating - {detail}"
            print(f"\033[{CIAN}{text}\033[0m")

        # Si no se ha recibido mensaje de todos los procesadores, esperar.
        self.processors_list.append(src_id)
        # print("Tamano ", len(self.processors_list))
        if len(self.processors_list) == (self.nodes_quantity - 1):
            self.processors_list = []

            # Escribo en el bloque siguiendo la politica de escritura.
            [resp, block] = self.cache.write(address, self.tmp, State.MODIFIED)

            # Animacion de escritura de la cache local
            self.write_animation(block)
