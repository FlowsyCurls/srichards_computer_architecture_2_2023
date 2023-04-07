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

    # Metodo para lectura local desde peticion local
    def read_local(self, address):
        """
        Si yo leo mi propia cache.
            Si es hit:
                state queda igual
            Si no es hit:
                request del dato.
        """
        # Verificar si el bloque está en caché
        # NOTA: esta funcion toma en consideracion que el bloque sea invalido.
        [hit, block] = self.cache.read(address)

        # No es hit
        if not hit:
            # Indico que es un miss.
            self.cache_frame.miss_animation()

            # Solicito el bloque al bus.
            self.processors_list = []
            self.printc("read", "0")
            self.bus.add_request(
                requester=self, message_type=MessageType.RdReq, address=address
            )
            return

        # Es hit
        else:
            # Indico que es un hit.
            self.cache_frame.hit_animation()

            # Animacion de lectura de la cache local
            self.cache_frame.read(block=f"B{block.id}")
            self.printc("read", "1")

            # time.sleep(CACHE_RD_DELAY)
            self.running = False
            return

    # Metodo para leer la cache local desde peticion remota
    def read_remote(self, address):
        """
        Si alguien quiere un dato de mi cache
            Si es hit:
                M -> O
                O -> O
                E -> S
                S -> S
                I no entra es un miss automatico

                return -> dato

            Si no es hit:
                return -> 'miss'
        """

        # Verificar si el bloque está en caché
        # NOTA: esta funcion toma en consideracion que el bloque sea invalido.
        [hit, block] = self.cache.read(address)
        self.printc("read", "b")

        # Es hit
        if hit:
            # Si el bloque está enM, pasa a O
            if block.state == State.MODIFIED:
                block.state = State.OWNED
                self.printc("read", "c")

            # Si el bloque está en E, pasa a S
            elif block.state == State.EXCLUSIVE:
                block.state = State.SHARED
                self.printc("read", "d")

            self.write_animation(block=block, color=HIGHLIGHT_RQ)
            self.printc("read", "e")
            return block.data
        self.printc("read", "f")

        # No es hit
        return "miss"

    def write(self, address, new_data, state):
        [modif_state, block] = self.cache.write(address, new_data, state)
        self.printc("write", "/0")

        # Si se debe hacer WB:
        # Entonces el estado es Owned
        if modif_state == State.OWNED:
            self.printc("write", "/3")
            self._task_mem_wb(address=address, data=block.data)
            self.printc("write", "/4")
            block.set(address, new_data, state)

        if modif_state in [State.SHARED, State.OWNED]:
            # Inv -   Se realiza un request en esta direccion en los otros procesadores
            self.bus.add_request(self, MessageType.Inv, address)
            self.printc("write", "/5")

        self.write_animation(block)
        self.printc("write", "/6")

        # En este caso el procesador finaliza la accion si él mismo fue quien consultó.
        if state == State.MODIFIED:
            self.printc("write", "/7")
            self.running = False

    # Funcion para consultar la lectura desde memoria y esperar al valor
    def _task_mem_rd(self, address):
        self.mem_action_done = False
        self.bus.add_mem_request(self, MessageType.RD, address)
        # Esperamos la lectura del valor.
        while not self.mem_action_done:
            time.sleep(CYCLE_DURATION)
        return self.tmp  # dato retornado de peticion de lectura a la memoria.

    # Funcion para realizar wb a memoria y esperar que finalice.
    def _task_mem_wb(self, address, data):
        self.mem_action_done = False
        self.printc("write", "/1")
        self.bus.add_mem_request(self, MessageType.WB, address, data)
        # Esperamos la escritura del valor
        while not self.mem_action_done:
            time.sleep(CYCLE_DURATION)
        self.printc("write", "/2")

    ######################################################
    #   PROCESAMIENTO DE MENSAJES
    ######################################################

    # Método para procesar un mensaje recibido
    def _process_message(self, controller, message_type, address, detail=None):
        if message_type == MessageType.RdReq:
            self._process_read_request(controller, address)
        elif message_type == MessageType.RdResp:
            self._process_read_response(controller, address, detail)
        elif message_type == MessageType.Inv:
            self._process_invalidation(address)

    # Método privado para procesar una solicitud de lectura
    def _process_read_request(self, requester, address):
        """
        Recibo una solicitud de lectura a mi cache

            - Llamo a la lectura remota:
                Si es hit:
                    - response dato al que solicita

                Si no es hit:
                    - response 'miss' al que solicita
        """
        # Verificar si el bloque está en caché, es una consulta desde afuera.
        self.printc("read", "a")
        resp = self.read_remote(address)
        self.printc("read", "g")

        # Si miss, se envia respuesta negativa. Si hit, se envía el bloque al procesador solicitante
        self.bus.add_response(
            requester=requester,
            sponsor=self,
            message_type=MessageType.RdResp,
            address=address,
            detail=resp,
        )
        self.printc("read", "h")

    # Método privado para procesar las respuestas a la solicitud de lectura que hice
    def _process_read_response(self, sponsor, address, response):
        """
        Recibo una respuesta a mi solicitud de lectura a otras caches

            - Si es un hit:
                escribo el dato en mi cache local como compartido

            - Si es un miss:
                agrego a la lista de respuestas

                (si falta alguno en responder)
                    espero

                (si todos han respondido)
                    consulto el dato a memoria

        """

        self.printc("read", "-0")

        # Si el mensaje es un hit de alguna de las cache
        if response != "miss":
            # Escribo el dato consultado en estado compartido, con política de escritura
            self.write(address=address, new_data=response, state=State.SHARED)
            self.printc("read", "-1")
            return

        # Si el mensaje es un miss
        self.processors_list.append(sponsor.cache.id)
        self.printc("read", "-2")

        if len(self.processors_list) != (self.nodes_quantity - 1):
            # Si no han contestado todos, no hace nada
            return
        self.printc("read", "-3")

        # Si todos han respondido y no se encuentra en ninguno de los procesadores
        # Se lee desde memoria y pasa a un estado exclusivo
        mem_data = self._task_mem_rd(address=address)
        self.printc("read", "-4")

        # Se escribe en memoria cache.
        self.write(address=address, new_data=mem_data, state=State.EXCLUSIVE)
        self.printc("read", "-5")

    # Método privado para procesar un mensaje de invalidación
    def _process_invalidation(self, address):
        """
        Recibo una peticion de invalidar X direccion

            - Si es un hit:
                invalido
                reviso el estado:
                    O -> I
                    M -> I
                (ameritan un WB)
                los demás no

            - Si es un miss:
                no hago nada

        """
        self.printc("inval", ".0")

        [do_WB, updated_block] = self.cache.invalidate(address)
        self.printc("inval", ".1")

        if updated_block is None:
            self.running = False
            return

        # Si se debe hacer WB:
        if do_WB:
            self.printc("inval", ".2")
            self._task_mem_wb(address=address, data=updated_block.data)
        self.printc("inval", ".3")
        self.write_animation(updated_block, HIGHLIGHT_INV)
        self.running = False

    ######################################################
    #   PROCESAMIENTO DE ANIMACIONES
    ######################################################

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
        # time.sleep(CACHE_WR_DELAY)
        self.running = False

    def printc(self, action, text):
        if self.cache.id == 0:
            st = f" {action}\tP{self.cache.id}\t{text}"
            print(f"\033[{BLUE}{st}\033[0m")
        elif self.cache.id == 1:
            st = f"   {action}\tP{self.cache.id}\t{text}"
            print(f"\033[{YELLOW}{st}\033[0m")
        elif self.cache.id == 2:
            st = f"      {action}\tP{self.cache.id}\t{text}"
            print(f"\033[{RED}{st}\033[0m")
        elif self.cache.id == 3:
            st = f"          {action}\tP{self.cache.id}\t{text}"
            print(f"\033[{YELLOW}{st}\033[0m")
