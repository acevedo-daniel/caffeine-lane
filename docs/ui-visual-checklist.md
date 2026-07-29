# Lista de comprobación visual

Ejecutar esta lista antes de un release visual. Usar una base recién migrada
para los estados vacíos y `python manage.py seed_portfolio` para los estados
con contenido.

## Viewports

- Móvil: 360 × 800 px.
- Tablet: 768 × 1024 px.
- Escritorio: 1440 × 900 px.

## Páginas y estados

- `/`, `/home/`, `/about/` y `/contact/`: contenido normal, formulario vacío y
  formulario con errores.
- `/posts/search/`: sin consulta, sin resultados, resultados y paginación.
- `/posts/category/builds/`, `/guides/` y `/reviews/`: con contenido y vacías.
- Detalle de una publicación: imagen, extracto largo, comentarios, usuario
  anónimo y usuario autenticado.
- `/accounts/login/`, `/accounts/register/`, recuperación de contraseña y
  perfil: formularios válidos, errores de campo y error general.
- Errores `/400`, `/403`, `/404` y `/500` con `DEBUG=False`.

## Criterios de aceptación

- Header, menú móvil y footer permiten navegar con teclado y tienen foco
  visible; los enlaces internos no devuelven 404 ni 500.
- Tipografía, escala, espaciado, botones, formularios, badges, mensajes y
  paginación mantienen el mismo contraste y radio visual.
- Las tarjetas conservan altura razonable con títulos y extractos largos; cada
  imagen tiene proporción fija, `alt` útil o un placeholder decorativo.
- El carrusel conserva controles con nombre accesible y no tapa texto en móvil.
- No hay scroll horizontal a 360 px, textos cortados ni mezclas involuntarias
  de español e inglés.
- Tab, Shift+Tab y Enter alcanzan todos los controles; el foco tiene contraste
  perceptible.

## Segunda pasada

1. Repetir los tres viewports después de corregir los hallazgos.
2. Verificar saltos visuales al cargar imágenes y al abrir el menú móvil.
3. Revisar únicamente detalles pequeños: alineación, espacios, sombras,
   truncado de texto y estados hover/focus.
