import uvicorn
from fastapi import FastAPI, HTTPException
from ws_freshportal.subastas.main import main_subastas
from ws_freshportal.ventas.main import main_ventas
from ws_unosof.dae.main import dae_main
from ws_unosof.clientes.main import main_cst

app = FastAPI (
    title='Web Scraping API',
    description='API desarrollada para extraer informacion de paginas web',
    version='2.0.0'
)

@app.get('/', description='Ruta por defecto')
def default_endpoint():
    try:
        info = [
            {
                "status" : 'ok',
            },
            {
                "message" : "API en ejecucion ..."
            }
        ]
        return info
    except HTTPException as http_ex:
        info = [
            {
                "status" : 'fail'
            },
            {
                "message" : f"La API contiene problemas de ejecución, {http_ex.status_code}"
            }
        ]
        return info
    
@app.get('/extraer-migrar-subastas', description='Ruta para extraer la información de las subastas')
def get_subastas_data():
    try:
        main_subastas()
    except HTTPException as http_ex:
        return { "error" : f"{http_ex.status_code}, {http_ex}" }
    
@app.get('/extraer-migrar-ventas', description='Ruta para extraer la información de las ventas')
def get_ventas_data():
    try:
        main_ventas()
    except HTTPException as http_ex:
        return { "error" : f"{http_ex.status_code}, {http_ex}" }
    
@app.get('/extraer-migrar-dae', description='Ruta para extraer la información de Dae Unosof')
def get_dae_data():
    try:
        dae_main()
    except HTTPException as http_ex:
        return { "error" : f"{http_ex.status_code}, {http_ex}" }
    
@app.get('/extraer-migrar-cst', description='Ruta para extraer la información de Customers Unosof')
def get_ventas_subastas_data():
    try:
        main_cst()
    except HTTPException as http_ex:
        return { "error" : f"{http_ex.status_code}, {http_ex}" }
    
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=9999)