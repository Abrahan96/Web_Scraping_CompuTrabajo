# Guía para sustentar el primer entregable

## Idea principal

El programa consulta una página de Computrabajo, convierte su HTML en un objeto navegable, encuentra las tarjetas repetidas de empleo, guarda cuatro campos y limpia el resultado con Pandas.

```text
URL -> requests -> HTML -> BeautifulSoup -> lista -> DataFrame -> CSV
```

## Cómo explicar cada archivo

### 1. `src/conexion.py`

- `crear_slug()` adapta el puesto al formato de la URL.
- `construir_url()` une la dirección base, el puesto y la página.
- `conectar()` utiliza `requests.get()`.
- `timeout=20` evita esperar indefinidamente.
- `raise_for_status()` detecta respuestas HTTP con error.
- Los bloques `except` muestran mensajes comprensibles.

### 2. `src/exploracion.py`

- `crear_soup()` transforma el texto HTML en un árbol.
- `find_all()` busca todos los elementos que coinciden.
- El contenedor repetible es `article` con clase `box_offer`.
- Dentro de cada tarjeta buscamos el título, empresa y ubicación.
- `urljoin()` convierte enlaces relativos en enlaces completos.

### 3. `src/limpieza.py`

- `pd.DataFrame()` convierte la lista de diccionarios en una tabla.
- `fillna()` reemplaza valores nulos temporalmente.
- `str.strip()` elimina espacios al inicio y al final.
- `drop_duplicates()` elimina ofertas repetidas.
- `reset_index()` vuelve a numerar las filas.
- `to_csv()` guarda el resultado limpio.

### 4. `main.py`

Ejecuta el proceso en este orden:

1. Solicitar el puesto con `input()`.
2. Conectar.
3. Crear el objeto `soup`.
4. Explorar el HTML.
5. Extraer las ofertas.
6. Guardar JSON crudo.
7. Crear y limpiar el DataFrame.
8. Guardar CSV.

Si el usuario presiona Enter sin escribir un puesto, el programa utiliza `analista de datos` como valor predeterminado. Esto evita que se construya una URL vacía.

## Preguntas probables

### ¿Por qué se utiliza BeautifulSoup y no Selenium?

Porque las ofertas que necesitamos ya aparecen en el HTML descargado. Selenium se utiliza cuando el contenido requiere JavaScript, clics, desplazamiento o inicio de sesión.

### ¿Qué significa HTTP 200?

La solicitud fue recibida y respondida correctamente por el servidor.

### ¿Qué es el contenedor repetible?

Es la etiqueta HTML que se repite por cada oferta. En este portal es `article.box_offer`.

### ¿Por qué guardar JSON antes de limpiar?

Para conservar una copia cercana a la fuente. Si una regla de limpieza resulta incorrecta, podemos volver a procesar el JSON sin consultar nuevamente la web.

### ¿Por qué también guardar CSV?

Porque es fácil de revisar en Excel y representa el resultado tabular limpio.

### ¿Por qué todavía no se usa POO?

Porque este avance tiene pocos pasos y no necesita mantener objetos con estado. Las funciones son suficientes, más fáciles de aprender y coherentes con el nivel actual del curso.

### ¿Qué limitación tiene este avance?

Solo analiza las tarjetas del listado. Todavía no visita el detalle de cada oferta ni identifica habilidades.

## Demostración recomendada

```powershell
python main.py
python -m tests.pruebas_terminal
```

Durante la demostración señala:

1. El puesto ingresado dinámicamente.
2. El código HTTP 200.
3. La cantidad de tarjetas encontradas.
4. Un registro de la lista de diccionarios.
5. La cantidad de filas antes y después de limpiar.
6. Los archivos JSON y CSV generados.
7. Las cinco pruebas con resultado `OK`.
