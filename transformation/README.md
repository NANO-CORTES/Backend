# Microservicio de Transformación Analítica (ms-transformation)

Este microservicio se encarga procesar y preparar los datos de territorios recibidos de manera que puedan ser evaluados en etapas posteriores. Forma parte integral del pipeline de **Analítica Territorial**, realizando limpieza de datos nulos, de-duplicación, estandarización de cadenas de texto y normalización Min-Max (escala 0.0 a 1.0) utilizando **Pandas**.

---

## 🛠 Requisitos Previos

Asegúrate de contar con las siguientes herramientas instaladas para garantizar un entorno funcional:

- **Python:** Versión `3.11` o superior (Requerido para ejecución nativa local).
- **Gestor de Paquetes Pip:** (Por defecto en Python) para instalación de librerías.
- **Docker y Docker Compose:** En caso de que se desee correr la solución containerizada.
- **Entorno Virtual (Opcional pero recomendado):** Puedes usar `venv` u otras herramientas de ambientes virtuales en Python.

---

## 🚀 Guía de Levantamiento (Ejecución del Servicio)

Existen dos vías principales para levantar este microservicio: de manera nativa (local) o mediante Docker.

### Opción A: Ejecución Local Nativa (Uvicorn)

1. **Abre tu terminal** en la raíz de la carpeta `transformation/`.
2. **Crea y activa un entorno virtual**:
   - *Windows:* `python -m venv venv` y luego `.\venv\Scripts\activate`
   - *Mac/Linux:* `python3 -m venv venv` y luego `source venv/bin/activate`
3. **Instala las dependencias necesarias** listadas en el `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
4. **Levanta el servidor** utilizando Uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *La API estará disponible en: http://localhost:8000 y su documentación Swagger en http://localhost:8000/docs.*

### Opción B: Ejecución en Entorno Dockerizado

El microservicio cuenta con su respectivo `Dockerfile`. Para levantarlo de manera aislada:
1. Asegúrate de que el Engine de Docker esté corriendo.
2. Construye la imagen Docker desde el directorio `transformation/`:
   ```bash
   docker build -t ms-transformation .
   ```
3. Ejecuta el contenedor exponiendo el puerto al de tu máquina:
   ```bash
   docker run -p 8000:8000 ms-transformation
   ```

---

## 🧪 Pruebas del Endpoint (Vía API)

Actualmente, el microservicio recibe un POST con un `dataset_load_id` y procesa los datos internamente. Funciona así:

```bash
# Ejemplo usando cURL hacia el endpoint Local
curl -X POST "http://localhost:8000/api/v1/transform" \
     -H "Content-Type: application/json" \
     -d "{\"dataset_load_id\": \"uuid-1234-5678-test\"}"
```
*(Para facilitar el desarrollo desconectado en esta etapa (HU-07), el endpoint simula el cargado leyendo datos ficticios por debajo a través del método `fetch_mock_dataset`).*

---

## 📂 ¿Cómo probar la Lógica Analítica con un Archivo CSV Manual?

Si tienes un archivo `.csv` real y **necesitas validar la lógica de analítica sin afectar la API actual**, la opción más segura es utilizar un script auxiliar (puedes crear un archivo rápido de python) para inyectar este CSV directo en las funciones maestras de `TransformerService` y arrojar los resultados sin estorbar el código del BackEnd ni sus endpoints HTTP. 

EJECUTA un archivo llamado `test_manual.py` en la raíz de la carpeta `transformation` 

(Para facilidad de lectura, contiene el siguiente código:)

```python
import pandas as pd
from app.services.transformer_service import process_dataset

# 1. Carga aquí tu archivo de prueba (.csv)
# Asegúrate que tenga las columnas mínimas (zone_code, zone_name) y variables numéricas.
path_del_archivo = "mi_archivo_de_prueba.csv"

print(f"[*] Cargando archivo: {path_del_archivo}")
try:
    df_externo = pd.read_csv(path_del_archivo)
    print(f"[*] Filas Iniciales: {len(df_externo)}")

    # 2. Re-usar la lógica real de negocio del microservicio
    df_procesado, reglas_aplicadas = process_dataset(df_externo)

    # 3. Guardar o evaluar el resultado
    df_procesado.to_csv("resultado_limpio.csv", index=False)
    
    print("\n[+] Transformación Finalizada Exitosamente!")
    print(f"[+] Filas Finales luego de quitar duplicados: {len(df_procesado)}")
    print("\n[!] Reglas que fueron aplicadas:")
    for rule in reglas_aplicadas:
        print(f"  - {rule}")
        
    print("\nEl archivo transformado se ha guardado como 'resultado_limpio.csv'.")

except FileNotFoundError:
    print("Error: No se encontró el archivo. Asegúrate que 'mi_archivo_de_prueba.csv' exista en tu carpeta.")
```

**Ejecución:**
```bash
# Correr en la terminal para limpiar y validar el CSV externalmente
python test_manual.py
```
> **Nota de Arquitectura:** Con esta aproximación conservas intacto el archivo `app/api/transform.py` y `app/services/transformer_service.py`, al mismo tiempo que te permite experimentar con *DataFrames* arbitrarios e inspeccionar exhaustivamente la limpieza y estandarización analítica resultando en un .csv pulido que puedes observar en Excel o editores de texto.

---

## 🏗 Pruebas Unitarias Automatizadas (Pytest)

Las reglas de negocio de la transformación y estandarización cuentan con tests verificados usando el entorno Pytest. Para validarlos:

```bash
# En la raíz de transformation/
pytest app/tests/test_transform.py -v
```
Con eso podrás ver las pruebas de `test_standardize_text` (remoción de tildes/espacios) y `test_process_dataset` (normalización Mín/Máx [0.0 - 1.0]).
