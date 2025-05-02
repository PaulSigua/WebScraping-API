import os
import time
from fastapi import HTTPException
from services.driver_service import create_driver_connection_prefs
from database.db import log_to_db
from database.db_freshportal import get_url_login, get_user_login, get_password_login, get_url_data_subastas
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from utils.mail import send_mail
from ws_freshportal.subastas.migrate_db import save

download_dir = os.path.expanduser(r"C:/Users/mateo/Desktop/Chamba/API/Web-Scraping_API/src/ws_freshportal/subastas")

def login(driver):
    try:
        url = str(get_url_login())
        print("URL: ", url)
        driver.get(url)
        username = driver.find_element(By.ID, 'username')
        username.send_keys(get_user_login())
        password = driver.find_element(By.ID, 'password')
        password.send_keys(get_password_login())

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.fps-button'))).click()

    except Exception as e:
        message = f"Error al iniciar sesión en subastas, {e}"
        print(message)

def delete_file():
    # Ruta del archivo que deseas eliminar
    file_path = r"C:/Users/mateo/Desktop/Chamba/API/Web-Scraping_API/src/ws_freshportal/subastas/FloridayIoYieldExcel.xls"

    try:
        # Verifica si el archivo existe
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"El archivo {file_path} ha sido eliminado correctamente.")
        else:
            print(f"El archivo {file_path} no existe.")
    except Exception as e:
        print(f"Ocurrió un error al intentar eliminar el archivo: {e}")

def wait_table(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ajax_table_table tbody"))
        )
        print("Tabla cargada correctamente")
    except Exception as e:
        print("Error al cargar la tabla:", e)
        driver.quit()

def wait_for_download(download_dir, timeout=50):
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = os.listdir(download_dir)
        # Verifica si hay un archivo con extensión .xls o .xlsx
        if any(file.endswith((".xls", ".xlsx")) for file in files):
            return True
        time.sleep(1)
    raise Exception("El archivo no se descargó en el tiempo esperado")

def generate_url_base(start, end):
    base_url = get_url_data_subastas()
    if not base_url:
        raise ValueError("La base URL obtenida de la base de datos es inválida.")
    return base_url.format(start_date=start, end_date=end)

def generate_url():
    try:
        today = datetime.today().date()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        # start_date = datetime(2025, 1, 1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        # end_date = datetime(2025, 1,13).strftime('%Y-%m-%d')
        url = generate_url_base(start_date, end_date)
        if not url:
            raise ValueError("La URL generada es inválida o está vacía.")
        return url
    except Exception as e:
        print(f"ERROR, al generar la fecha o la URL: {e}")
        # Retorna un valor por defecto para evitar el error
        return "about:blank/error"
    
def get_file():
    try:
        delete_file()
        driver = create_driver_connection_prefs()
        login(driver)
        url = generate_url()
        print("URL: ", url)
        driver.get(url)
        wait_table(driver)
        time.sleep(10)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'export'))
            ).click()
            time.sleep(10)
            print(f"Ingreso al primer try")
        except Exception as e:
            print(f"ERROR, ocurrió un error mientras esperaba el botón exportar: {e}")

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.export_excel.btn-export"))
            ).click()
            wait_for_download(download_dir)
            print(f"Ingreso al segundo try")
            time.sleep(5)
        except Exception as e:
            print(f"ERROR, esperando el boton descargar: {e}")

    except Exception as e:
        message = f'Error al realizar webscraping de las subastas: ', e
        print(message)
        log_to_db(1, 'ERROR', message, 'get_file', 500)
        send_mail(message)
        
    finally:
        driver.close()
        driver.quit()
        
def main_subastas():
    try:
        get_file()
        save()
        print('Proceso finalizado')
    except HTTPException as e:
        message = f'ERROR Web Scraping {e}'
        print(message)
        send_mail(message)
        log_to_db(1, 1, 'ERROR', message, 'main_subastas()', e.status_code)