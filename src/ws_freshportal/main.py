from sched import scheduler
from ws_freshportal.ventas.main import main_ventas
from ws_freshportal.subastas.main import main_subastas

def sched_freshportal():
    main_subastas()
    main_ventas()