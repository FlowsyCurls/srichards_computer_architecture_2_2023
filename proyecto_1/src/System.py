import threading
from Processor import Processor
from Bus import Bus
from Utils import NUM_CPU
import time


class System:
    def __init__(self, cache_frames, memory_frame):
        self.bus = Bus(memory_frame)
        self.num_processors = NUM_CPU
        self.cache_frames = cache_frames
        # Creamos 4 instancias de Procesador
        self.processors = [
            Processor(i, self.bus, self.cache_frames[i])
            for i in range(self.num_processors)
        ]
        # Creamos un hilo para cada instancia de Procesador
        self.threads = [threading.Thread(target=p.execute) for p in self.processors]
        # Conectamos todos los procesadores al bus
        [self.bus.connect(p) for p in self.processors]
        # Empieza en modo manual
        self.auto_mode = False
        # Empezar el bus
        self.bus.run()

    def execute(self):
        # Wait until every processor stopped running
        # while any(processor.controller.running for processor in self.processors):
        #     (
        #         print(processor.id, processor.controller.running)
        #         for processor in self.processors
        #     )
        #     time.sleep(2)

        for processor, thread in zip(self.processors, self.threads):
            if not processor.controller.running:
                thread = threading.Thread(target=processor.execute)
                thread.start()
                self.threads[processor.id] = thread
                time.sleep(0.3)
            else:
                #     # Processor is still running, skip this cycle
                print("Running", processor.id)
                pass

        for thread in self.threads:
            thread.join()

    def execute_auto(self, time_interval):
        self.auto_mode = True
        while self.auto_mode:
            self.execute()
            time.sleep(time_interval)

    def execute_manual(self):
        self.auto_mode = False
        running = True
        while running:
            text = input("Press ENTER to execute one cycle of processors\n\n")
            if text == "s":
                self.bus.state()
                time.sleep(5)
            if text == "q":
                running = False
                continue
            self.execute()
