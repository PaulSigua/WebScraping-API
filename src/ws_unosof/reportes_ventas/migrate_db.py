from database.db_unosof import execute_query, insert_data_sales, delete_data_sales
from datetime import datetime, timedelta

def create_table():
    # SQL query to create the table
    create_table_query = """
        CREATE TABLE rptUnosof_Reportes_Ventas_Orden_Permanente (
            rvent_id INT IDENTITY(1,1) PRIMARY KEY,
            rvent_sku_producto VARCHAR(MAX) NOT NULL,
            rvent_tallos_vendidos INT,
            rvent_tallos_porcentaje DECIMAL(5,2),
            rvent_dolares_vendidos DECIMAL(10,2),
            rvent_dolares_porcentaje DECIMAL(5,2),
            rvent_precio_medio DECIMAL(10,4),
            rvent_precio_medio_cm DECIMAL(10,4),
            rvent_fecha_inicio DATE NOT NULL,
            rvent_fecha_fin DATE NOT NULL,
            rvent_nombre_reporte VARCHAR(100) NOT NULL
        );
    """
    # Execute the query to create the table
    execute_query(create_table_query)
    
def delete_old_records():
    """Elimina registros antiguos de la tabla rptUnosof_Reportes_Ventas_Orden_Permanente."""
    fecha_limite = (datetime.now() - timedelta(days=46)).strftime('%Y-%m-%d')
    delete_data_sales((fecha_limite,))
    
def save(data):
    try:
        
        # if data:
        #     delete_old_records()
            
        def clean_decimal(value):
            if value is None or str(value).strip() == "":
                print("Valor vacío o nulo: ", value)
                return None
            value = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
            try:
                return float(value)
            except ValueError as e:
                print(f"Error al convertir a decimal: {e}")
                print(f"Valor problemático: {value}")
                return None

        def clean_int(value):
            if value is None or str(value).strip() == "":
                return None
            value = str(value).strip().replace(".", "").replace(",", "")
            try:
                return int(value)
            except ValueError:
                return None

        def clean_date(value):
            if value is None or str(value).strip() == "":
                return None
            for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return None

        for reporte in data:
            reporte_nombre = reporte["reporte"]
            filas = reporte["datos"]
            for row in filas:
                # Aseguramos que tenga al menos 10 columnas (7 datos + 3 metadatos)
                if len(row) < 10:
                    continue

                values = [
                    row[0],                              # sku_producto
                    clean_int(row[1]),                   # tallos_vendidos
                    clean_decimal(row[2]),                 # tallos_porcentaje
                    clean_decimal(row[3]),                 # dolares_vendidos
                    clean_decimal(row[4]),      # dolares_porcentaje
                    clean_decimal(row[5]),                 # precio_medio
                    clean_decimal(row[6]),                 # precio_medio_cm
                    clean_date(row[7]),                  # fecha_inicio
                    clean_date(row[8]),                  # fecha_fin
                    row[9]                               # nombre_reporte
                ]

                print("Valores a insertar: ", values)
                insert_data_sales(values)

    except Exception as e:
        print(f'ERROR: {e}')