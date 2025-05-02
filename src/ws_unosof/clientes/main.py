from database.db_unosof import (
    get_url_login, 
    get_user_login, 
    get_password_login, 
    get_url_data_cst
)
from utils.mail import send_mail
from ws_unosof.clientes.migrate_db import save
from services.driver_service import create_driver_connection
from fastapi import HTTPException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from database.db import log_to_db

def login(driver):
    """Realiza el inicio de sesión en la plataforma."""
    try:
        driver.get(get_url_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Login"))).click()
        print("Inicio de sesión exitoso.")
    except HTTPException as e:
        error_msg = f"Error al iniciar sesión: {e}"
        print(error_msg)
        raise e

def scroll_down(driver):
    """Desplaza la página hacia abajo."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 2).until(lambda d: d.execute_script("return document.readyState") == "complete")

def scrape_data(driver):
    """Realiza el web scraping de los reportes."""

    login(driver)
    try:

        driver.get(get_url_data_cst())

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_password_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()

        driver.get(get_url_data_cst())
        
        # Esperar a que el elemento de Status esté presente
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "bo_active")))
        
        # Crear un objeto Select
        select = Select(element)

        # Seleccionar la opción con el índice 0
        select.select_by_index(0)
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "SearchCustomers"))).click()

        # Espera hasta que el elemento tblCustomers esté presente
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tblCustomers")))

        scroll_down(driver)

        contenido_pagina = driver.page_source
        soup = BeautifulSoup(contenido_pagina, 'html.parser')

        data = []
        table = soup.find(id='tblCustomers')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all("td")
                row_data = [cell.text.strip() for cell in cells]
                if row_data:
                    data.append(row_data)
        else:
            print("No se encontraron filas con datos.")

        print("Data de los customers, ", data)
        return data

    except Exception as e:
        error_msg = f"Error al realizar el scraping: {e}"
        print(error_msg)
        raise e
    finally:
        driver.close()
        driver.quit()  # Cerrar navegador siempre
        print("Conexiones cerradas")
        
def main_cst():
    """Función principal para ejecutar el scraping y guardar los datos."""
    try:
        driver = create_driver_connection()
        data = scrape_data(driver)
        save(data)
        print('Proceso finalizado')
    except HTTPException as e:
        message = f'ERROR Web Scraping Clientes: {e}'
        print(message)
        send_mail(message)
        log_to_db(2, 1, message, 'ERROR', 'main_cst()', e.status_code)