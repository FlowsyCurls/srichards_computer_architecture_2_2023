import time
from Utils import *
from myrandom import myrandom


class Controller:
    def __init__(self, id, core_board, cache, channel):
        self.id = id
        self.core_board = core_board
        self.cache = cache
        self.channel = channel

    """
    Process the next instruccion to be executed.
    """

    def execute(self):
        # Update string variable of the current instruction
        inst_str = self.core_board.next_instr_stringvar.get()
        self.core_board.curr_instr_stringvar.set(inst_str)

        # Get parts of the instruction
        core_name, *rest = inst_str.split(": ")
        op, *rest = rest[0].split(" ")

        if op == "CALC":
            message = {"id": core_name, "access": AccessType.calc}
            self.channel.put(message)
            return

        # Get address part
        address = rest[0].split(";")[0]

        # Get block from cache
        block = self.cache.get_block_by_address(address)

        if op == "READ":
            #  readhit  -   If block is in cache and state is not I
            if block is not None and block.get_state() != "I":
                self.core_board.animation_access("read hit")
                time.sleep(CACHE_WR_DELAY)
                self.cache.animation(block.get_id(), HIGHLIGHT_HIT)
                return

            # readmiss   -   If block is not in cache
            block_id = (
                # If block is not in cache then look for a place to write
                # if block is in cache but I then use this place.
                self._get_block_id_with_writing_policy(address)
                if block is None
                else block.get_id()
            )
            message = {
                "id": core_name,
                "access": AccessType.readmiss,
                "address": address,
                "block_id": block_id,
            }
            self.channel.put(message)
            self.core_board.animation_access("read miss")

        elif op == "WRITE":
            # Get address and data part
            _, value = rest[0].split(";")

            # writemiss  -   If block does not exist at all
            if block is None:
                # Get the key of the block with write policy
                message = {
                    "id": core_name,
                    "access": AccessType.writemiss,
                    "address": address,
                    "value": value,
                    "block_id": self._get_block_id_with_writing_policy(address),
                }
                self.channel.put(message)
                self.core_board.animation_access("write miss")
                return

            # writemiss  -   If block state is O, S or I:
            if block.get_state() not in ["M", "E"]:
                message = {
                    "id": core_name,
                    "access": AccessType.writemiss,
                    "address": address,
                    "value": value,
                    "block_id": block.get_id(),
                }
                self.channel.put(message)
                self.core_board.animation_access("write miss")
                return

            # writehit  -   If block state is M or E:
            # Update block
            self.core_board.animation_access("write hit")
            block_id = block.get_id()
            time.sleep(CACHE_WR_DELAY)
            self.cache.set(block_id, "M", address, value)
            self.cache.animation(block_id, HIGHLIGHT_HIT)

        else:
            raise ValueError(f"Unrecognized instruction: {inst_str}")

    """
    Given an address, this function returns the ID of a block in the cache
    that matches the specified writing policy.
    """

    def _get_block_id_with_writing_policy(self, address):
        # Cast the address to do arithmetic operation
        address = int(address, 2)
        set_num = address % 2
        blocks = self.cache.get_blocks_in_set(set_num)
        writing_policy = ["I", "E", "S", "M", "O"]
        for state in writing_policy:
            for block in blocks:
                if block.get_state() == state:
                    return block.get_id()
        print("Error - Writing Policy")
        return None


class CPU:
    def __init__(self, id, core_board, channel):
        self._id = id
        self._core_board = core_board
        self._controller = Controller(id, core_board, core_board.get_cache(), channel)

    def get_id(self):
        return self._id

    def get_core_board(self):
        return self._core_board

    def get_cache(self):
        return self._controller.cache

    def execute(self):
        self._controller.execute()

    def set_instruction(self):
        # Call the set_instructions method from the MyRandom class to generate the next instruction
        myrandom.set_instruction(self._id, self._core_board.next_instr_stringvar)
