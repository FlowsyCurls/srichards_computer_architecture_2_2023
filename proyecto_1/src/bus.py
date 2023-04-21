import time
from src.utils import (
    CACHE_RD_DELAY,
    CACHE_WR_DELAY,
    HIGHLIGHT_INV,
    HIGHLIGHT_READ,
    HIGHLIGHT_RQ,
    HIGHLIGHT_WB,
    HIGHLIGHT_WRITE,
    MEM_DELAY,
    NUM_CPU,
    PROCESS_DELAY,
    AccessType,
)


class Bus:
    def __init__(self, memory_board, channel, cores):
        super().__init__()
        self.memory_board = memory_board
        self.channel = channel
        self.cores = cores

    def get_core_cache(self, id):
        return self.cores[id].get_cache()

    def get_mem_data(self, address):
        return self.memory_board.get_data(address)

    def process_tasks(self):
        time.sleep(PROCESS_DELAY)

        # Clear colored blocks
        self._clear_animation()

        for message in iter(self.channel.get, None):
            access = message["access"]

            # If its a CALC, just pass
            if access == AccessType.calc:
                continue

            # Get the core cache
            core_id = int(message["id"][1])
            local_cache = self.get_core_cache(core_id)

            # Get important information
            block_id = message["block_id"]
            address = message["address"]

            # Block destructuring
            block = local_cache.get_block_by_id(block_id)
            state = block.get_state()
            data = block.get_data()

            # If a readmiss is given
            if access == AccessType.readmiss:
                self._process_readmiss(
                    core_id, local_cache, block_id, state, address, data
                )

            # If a writemiss is given
            elif access == AccessType.writemiss:
                # Obtain value to write
                value = message["value"]
                self._process_writemiss(
                    core_id, local_cache, block_id, state, address, data, value
                )

            else:
                print(f"Error access - '{access}' not found.")

    """ 
    This function processes a readmiss message by updating the cache state
    and data for the specified block.
    """

    def _process_readmiss(self, core_id, local_cache, block_id, state, address, data):
        # If I do read and if I am writing on M or O I must do WB
        if state in ["M", "O"]:
            self._perfom_wb(dirty_address=address, dirty_data=data)

        # Now ask check if other cores has the block:
        owned_data = self._seek_owned(address, core_id)

        # If sponsors state is O or M then set block state to S
        if owned_data is not None:
            time.sleep(CACHE_RD_DELAY)
            local_cache.set(block_id, "S", address, owned_data)
            local_cache.animation(block_id, HIGHLIGHT_READ)

        # If no sponsors
        else:
            # Check if address is E or S in another node
            # and save that value to the local cache in S state
            shared_data = self._seek_shared(address, core_id)
            if shared_data is not None:
                time.sleep(CACHE_WR_DELAY)
                local_cache.set(block_id, "S", address, shared_data)
                local_cache.animation(block_id, HIGHLIGHT_WRITE)

            # Then no one have the value, read from memory then set block state to E
            else:
                # Read from memory
                mem_data = self.get_mem_data(address)
                time.sleep(MEM_DELAY)
                self.memory_board.animation(address, HIGHLIGHT_READ)
                time.sleep(CACHE_WR_DELAY)
                local_cache.set(block_id, "E", address, mem_data)
                local_cache.animation(block_id, HIGHLIGHT_WRITE)

    """
    This function processes a writemiss message by updating the cache state
    and data for the specified block, and broadcasting a message to other
    caches to invalidate their copies of the block.
    """

    def _process_writemiss(
        self, core_id, local_cache, block_id, state, address, data, value
    ):
        # If state is O, then do a WB
        if state in ["O", "M"]:
            self._perfom_wb(address, data)

        # Now write in the block and save the changes in the local cache
        time.sleep(CACHE_WR_DELAY)
        local_cache.set(block_id, "M", address, value)
        local_cache.animation(block_id, HIGHLIGHT_WRITE)

        # Finally tell others to invalidate this block
        self._seek_invalidate(address, core_id)

    def _clear_animation(self):
        # Clear animation in memory and each core
        self.memory_board.clear_animation()
        [core.get_core_board().clear_animation() for core in self.cores]

    def _perfom_wb(self, dirty_address, dirty_data):
        self.memory_board.set_data(dirty_address, dirty_data)
        # Set board color
        time.sleep(MEM_DELAY)
        self.memory_board.animation(dirty_address, HIGHLIGHT_WB)

    def _seek_owned(self, local_address, requester_id):
        # search for block that can gives the value - Owned or Modified
        for core_id in range(NUM_CPU):
            if core_id != requester_id:
                local_cache = self.get_core_cache(core_id)
                block = local_cache.get_block_by_address(local_address)

                # If block is not in core[i], then continue
                if block is None:
                    continue

                # If block is in core[i], then verify state.
                state = block.get_state()
                address = block.get_address()

                # If block is M or O, then set state to O and give value
                if local_address == address and state in ["M", "O"]:
                    block.set_state("O")
                    time.sleep(CACHE_RD_DELAY)
                    local_cache.animation(block.get_id(), HIGHLIGHT_RQ)
                    return block.get_data()

        # If we arrive here it means that no core has an O or M block of this address.
        return None

    def _seek_shared(self, local_address, requester_id):
        # search for block that can gives the value - Owned or Modified
        for core_id in range(NUM_CPU):
            if core_id != requester_id:
                local_cache = self.get_core_cache(core_id)
                block = local_cache.get_block_by_address(local_address)

                # If block is not in core[i], then continue
                if block is None:
                    continue

                # If block is in core[i], then verify state.
                state = block.get_state()
                address = block.get_address()

                # If block is E or S then give value
                if local_address == address and state in ["E", "S"]:
                    time.sleep(CACHE_RD_DELAY)
                    block.set_state("S")
                    local_cache.animation(block.get_id(), HIGHLIGHT_RQ)
                    return block.get_data()

        # If we arrive here it means that no core has an E, S block of this address.
        return None

    def _seek_invalidate(self, local_address, requester_id):
        # search for this block in each core and invalidate it
        # search for block that can gives the value - Owned or Modified
        for core_id in range(NUM_CPU):
            if core_id != requester_id:
                local_cache = self.get_core_cache(core_id)
                block = local_cache.get_block_by_address(local_address)

                # If block is not in core[i], then continue
                if block is None:
                    continue

                # If block is in core[i], then invalidate
                if block.get_state() == "I":
                    return

                block.set_state("I")
                time.sleep(CACHE_WR_DELAY)
                local_cache.animation(block.get_id(), HIGHLIGHT_INV)
