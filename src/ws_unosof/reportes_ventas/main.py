from database.db_unosof import get_url_login, get_user_login, get_password_login, get_url_data_sales
from services.driver_service import create_driver_connection
from database.db import log_to_db
from utils.mail import send_mail
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from fastapi import HTTPException
import json
import time
from ws_unosof.reportes_ventas.migrate_db import save

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
    
def extract_table_data(driver, fecha_inicio, fecha_fin, nombre_reporte):
    """Extrae los datos de la tabla con BeautifulSoup, agregando fechas y nombre del reporte"""
    scroll_down(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find(id='tblSalesMasterSKU')
    data = []

    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells]
            if row_data:
                # Agregamos columnas adicionales al final de cada fila
                row_data.extend([fecha_inicio, fecha_fin, nombre_reporte])
                data.append(row_data)
    return data

def generate_report(driver, report_name, bo_sample_index, report_id_index=None, fecha_inicio=None, fecha_fin=None):
    """Genera un reporte aplicando el filtro de fechas, basándose en los índices, y extrae los datos."""
    print(f"Generando reporte: {report_name}")

    # 1) Seleccionar el ID de reporte si corresponde
    if report_id_index is not None:
        Select(driver.find_element(By.ID, 'reportID1')).select_by_index(report_id_index)

    # 2) Formatear fechas a string YYYY-MM-DD (o el formato que tu web espere)
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d') if isinstance(fecha_inicio, datetime) else fecha_inicio
    fecha_fin_str    = fecha_fin.strftime('%Y-%m-%d')    if isinstance(fecha_fin,    datetime) else fecha_fin

    # 3) Rellenar los inputs de fecha y disparar el cambio de foco
    inicio_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'dt_search_start')))
    fin_input    = driver.find_element(By.NAME, 'dt_search_end')

    inicio_input.clear()
    inicio_input.send_keys(fecha_inicio_str + Keys.TAB)
    print(f"  Fecha inicio set a: {inicio_input.get_attribute('value')}")

    fin_input.clear()
    fin_input.send_keys(fecha_fin_str + Keys.TAB)
    print(f"  Fecha fin    set a: {fin_input.get_attribute('value')}")

    # 4) Seleccionar el sample y generar el reporte
    Select(driver.find_element(By.ID, 'bo_sample')).select_by_index(bo_sample_index)
    driver.find_element(By.NAME, 'generateReport_1').click()

    # 5) Esperar a que la tabla esté lista y extraer
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "tblSalesMasterSKU")))
    data = extract_table_data(driver, fecha_inicio_str, fecha_fin_str, report_name)
    print(f"[{report_name}] Filas extraídas: {len(data)}")
    return {"reporte": report_name, "datos": data}

def scrape_data(driver):
    """Realiza el scraping de múltiples reportes con rango de fechas"""
    try:
        login(driver)

        today = datetime.today().date()
        start_date = (today - timedelta(days=45))  # Fecha inicial fija: 2024-01-01
        end_date = start_date  # El rango será de un solo día

        driver.get(get_url_data_sales())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()
        driver.get(get_url_data_sales())

        all_data = []

        while start_date <= today:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            print(f"Extrayendo datos del rango de fechas: {start_date_str} a {end_date_str}")

            reportes = [
                ("standing_order", 2, 45),
                ("open_market", 3, None),
                ("prebook", 6, None),
            ]

            day_data = []  # Datos específicos del día actual

            for nombre, bo_index, rep_index in reportes:
                # Ahora generate_report se encarga de aplicar las fechas antes de generar
                data = generate_report(driver, nombre, bo_index, rep_index, start_date_str, end_date_str)
                
                # Filtrar filas ignorando las que contienen palabras clave
                filtered_data = [
                    row for row in data["datos"] if not ignore_text(row)
                ]
                data["datos"] = filtered_data
                day_data.append(data)

            # Guardar los datos del día en la base de datos
            save(day_data)
            print(f"Datos del día {start_date_str} guardados en la base de datos.")

            # Agregar los datos del día al conjunto total
            all_data.extend(day_data)

            # Avanzar al siguiente día
            start_date += timedelta(days=1)
            end_date = start_date  # Mantener el rango de un día
        
        return all_data

    except Exception as e:
        print(f"Error al realizar el scraping: {e}")
    finally:
        driver.quit()
        
def scrape_data_day_by_day(driver):
    """Realiza el scraping de múltiples reportes con rango de fechas día por día desde 2024-01-01 hasta hoy."""
    try:
        login(driver)

        today = datetime.today().date()
        start_date = datetime(2025, 3, 1).date()  # Fecha inicial fija: 2024-01-01
        end_date = start_date  # El rango será de un solo día

        driver.get(get_url_data_sales())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()
        driver.get(get_url_data_sales())

        all_data = []

        while start_date <= today:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            print(f"Extrayendo datos del rango de fechas: {start_date_str} a {end_date_str}")

            reportes = [
                ("standing_order", 2, 45),
                ("open_market", 3, None),
                ("prebook", 6, None),
            ]

            day_data = []  # Datos específicos del día actual

            for nombre, bo_index, rep_index in reportes:
                # Ahora generate_report se encarga de aplicar las fechas antes de generar
                data = generate_report(driver, nombre, bo_index, rep_index, start_date_str, end_date_str)
                
                # Filtrar filas ignorando las que contienen palabras clave
                filtered_data = [
                    row for row in data["datos"] if not ignore_text(row)
                ]
                data["datos"] = filtered_data
                day_data.append(data)

            # Guardar los datos del día en la base de datos
            save(day_data)
            print(f"Datos del día {start_date_str} guardados en la base de datos.")

            # Agregar los datos del día al conjunto total
            all_data.extend(day_data)

            # Avanzar al siguiente día
            start_date += timedelta(days=1)
            end_date = start_date  # Mantener el rango de un día
        
        return all_data

    except Exception as e:
        print(f"Error al realizar el scraping: {e}")
    finally:
        driver.quit()

def sales_main():
    driver = create_driver_connection()
    datos_reporte = scrape_data_day_by_day(driver)
    # save(datos_reporte)  # Guardar datos en la base de datos
    return datos_reporte

def ignore_text(row):
    """Ignora filas que no contienen datos relevantes."""
    list_keywords = [
        "LADY IN GREEN TOTALS",
        "LYSIMACCHIA RAINBOW TOTALS",
        "LYSIMACCHIA TINT TOTALS",
        "LYSIMACCHIA WHITE TOTALS",
        "MILLION STARS TOTALS",
        "MILLION STARS GLIT TOTALS",
        "MILLION STARS TINT TOTALS",
        "MILLION STARS TINT + GLIT TOTALS",
        "XLENCE TOTALS",
        "XLENCE ARCOIRIS TOTALS",
        "XLENCE ARCOIRIS + GLIT TOTALS",
        "XLENCE MULTI COLOR TOTALS",
        "XLENCE TINT TOTALS",
        "XLENCE TINT + GLIT TOTALS",
        "XLENCE TINT IMM TOTALS",
        "XLENCE GLIT TOTALS	",
        "XLENCE MULTI COLOR + GLIT TOTALS",
        "XLENCE GLIT TOTALS",
        "ANTURIO TOTALS",
        "BROMELIA TOTALS",
        "CASCARA PINO TOTALS",
        "CLOUD TOTALS",
        "ORQUIDEA TOTALS",
        "ORQUIDEA REPOSICION TOTALS",
        "VARA ORQUIDEA TOTALS",
        "DELPHINIUM SEA WALTZ TOTALS",
        "DELPHINIUM TRITON TOTALS",
        "DELPHINIUM SKY WALTZ TOTALS",
        "DIANTHUS KIWI BOOM TOTALS",
    ]
    
    # Verifica si alguna palabra clave está en la fila
    return any(keyword in row for keyword in list_keywords)