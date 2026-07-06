import logging
import json

def load_branches(config):
    try:
        with open(config["branches_file"], "r", encoding="utf-8") as file:
            branches = json.load(file)
        return branches
    except Exception as error:
        logging.critical("\n" + "=" * 60 + f"❌ ¡¡¡ERROR AL CARGAR EL ARCHIVO BRANCHES !!!\n: {error}\n" + "=" * 60 + "\n" ,exc_info=True)
        raise