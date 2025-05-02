from fastapi import HTTPException
from services.driver_service import create_driver_connection
from database.db import log_to_db
from database.db_freshportal import get_url_login, get_url_data_ventas, get_user_login, get_password_login
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils.mail import send_mail
from ws_freshportal.ventas.migrate_db import save

def login(driver):
    try:
        driver.get(get_url_login())
        print("Iniciando sesion")
        # Iniciar sesión
        username = driver.find_element(By.ID, 'username')
        username.send_keys(get_user_login())
        password = driver.find_element(By.ID, 'password')
        password.send_keys(get_password_login())

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.fps-button'))).click()
        
    except Exception as e:
        print("Ocurrio un error al iniciar sesion, ", e)

def generate_url_base(start, end):
    base_url = get_url_data_ventas()
    if not base_url:
        raise ValueError("La base URL obtenida de la base de datos es inválida.")
    return base_url.format(start_date=start, end_date=end)

def generate_url():
    try:
        today = datetime.today().date()
        start_date = (today - timedelta(days=15)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        url = generate_url_base(start_date, end_date)
        # print(f"URL: ", url)
        if not url:
            raise ValueError("La URL generada es inválida o está vacía.")
        return url
    except Exception as e:
        print(f"ERROR, al generar la fecha o la URL: {e}")
        # Retorna un valor por defecto para evitar el error
        return "about:blank/error"
    
def scroll_down(driver):
    """Desplaza la página hacia abajo."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 2).until(lambda d: d.execute_script("return document.readyState") == "complete")
    
def scrape_table(driver):
    try:
        driver.get(generate_url())

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "management_total_table"))
        )

        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        table = soup.find(id='management_total_table')
        
        scroll_down(driver)

        if not table:
            print("No se encontró la tabla en la página.")
            raise ValueError("Tabla no encontrada.")

        rows = []
        max_columns = 0

        # Obtener todas las filas y omitir la primera y la última
        table_rows = table.find_all('tr')[1:-1]

        # Procesar las filas restantes
        for row in table_rows:
            cells = row.find_all(['td', 'th'])
            cell_values = [cell.get_text(strip=True) for cell in cells]
            max_columns = max(max_columns, len(cell_values))
            rows.append(cell_values)

        data = []

        for row in rows:
            # print('FILA: ', row)
            data.append(row)

        return data
    
    except Exception as e:
        print(f"ERROR, {e}")
        
def scraple_data():
    try:
        driver = create_driver_connection()
        login(driver)
        data = scrape_table(driver)
        
        driver.close()
        driver.quit()
        
        return data
    except Exception as e:
        print(f'ERROR: {e}')
        
def main_ventas():
    try:
        data = scraple_data()
        save(data)
        print('Proceso finalizado')
    except HTTPException as e:
        message = f'ERROR Web Scraping Fresh-portal Ventas {e}'
        print(message)
        send_mail(message)
        log_to_db(1, 2, 'ERROR', message, 'main_ventas()', e.status_code)