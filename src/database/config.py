from src.utils import get_path

TORTISE_ORM = {
    "connections": {"default": f"sqlite://{get_path('vsingerboard.sqlite3', dir_name='data')}"},
    "apps": {
        "models": {
            "models": ["src.database.model", "aerich.models"],
            "default_connection": "default",
        }
    }
}
