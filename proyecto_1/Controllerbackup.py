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

        '''
        Si es un hit, entonces debemos verificar el bloque
        Si yo leo localmente, no pasa nada.
        
        Si me leen:
            en M, pasa a O
            en cualquier otro estado, no pasa nada.
        '''
        if hit:
            # Si el bloque está, se cambia el estado y se envia.
            if remote:
                if block.state == State.MODIFIED:
                    # Si está en M y lo leen pasa a O
                    self.write_animation(block, HIGHLIGHT_RQ)

            if not remote:
                # text = f" ✔️  Read Hit!   Cache {sender.id}    block: {block.id}    {block.state}    addr: {print_address_bin(address)}    data: {print_data_hex(block.data)}"
                # print(f"\033[{GREEN}{text}\033[0m")
                self.cache_frame.hit_animation()
                # Animacion de lectura de la cache local
                self.cache_frame.read(block=f"B{block.id}")
                time.sleep(CACHE_RD_DELAY)
                self.running = False
            return [True, block]

        else:
            # Si no esta el block
            if not remote:
                # text = f" ❌  Read Miss!   Cache {sender.id}   addr: {print_address_bin(address)}"
                # print(f"\033[{RED}{text}\033[0m")
                self.cache_frame.miss_animation()
                # Si el bloque NO está en caché, se solicita a otro.
                self.processors_list = []
                self.bus.add_request(sender, MessageType.RdReq, address)
            return [False, None]

    # # Metodo para escribir la cache local
    # def write(self, sender, address, data):
    #     # Verificar si el bloque está en caché
    #     [hit, block] = self.cache.read(address)
    #     # Guardar el valor de escritura
    #     new_value = data
    #     prev_value = block.data

    #     if hit:
    #         # text = f" ✔️  Write Hit!   Cache {sender.id}    block: {block.id}    addr: {print_address_bin(address)}    data: {print_data_hex(prev)}  ➜  {print_data_hex(block.data)}"
    #         # print(f"\033[{GREEN}{text}\033[0m")
    #         self.cache_frame.hit_animation()

    #         # Proceso con la funcion auxiliar
    #         self._write_aux(
    #             state=State.MODIFIED,
    #             address=address,
    #             prev_data=prev_value,
    #             next_data=new_value,
    #         )

    #         # Inv -   Si está en S, O y escribe pasa al estado M e invalida todo lo demás.
    #         if block.state in [State.SHARED, State.OWNED]:
    #             # Envia mensaje de invalidacion
    #             self.bus.add_request(sender, MessageType.Inv, address)
    #         return

    #     # Si el bloque no está:

    #     # text = f" ❌  Write Miss!   Cache {sender.id}   addr: {print_address_bin(address)}    data: {print_data_hex(data)}"
    #     # print(f"\033[{RED}{text}\033[0m")
    #     self.cache_frame.miss_animation()

    #     # Proceso con la funcion auxiliar
    #     self._write_aux(
    #         state=State.MODIFIED,
    #         address=address,
    #         prev_data=prev_value,
    #         next_data=new_value,
    #     )

    #     # Inv -   Se realiza un request en esta direccion en los otros procesadores
    #     self.bus.add_request(sender, MessageType.Inv, address)

    # Procesa si hay un write back
    def _write_aux(self, state, address, prev_data, next_data):
        # Escribo primero antes de mandar invalidacion por la sincronizacion.
        [resp, block] = self.cache.write(address, next_data, State.MODIFIED)

        if resp is True:
            # print(f"El bloque se ha obtenido de memoria.\n")
            # Animacion de escritura de la cache local
            self.write_animation(block)
            return

        # WB  -   Si la respuesta de escritura es falsa, entonces significa que solo hay bloques M u O, hay que invalidar para escribir
        self._wb(
            state=State.EXCLUSIVE,
            address=block.address,
            prev_data=block.data,
            next_data=next_data,
        )

    def _wb(self, state, address, prev_data, next_data):
        # Se invalida el bloque, luego se modifica nuevamente
        block.state = State.INVALID
        # escribimos el valor viejo en memoria
        self._do_wb_or_rd(message_type=MessageType.WB, address=address, data=prev_data)
        # escribimos el valor nuevo en el bloque
        [resp, block] = self.cache.write(address, next_data, state)

        # Si la operacion es exitosa
        if resp is True:
            # Animacion de escritura de la cache local
            self.write_animation(block)
        else:
            print("ERROR 0")

    def _do_wb_or_rd(self, message_type, address, data):
        # WB section
        self.mem_action_done = False
        self.bus.add_mem_request(self, message_type, address, data)
        while not self.mem_action_done:
            time.sleep(CYCLE_DURATION)
        return self.tmp  # dato retornado de peticion de lectura a la memoria.

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
            self._process_invalidation(sender, address)

    # Método privado para procesar una solicitud de lectura
    def _process_read_request(self, sender, address):
        # text = f" ▶  N{sender.id}   Read Request  ⟶   {print_address_bin(address)}"
        # print(f"\033[{BLUE}{text}\033[0m")
        # Verificar si el bloque está en caché, es una consulta desde afuera.
        [hit, block] = self.read(sender, address)

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
        # text = f"   ❣️\tN{self.cache.id}  from   N{src_id}   ⟵   {detail}"
        # color = RED if detail == "miss" else YELLOW
        # print(f"\033[{color}{text}\033[0m")
        # Si el mensaje es un miss
        if detail == "miss":
            self.processors_list.append(src_id)
            if len(self.processors_list) == (self.nodes_quantity - 1):
                # Si no se encuentra en ninguno de los procesadores
                # Se lee desde memoria y pasa a un estado exclusivo
                # RD
                next_data = self._do_wb_or_rd(
                    message_type=MessageType.RD, address=address, data=None
                )
                [resp, block] = self.cache.write(address, next_data, State.EXCLUSIVE)

                if resp is True:
                    # print(f"El bloque se ha obtenido de memoria.\n")
                    # Animacion de escritura de la cache local
                    self.write_animation(block)
                    return

                # WB
                # Si la respuesta de escritura es falsa, entonces significa que solo hay bloques M u O, hay que invalidar para escribir
                self._wb(
                    state=State.EXCLUSIVE,
                    address=block.address,
                    prev_data=block.data,
                    next_data=next_data,
                )
                # Inv -   Se realiza un request en esta direccion en los otros procesadores
                self.bus.add_request(sender, MessageType.Inv, address)    

            # Si no han contestado todos, no hace nada
            return

        else:
            # Si el mensaje es un hit de alguna de las cache
            # Escribo el dato consultado, con política de escritura
            [resp, block] = self.cache.write(address, detail, State.SHARED)

            if resp is True:
                # print(f"El procesador {src_id} ha brindado el bloque.")
                # Animacion de escritura de la cache local
                self.write_animation(block)
                return

            # Si la respuesta de escritura es falsa, entonces significa que solo hay bloques M u O, hay que invalidar para escribir
            # detail tiene el dato que debemos escribir, pero primero tenemos que hacer write back, invalidar y escribir el bloque nuevo en cache
            self._process_wb(
                state=State.SHARED,
                address=block.address,
                prev_data=block.data,
                next_data=detail,
            )

    # Método privado para procesar un mensaje de invalidación

    # def _process_invalidation(self, sender, address):
    #     # Verificar si el bloque está en caché
    #     [hit, block] = self.cache.read(address)
    #     if hit:
    #         # Si el bloque está, se analiza el estado.
    #         if block.state in [State.OWNED, State.MODIFIED]:
    #             # Si el bloque está en O o M, se hace WB
    #             # text = f"    ⤵️    N{sender.id} anula a N{self.cache.id}\n        Write-Back!    Cache {self.cache.id}    {block}"
    #             # print(f"\033[{CIAN}{text}\033[0m")
    #             # WB section
    #             self.mem_action_done = False
    #             self.bus.add_mem_request(self, MessageType.WB, address, block.data)
    #             while not self.mem_action_done:
    #                 time.sleep(CYCLE_DURATION)
    #         block.invalidate()
    #         self.write_animation(block, HIGHLIGHT_INV)
    #     self.running = False
