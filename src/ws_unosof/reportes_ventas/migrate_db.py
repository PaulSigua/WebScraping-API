from database.db_unosof import execute_query, insert_data_sales, delete_data_sales, get_report_sales_query
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
            rvent_fecha_inicio_consulta DATE NOT NULL,
            rvent_fecha_fin_consulta DATE NOT NULL,
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
            account_rep_label = reporte["account_rep_label"]

            for row in filas:
                # Aseguramos que tenga al menos 10 columnas (7 datos + 3 metadatos)
                if len(row) < 10:
                    continue

                # Validar si el registro ya existe en la base de datos
                sku_producto = row[0]
                fecha_inicio = clean_date(row[7])
                fecha_fin = clean_date(row[8])
                existing_record = get_report_sales_query(
                    """
                    SELECT rvent_nombre_cuenta_reporte
                    FROM rptUnosof_Reportes_Ventas_Orden_Permanente
                    WHERE rvent_sku_producto = ? AND rvent_fecha_inicio_consulta = ? AND rvent_fecha_fin_consulta = ?
                    """,
                    (sku_producto, fecha_inicio, fecha_fin)
                )

                if existing_record:
                    # Si el registro existe, concatenar las etiquetas si no están ya presentes
                    existing_labels = existing_record[0]["rvent_nombre_cuenta_reporte"]
                    if account_rep_label not in existing_labels:
                        updated_labels = f"{existing_labels} - {account_rep_label}"
                        get_report_sales_query(
                            """
                            UPDATE rptUnosof_Reportes_Ventas_Orden_Permanente
                            SET rvent_nombre_cuenta_reporte = ?
                            WHERE rvent_sku_producto = ? AND rvent_fecha_inicio_consulta = ? AND rvent_fecha_fin_consulta = ?
                            """,
                            (updated_labels, sku_producto, fecha_inicio, fecha_fin)
                        )
                else:
                    # Si el registro no existe, insertar un nuevo registro
                    values = [
                        sku_producto,                      # sku_producto
                        clean_int(row[1]),                 # tallos_vendidos
                        clean_decimal(row[2]),             # tallos_porcentaje
                        clean_decimal(row[3]),             # dolares_vendidos
                        clean_decimal(row[4]),             # dolares_porcentaje
                        clean_decimal(row[5]),             # precio_medio
                        clean_decimal(row[6]),             # precio_medio_cm
                        fecha_inicio,                      # fecha_inicio
                        fecha_fin,                         # fecha_fin
                        reporte_nombre,                     # nombre_reporte
                        f"{account_rep_label}"             # account_rep_label
                    ]

                    print("Insertando valores: ", values)
                    insert_data_sales(values)

    except Exception as e:
        print(f'ERROR al guardar los datos en la base de datos: {e}')