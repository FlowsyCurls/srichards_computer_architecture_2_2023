from Utils import State
from Utils import MessageType

# Clase para representar un controlador de caché


class Controller:
    def __init__(self, cache, bus):
        self.cache = cache  # Caché a la que está asociado el controlador
        self.bus = bus

    def read(self, sender, address):
        # Verificar si el bloque está en caché
        block = self.cache.read(address)
        if block is not None:
            # Si el bloque está en caché, verificar su estado
            if block.state == State.INVALID:
                # Si el bloque está inválido, retornar un mensaje de invalido.
                return None

            if block.state == State.EXCLUSIVE and sender.id != self.cache.id:
                block.state = State.SHARED  # Si el bloque está E, actualizar estado a S
            return block.data  # Devolver dato

        else:
            # Si es un acceso local
            if sender.id == self.cache.id:
                # Si el bloque no está en caché, obtenerlo de otras caches o memoria
                self.bus.send_message(sender, address, MessageType.RdResp)
            # Si el acceso es remoto, retornar un mensaje invalido.
            return None

    # def write(self, address, data):
    #     # Verificar si el bloque está en caché
    #     block = self.cache.get_block(address)
    #     if block is not None:
    #         # Adquirir lock antes de acceder al bloque
    #         self.cache.acquire_lock(address)
    #         # Si el bloque está en caché y no está modificado, actualizar estado a M
    #         if block.state != State.M:
    #             block.state = State.M
    #         # Escribir dato en bloque y liberar lock
    #         block.write(data)
    #         self.cache.release_lock(address)
    #     else:
    #         # Si el bloque no está en caché, obtenerlo de la memoria
    #         self.ram.write(address, data)

    # Método para procesar un mensaje recibido por el bus

    def process_message(self, message_type, data):
        if message_type == MessageType.RdReq:
            self._process_read_request(data)
        elif message_type == MessageType.RdResp:
            self._process_read_response(data)
        # elif message_type == MessageType.WrReq:
            # self._process_write_request(data)
        # elif message_type == MessageType.Inv:
        #     self._process_invalidation(data)
        # elif message_type == MessageType.WB:
        #     self._process_write_back(data)

    # Método privado para procesar una solicitud de lectura
    def _process_read_request(self, address):
        block = self.cache.read(address)

        if not block:
            # Si no existe el bloque no se hace nada.
            return None

        if block.state == State.MODIFIED:
            # Si el bloque está en estado modificado, se debe escribir el bloque de vuelta a la memoria principal
            # antes de permitir que se lea el nuevo bloque desde la memoria principal
            self.bus.send_message(block.data, MessageType.WB)
            block.state = State.INVALID

        elif block.state == State.EXCLUSIVE:
            # Si el bloque está en exclusivo, el bloque pasa a ser compartido
            block.state = State.SHARED

        # Se envía el bloque al procesador solicitante
        self.bus.send_message(address, block.data, MessageType.RdResp)

    # Método privado para procesar una respuesta a una solicitud de lectura

    def _process_read_response(self, address, data):
        block = self.cache.write(address)

        if block:
            # Si todos los bloque están en Modified
            # Se escribe el dato en la memoria principal
            # Se invalida el bloque, luego se modifica nuevamente
            self.bus.send_message(block.data, MessageType.WB)
            # El bloque se convierte en compartido y se actualiza el dato en el bloque
            self.cache.write(address, data, State.SHARED)

    # Método privado para procesar una solicitud de escritura

    # def _process_write_request(self, sender, address):
    #     index, tag = self.cache._get_index_and_tag(address)
    #     block = self.cache.blocks[index]
    #     if block.state == BlockState.SHARED:
    #         # Si el bloque está en estado compartido, se debe enviar un mensaje de invalidación a todos los otros
    #         # procesadores que tengan copias de ese bloque
    #         self.cache.bus.send_message(
    #             self.cache, block.data, MessageType.Inv)
    #     block.state = BlockState.MODIFIED  # El bloque se convierte en modificado
    #     block.data = sender.write_data     # Se actualiza el dato en el bloque
    #     # Se escribe el dato en la memoria principal
    #     self.cache.bus.write(address, tag, sender.write_data)































# Clase que representa un bloque en la caché


# class Controller:
#     def __init__(self, cache, bus):
#         self.cache = cache
#         self.bus = bus

#     def read(self, address):
#         data = self.cache.read(address)
#         if data is None:
#             data = self.bus.read(address, self.cache)
#             if data is not None:
#                 self.cache.write(address, data)
#         return data

#     def write(self, address, data):
#         if self.cache.write(address, data):
#             self.bus.invalidate(address)
#         else:
#             self.bus.write(address, data, self.cache)


#            def evict(self):
#         # Verificar si hay algún bloque inválido
#         for block in self.blocks:
#             if block.state == State.I:
#                 self.blocks.remove(block)
#                 return

#         # Si no hay ningún bloque inválido, seleccionar un bloque para evicción
#         block = self.policy.select_block()
#         # Verificar si el bloque ha sido modificado
#         if block.state == State.M:
#             # Si el bloque ha sido modificado, escribir en la memoria principal
#             self.ram.write(block.address, block.data)
#             block.state = State.I
#         # Eliminar bloque de la caché
#         self.blocks.remove(block)
