from database.db_unosof import get_url_login, get_user_login, get_password_login, get_url_data_sales
from services.driver_service import create_driver_connection
from database.db import log_to_db
from utils.mail import send_mail
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from fastapi import HTTPException
import time

def login(driver):
    """Realiza el inicio de sesión en la plataforma."""
    try:
        driver.get(get_url_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Login"))).click()
        print("Inicio de sesión exitoso.")
    except Exception as e:
        print(f'ERROR al iniciar sesion: {e}')
        raise e
    
def scroll_down(driver):
    """Desplaza la página hacia abajo."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 2).until(lambda d: d.execute_script("return document.readyState") == "complete")
    
def scrape_data(driver):
    """Realiza el web scraping de los reportes con fechas cada 30 días."""
    try:
        login(driver)

        today = datetime.today().date()
        start_date = today - timedelta(days=45)
        end_date = today + timedelta(days=2)

        driver.get(get_url_data_sales())

        # Iniciar sesión en la plataforma en caso de error
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()

        driver.get(get_url_data_sales())

        while start_date <= today:
            # Formatear las fechas a cadenas de texto
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            print(f"Extrayendo datos del rango de fechas: {start_date_str} a {end_date_str}")

            # Rellenar el formulario con las fechas
            fechaInicio = driver.find_element(By.NAME, 'dt_search_start')
            fechaInicio.clear()
            fechaInicio.send_keys(start_date_str)
            fechaFin = driver.find_element(By.NAME, 'dt_search_end')
            fechaFin.clear()
            fechaFin.send_keys(end_date_str)
            
            # Configurar filtros y generar reporte
            Select(driver.find_element(By.ID, 'bo_sample')).select_by_index(1)
            Select(driver.find_element(By.ID, 'reportID1')).select_by_index(45)
            driver.find_element(By.NAME, 'generateReport_1').click()
            
            # Esperar carga del reporte
            time.sleep(10)
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "tblSalesMasterSKU")))

            # Extraer datos del reporte
            scroll_down(driver)
            contenidoPagina = driver.page_source
            soup = BeautifulSoup(contenidoPagina, "html.parser")

            data = []
            table = soup.find(id='tblSalesMasterSKU')
            if table:
                rows = table.find_all("tr")  # Extraer todas las filas de la tabla
                
                for row in rows:
                    # Extraer todas las celdas <td> en cada fila
                    cells = row.find_all("td", {"class": "noclass"})
                    row_data = [cell.text.strip() for cell in cells]  # Extraer el texto de cada celda y eliminar espacios extra
                    if row_data:  # Asegurarse de que la fila no esté vacía
                        data.append(row_data)
                        
                print(f"Datos extraídos: {data}")
            
            print(f'Se extrajeron {len(data)} filas de datos.')
            return data

    except Exception as e:
        error_msg = f"Error al realizar el scraping: {e}"
        print(error_msg)
    finally:
        driver.quit()
        
def sales_main():
    driver = create_driver_connection()
    data = scrape_data(driver)
    return data