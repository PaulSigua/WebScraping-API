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

# Mapeo de índices de account_rep a sus etiquetas correspondientes
ACCOUNT_REP_NAMES = {
    1: "BMUNZON",
    2: "DABAD",
    3: "DMARTINEZ",
    4: "FVRIES",
    5: "MCRESPO",
    6: "PBARRERA",
    7: "TSONNABEND",
}

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
    """Extrae los datos de la tabla con BeautifulSoup, eliminando duplicados y validando filas."""
    scroll_down(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find(id='tblSalesMasterSKU')
    data = []
    unique_rows = set()  # Para evitar duplicados

    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells]
            if row_data and len(row_data) >= 7:  # Validar que la fila tenga al menos 7 columnas
                # Agregar columnas adicionales al final de cada fila
                row_data.extend([fecha_inicio, fecha_fin, nombre_reporte])
                row_identifier = tuple(row_data[:7])  # Usar las primeras 7 columnas como identificador único
                if row_identifier not in unique_rows:
                    unique_rows.add(row_identifier)
                    data.append(row_data)
    return data


def generate_report(driver, report_name, bo_sample_index, report_id_index, account_rep, fecha_inicio=None, fecha_fin=None):
    """Genera un reporte aplicando el filtro de fechas, índices de sample y account rep, y extrae los datos."""
    rep_label = ACCOUNT_REP_NAMES.get(account_rep, "UNKNOWN")
    print(f"Generando reporte: {report_name} | Sample index: {bo_sample_index} | Account rep: {account_rep} ({rep_label})")

    try:
        # Seleccionar el ID de reporte si corresponde
        if report_id_index is not None:
            Select(driver.find_element(By.ID, 'reportID1')).select_by_index(report_id_index)

        # Formatear fechas a string YYYY-MM-DD
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else ""
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d') if fecha_fin else ""

        # Rellenar los inputs de fecha
        inicio_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'dt_search_start')))
        fin_input = driver.find_element(By.NAME, 'dt_search_end')

        inicio_input.clear()
        inicio_input.send_keys(fecha_inicio_str + Keys.TAB)
        print(f"  Fecha inicio set a: {inicio_input.get_attribute('value')}")

        fin_input.clear()
        fin_input.send_keys(fecha_fin_str + Keys.TAB)
        print(f"  Fecha fin    set a: {fin_input.get_attribute('value')}")

        # Seleccionar el sample y account rep, y generar el reporte
        Select(driver.find_element(By.ID, 'bo_sample')).select_by_index(bo_sample_index)
        Select(driver.find_element(By.ID, 'gu_sales_rep_1')).select_by_index(account_rep)
        driver.find_element(By.NAME, 'generateReport_1').click()

        # Esperar a que la tabla esté lista y extraer los datos
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "tblSalesMasterSKU")))
        data = extract_table_data(driver, fecha_inicio_str, fecha_fin_str, report_name)
        print(f"[{report_name} | Sample {bo_sample_index} | Rep {account_rep} ({rep_label})] Filas extraídas: {len(data)}")

        # Devolver diccionario con etiqueta incluida
        return {
            "reporte": report_name,
            "datos": data,
            "sample": bo_sample_index,
            "account_rep": account_rep,
            "account_rep_label": rep_label
        }
    except Exception as e:
        print(f"Error generando el reporte {report_name} para Sample {bo_sample_index}, Rep {account_rep}: {e}")
        return {
            "reporte": report_name,
            "datos": [],
            "sample": bo_sample_index,
            "account_rep": account_rep,
            "account_rep_label": rep_label
        }


def scrape_data_day_by_day(driver):
    """Realiza el scraping de reportes día por día, iterando sobre samples y account reps."""
    try:
        login(driver)

        today = datetime.today().date()
        start_date = datetime(2025, 1, 1).date()
        end_date = start_date

        driver.get(get_url_data_sales())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()
        driver.get(get_url_data_sales())

        # Definir reportes con (nombre, índice de sample, índice de reportID)
        reportes = [
            ("standing_order", 2, 45),
            ("open_market", 3, None),
            ("prebook", 6, None),
        ]

        while start_date <= today:
            print(f"Extrayendo datos del rango: {start_date} a {end_date}")
            day_data = []

            for nombre, bo_index, report_id_index in reportes:
                # Iterar 7 account reps por cada sample, comenzando en posición 1
                for account_rep in range(1, 8):
                    try:
                        result = generate_report(
                            driver,
                            nombre,
                            bo_index,
                            report_id_index,
                            account_rep,
                            fecha_inicio=start_date,
                            fecha_fin=end_date
                        )
                        # Filtrar filas irrelevantes
                        filtered = [row for row in result["datos"] if not ignore_text(row)]
                        result["datos"] = filtered
                        print(f"Guardado reporte {nombre}, sample {bo_index}, rep {account_rep} ({result['account_rep_label']}) con {len(filtered)} filas.")
                        day_data.append(result)

                        # Guardar los datos extraídos en la base de datos
                        save([result])

                    except Exception as e:
                        print(f"Error generando {nombre} sample {bo_index} rep {account_rep}: {e}")

            start_date += timedelta(days=1)
            end_date = start_date

    except Exception as e:
        print(f"Error al realizar el scraping: {e}")
    finally:
        driver.quit()

def sales_main():
    driver = create_driver_connection()
    datos_reporte = scrape_data_day_by_day(driver)
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