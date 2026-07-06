import logging
import json

def load_topology(config,key):
    try:
        with open(config["topology_file"], "r", encoding="utf-8") as topology_file:
            dict=json.load(topology_file)
            return dict[key]
    except Exception as error:
        logging.critical(f"¡¡¡FATAL ERROR!!! ... NO SE ENCONTRARON LOS ARCHIVOS DE INFRAESTRUCTURA {error}", exc_info=True)
        raise