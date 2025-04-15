import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def create_driver_connection_prefs():
    chrome_options = Options()
    chrome_options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

    # Opcional: activa modo visible para pruebas
    # chrome_options.add_argument("--headless=new")  # Si quieres ocultar el navegador pero no es recomendable

    # Directorio de descarga
    download_path = r"C:/Users/mateo/Desktop/Chamba/API/Web-Scraping_API/src/ws_freshportal/subastas"
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    prefs = {
        "download.default_directory": os.path.abspath(download_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,  # Permitir descargas "potencialmente peligrosas"
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,  # Permite múltiples descargas sin permiso
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
    }

    chrome_options.add_experimental_option("prefs", prefs)

    # Para evitar que se detecte el WebDriver
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Eliminar el flag de automatización (opcional pero recomendado)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    return driver

def create_driver_connection():
    options = Options()
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    # chrome_options.add_argument("--headless=new")  # Si quieres ocultar el navegador pero no es recomendable
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # No especificar la versión
    return driver