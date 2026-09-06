import re
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_datetime
from PIL import Image, UnidentifiedImageError

from apps.accounts.models import User
from apps.core.image_validators import (
    ALLOWED_IMAGE_FORMATS,
    MAX_IMAGE_BYTES,
    MAX_IMAGE_DIMENSION,
)
from apps.posts.content_import import clean_text
from apps.posts.models import Category, Post
from apps.posts.taxonomy import STRUCTURAL_CATEGORIES, CategorySlug

EXPECTED_POST_COUNTS = {"builds": 9, "guides": 6, "reviews": 4}
EDITORIAL_AUTHOR_EMAIL = "editorial-author@example.invalid"
EDITORIAL_AUTHOR_USERNAME = "editorial-author"

EDITORIAL_POSTS = (
    {
        "slug": "cafe-racer-de-garaje",
        "title": "Café racer de garaje: una base honesta",
        "excerpt": "Decisiones simples para convertir una base usada en una moto que quieras seguir manejando.",
        "content": (
            "El proyecto no arrancó con un catálogo de accesorios en la mano ni buscando llamar la atención "
            "en redes sociales, sino con una premisa mucho más pragmática: postura de manejo y confiabilidad "
            "mecánica. Rescatamos una base japonesa de cuatro cilindros que llevaba años guardada bajo una lona "
            "en un galpón húmedo. Antes de cortar el primer tubo del subchasis o desarmar la pintura original, "
            "revisamos el tren delantero, cambiamos los rodamientos cónicos de dirección y purgamos el líquido "
            "de frenos apelmazado.\n\n"
            "A menudo el error más común al encarar una café racer es desarmar la moto completa el primer fin "
            "de semana sin un plan de ensamble claro. Nosotros optamos por la disciplina inversa: cada modificación "
            "debía permitir que la moto arrancara y rodara a la cuadra siguiente. Fabricamos soportes mínimos en "
            "chapa de acero para reubicar la batería debajo del colín artesanal, instalamos semimanillares con "
            "un ángulo relajado para no castigar las muñecas en ciudad y calibramos la tensión de la cadena.\n\n"
            "Cuando llegó la hora de rodar en ruta abierta hacia las sierras, el resultado confirmó las horas de "
            "banco de trabajo. La moto se siente compacta, rígida y previsible en cada apoyo. No es una máquina "
            "para ganar carreras de aceleración ni para exhibirla en vitrinas; es una moto de garaje construida "
            "con honestidad, lista para encender en el primer intento y devorar kilómetros al atardecer."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-03T12:00:00+00:00",
        "image": "source/builds/build-01.webp",
        "alt": "Café racer negra en restauración dentro de un taller luminoso.",
    },
    {
        "slug": "frenos-antes-de-potencia",
        "title": "Frenos antes de potencia",
        "excerpt": "La mejora que más transforma una moto vieja no siempre está en el motor.",
        "content": (
            "En cualquier construcción clásica existe la tentación inmediata de buscar más caballos de fuerza: "
            "filtros de admisión directa, escapes abiertos y chicleres de mayor caudal. Sin embargo, en el "
            "asfalto real, la verdadera velocidad y la confianza para inclinar la moto nacen de la capacidad "
            "de detenerla con precisión milimétrica cuando el tráfico o una curva ciega lo exigen.\n\n"
            "Desmontamos el sistema hidráulico original de cuatro décadas, cuyos sellos de goma estaban "
            "cristalizados y las mangueras de caucho se deformaban bajo presión. Reemplazamos las líneas viejas "
            "por latiguillos trenzados de acero inoxidable de calidad aeronáutica, instalamos una bomba radial "
            "moderna de tacto progresivo y reconstruimos las pinzas con pistones nuevos y pastillas sinterizadas "
            "de compuesto blando.\n\n"
            "El cambio en la dinámica de manejo fue instantáneo. La maneta ya no tiene ese tacto esponjoso que "
            "obliga a bombear en bajadas pronunciadas; ahora basta la fuerza de dos dedos para modular la "
            "deceleración con total serenidad. Poder frenar tarde y con control absoluto permite disfrutar del "
            "chasis y evaluar el rendimiento del motor con una tranquilidad que ninguna modificación de potencia "
            "puede comprar."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-10T12:00:00+00:00",
        "image": "source/builds/build-02.webp",
        "alt": "Detalle de una café racer preparada en un banco de trabajo.",
    },
    {
        "slug": "cableado-que-se-puede-reparar",
        "title": "Cableado que se puede reparar al costado de la ruta",
        "excerpt": "Un arnés claro y documentado es una mejora de seguridad, no un detalle estético.",
        "content": (
            "No hay nada más frustrante que quedarse varado al costado de una ruta secundaria al caer la noche "
            "por culpa de un fusible derretido o un cable sulfatado dentro de un manojo enredado con cinta "
            "aisladora vieja. En este taller consideramos que el sistema eléctrico es una pieza de ingeniería "
            "que merece tanta prolijidad y respeto como la soldadura del chasis.\n\n"
            "Eliminamos el laberinto de cables resecos de fábrica y diseñamos un arnés minimalista desde cero. "
            "Empleamos conductores de cobre estañado de grado automotriz con códigos de color normalizados, "
            "termocontraíble con adhesivo interno para sellar cada empalme contra la humedad y conectores "
            "estancos multipin accesibles sin necesidad de desmontar el depósito de combustible.\n\n"
            "Junto con la instalación de un módulo de encendido electrónico y un panel de fusibles compacto, "
            "dibujamos un diagrama en papel laminado que guardamos debajo del asiento junto a una pequeña lámpara "
            "de prueba. Si surge un inconveniente a trescientos kilómetros de casa, cualquier diagnóstico toma "
            "cinco minutos con una llave allen y un destornillador plano."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-17T12:00:00+00:00",
        "image": "source/builds/build-03.webp",
        "alt": "Motocicleta café racer y herramientas ordenadas en un taller.",
    },
    {
        "slug": "asiento-y-postura-para-rutas-cortas",
        "title": "Asiento y postura para rutas cortas",
        "excerpt": "Cómo encontrar una posición compacta sin convertir cada salida en una negociación con la espalda.",
        "content": (
            "La silueta plana y agresiva es el sello visual inconfundible del café racer tradicional, pero "
            "construir una moto vistosa que resulte insoportable después de quince kilómetros es un fracaso "
            "de diseño. Encontrar el triángulo ergonómico ideal entre puños, asiento y estriberas requiere "
            "paciencia, mediciones en estático y varias pruebas sobre el asfalto.\n\n"
            "Comenzamos moldeando la base del asiento sobre el chasis recortado utilizando láminas de fibra "
            "para copiar con exactitud las curvas del cuadro. Para el relleno combinamos dos capas: una base "
            "de espuma de polietileno de alta densidad para evitar que la estructura toque fondo en baches "
            "secos, y una capa superior viscoelástica moldeada a mano que distribuye la presión de manera homogénea.\n\n"
            "El tapizado en cuero rústico hidrofugado, cosido con hilo encerado en patrón acanalado transversal, "
            "ofrece el agarre justo para no deslizarse hacia atrás en aceleraciones firmes. La distancia a los "
            "semimanillares permite flexionar los codos naturalmente sin sobrecargar las palmas, logrando una "
            "máquina que se puede disfrutar tanto un domingo en la sierra como en un trayecto urbano cotidiano."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-24T12:00:00+00:00",
        "image": "source/builds/build-04.webp",
        "alt": "Café racer de perfil en un taller de restauración.",
    },
    {
        "slug": "checklist-para-salir-el-fin-de-semana",
        "title": "Checklist para salir el fin de semana",
        "excerpt": "Una rutina de diez minutos para arrancar con menos sorpresas y más ganas de rodar.",
        "content": (
            "Una escapada de fin de semana en una moto clásica no empieza cuando abrís el acelerador en el peaje "
            "de la autopista, sino la tarde previa en la tranquilidad del garaje. Dedicar diez minutos a una "
            "verificación metódica ahorra horas de espera en la banquina y permite salir a la ruta con la "
            "mente completamente despejada.\n\n"
            "Seguimos una rutina en círculo alrededor de la máquina: chequeo de presión y desgaste de neumáticos "
            "en frío, tensión y lubricación de cadena de transmisión, nivel de aceite motor con la moto a nivel, "
            "recorrido libre de cables de embrague y acelerador, y comprobación de luces de giro, posición y "
            "freno trasero. Un torque rápido a las tuercas de los ejes y soportes de motor cierra la inspección "
            "mecánica básica.\n\n"
            "Por último, verificamos la documentación obligatoria, el seguro al día, un botiquín compacto y "
            "un juego de herramientas elementales con fusibles de repuesto, alambre de fardo y cinta autosoldable. "
            "Con la máquina a punto y el bolso ajustado sobre el colín, solo resta esperar que aclare para "
            "salir a buscar las curvas."
        ),
        "category": CategorySlug.GUIDES,
        "published_at": "2026-03-03T12:00:00+00:00",
        "image": "source/guides/guide-01.webp",
        "alt": "Café racer preparada junto a una ruta de montaña al amanecer.",
    },
    {
        "slug": "mapa-papel-y-ruta-secundaria",
        "title": "Mapa de papel y ruta secundaria",
        "excerpt": "Elegir caminos tranquilos vuelve más memorable una salida incluso cuando el destino es cercano.",
        "content": (
            "Las aplicaciones de navegación satelital en teléfonos inteligentes son extraordinarias para "
            "encontrar el camino más rápido entre dos puntos en hora pico, pero la filosofía del café racer "
            "consiste exactamente en lo opuesto: buscar el camino más interesante, aunque implique demorarse "
            "dos horas más para llegar al mismo café de pueblo.\n\n"
            "Desplegar un mapa de rutas de papel sobre el banco de trabajo antes de salir permite descubrir "
            "trazados alternativos que los algoritmos descartan por lentos: caminos vecinales de asfalto rugoso, "
            "puentes ferroviarios olvidados y curvas que siguen la topografía natural de los ríos sin terraplenes "
            "de concreto. Marcar con lápiz los puntos de reabastecimiento de combustible asegura autonomía sin "
            "ansiedad.\n\n"
            "Llevar el mapa doblado en la ventana transparente del bolso de tanque te conecta con el territorio "
            "de una manera física y atenta. Preguntar indicaciones a los lugareños en una estación de servicio "
            "rural abre conversaciones genuinas y consejos sobre parajes que no figuran en ninguna guía turística "
            "digital."
        ),
        "category": CategorySlug.GUIDES,
        "published_at": "2026-03-10T12:00:00+00:00",
        "image": "source/guides/guide-02.webp",
        "alt": "Motocicleta junto a una carretera de montaña y un mapa de ruta.",
    },
    {
        "slug": "como-fotografiar-tu-moto-sin-estudio",
        "title": "Cómo fotografiar tu moto sin estudio",
        "excerpt": "Luz suave, fondo simple y un encuadre bajo bastan para mostrar las proporciones reales.",
        "content": (
            "Documentar las horas de trabajo dedicadas a una construcción no requiere cámaras cinematográficas "
            "costosas ni reflectores de estudio fotográfico. El mejor fotómetro disponible es la luz natural del "
            "atardecer y el ojo crítico del propio constructor que conoce cada ángulo y cada línea de tensión del "
            "chasis.\n\n"
            "El error más habitual es disparar de pie con la cámara a la altura del pecho, lo que deforma la "
            "perspectiva y hace que la moto parezca aplastada contra el suelo. Agachate hasta que el lente quede "
            "a la altura del centro del motor o del eje de las ruedas; esa perspectiva baja resalta la horizontalidad "
            "del tanque, la postura del asiento y el despeje del colín con respecto a la rueda trasera.\n\n"
            "Buscá fondos despejados: una pared de ladrillo visto desgastado, un portón de chapa oxidada o un "
            "mirador serrano al final de la tarde donde la luz lateral rasante dibuje las sombras de las aletas del "
            "cilindro. Evitá postes que parezcan brotar del asiento y limpiá los neumáticos con un trapo antes de "
            "obturar para que el trabajo resalte con toda su pureza."
        ),
        "category": CategorySlug.GUIDES,
        "published_at": "2026-03-17T12:00:00+00:00",
        "image": "source/guides/guide-03.webp",
        "alt": "Café racer estacionada frente a un paisaje de montaña sereno.",
    },
    {
        "slug": "una-cafe-racer-para-la-ciudad",
        "title": "Reseña: una café racer para la ciudad",
        "excerpt": "Ágil, ligera y directa: qué se gana y qué se resigna al usarla todos los días.",
        "content": (
            "Convivir a diario en el denso tránsito urbano sobre una café racer de geometrías puras es una "
            "experiencia radicalmente diferente a desplazarse en un vehículo utilitario moderno con arranque "
            "silencioso y suspensiones acolchadas. Aquí no hay filtros electrónicos, modos de conducción ni "
            "asistencias intrusivas.\n\n"
            "Entre semáforos y avenidas congestionadas, el radio de giro limitado de los semimanillares y el "
            "calor que sube de las aletas de refrigeración exigen compromiso físico y concentración constante. "
            "A cambio, la estrechez del chasis permite serpentear con soltura entre carriles y la respuesta "
            "instantánea de los carburadores de tiro directo regala una conexión sensorial que vuelve emocionante "
            "hasta el trayecto más monótono de la rutina laboral.\n\n"
            "Si estás dispuesto a aceptar una postura inclinada hacia adelante y un embrague que pide mano firme, "
            "la recompensa es incomparable: cada esquina de la ciudad se siente viva y el sonido seco del escape "
            "cono inverso rebotando contra los edificios de concreto te recuerda por qué elegiste andar en moto y "
            "no mirar la vida a través del parabrisas de un auto."
        ),
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-03-24T12:00:00+00:00",
        "image": "source/reviews/review-01.webp",
        "alt": "Café racer junto a un camino costero al atardecer azul.",
    },
    {
        "slug": "viajar-liviano-en-dos-ruedas",
        "title": "Reseña: viajar liviano en dos ruedas",
        "excerpt": "Una prueba de equipaje mínimo para escapadas de una noche sin cargar la moto de más.",
        "content": (
            "Nos propusimos recorrer seiscientos kilómetros de rutas secundarias a lo largo de un fin de semana "
            "llevando únicamente lo que entrara en una bolsa tubular compacta de veinte litros atada sobre el colín "
            "de aluminio. El objetivo de la prueba era verificar si es posible hacer mototurismo genuino sin "
            "desvirtuar la esencia deportiva y despojada de una máquina café racer.\n\n"
            "Al no cargar peso parásito en los laterales, el chasis conservó su agilidad intacta en los tramos "
            "trabados de montaña. Entrar en curvas enlazadas con una moto que frena donde querés y apoya sin "
            "oscilaciones de cola demuestra que la carga excesiva es el principal enemigo del placer de conducir "
            "en dos ruedas.\n\n"
            "En el destino, desatar una sola correa y tener el bolso al hombro en diez segundos mientras la moto "
            "descansa en la puerta de una hostería serrana confirma la tesis: la libertad no se mide por la cantidad "
            "de comodidades que transportás, sino por la liviandad con la que podés moverte por el mapa."
        ),
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-03-31T12:00:00+00:00",
        "image": "source/reviews/review-02.webp",
        "alt": "Motocicleta café racer frente al horizonte del mar.",
    },
    {
        "slug": "cuando-un-proyecto-esta-listo",
        "title": "Reseña: cuándo un proyecto está listo",
        "excerpt": "No existe el último tornillo perfecto; sí existe el momento de salir a manejar.",
        "content": (
            "Hay una trampa psicológica común en el mundo de las motos artesanales que los constructores experimentados "
            "conocen bien: el perfeccionismo paralizante. La búsqueda obsesiva de pulir un detalle milimétrico más o "
            "esperar una pieza inconseguible importada del exterior puede retrasar meses, o incluso años, el debut de una "
            "máquina sobre el asfalto.\n\n"
            "Sometimos a prueba una construcción que aún conservaba marcas de soldadura cruda en el escape y un tanque con "
            "pintura base mate sin barnizar. Salimos a rodarla por autopistas rápidas y caminos de ripio compacto para "
            "exigir el conjunto y anotar rigurosamente solo aquello que comprometiera la seguridad de frenado, la "
            "estabilidad de dirección o la fiabilidad de carga de la batería.\n\n"
            "Los detalles estéticos menores pueden —y deben— evolucionar con el tiempo y los kilómetros compartidos. Una "
            "moto que rueda con pequeñas imperfecciones tiene un alma infinitamente superior a una que descansa impecable "
            "pero estéril en un soporte de taller. La obra se completa verdaderamente en la ruta, con viento en el pecho "
            "y el cuentavueltas trepando hacia la línea roja."
        ),
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-04-07T12:00:00+00:00",
        "image": "source/reviews/review-03.webp",
        "alt": "Café racer estacionada en un mirador de costa al anochecer.",
    },
    {
        "slug": "un-taller-que-invita-a-volver",
        "title": "Un taller que invita a volver",
        "excerpt": "Unas pocas decisiones de orden vuelven el espacio más seguro, sereno y fácil de habitar.",
        "content": (
            "El garaje no es únicamente el lugar donde se guardan herramientas y repuestos viejos; es el santuario "
            "donde el tiempo se detiene, la cabeza se despeja y las manos se concentran en una sola tuerca a la vez. "
            "Cuando el desorden se apodera del banco de trabajo, la fatiga mental aparece antes de haber ajustado la "
            "primera pieza.\n\n"
            "Reorganizamos el espacio bajo una premisa sencilla: cada herramienta debe tener una posición asignada al "
            "alcance de la mano derecha mientras la moto descansa sobre el caballete central. Colocamos tableros fenólicos "
            "con siluetas marcadas para llaves combinadas y tubos, bandejas magnéticas para no perder arandelas durante "
            "el desarme y una iluminación cenital neutra que elimina sombras molestas sobre los carburadores.\n\n"
            "También reservamos un rincón limpio, lejos del polvo de la amoladora y las virutas de metal, con una pava "
            "eléctrica para el café, una libreta de hojas cuadriculadas y espacio suficiente para dar un paso atrás y "
            "observar la línea de la moto con perspectiva. Un taller bien pensado te invita a quedarte hasta tarde "
            "trabajando con entusiasmo y sin apuro."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-04-14T12:00:00+00:00",
        "image": "source/builds/build-05.webp",
        "alt": "Proyecto de motocicleta en un taller ordenado y luminoso.",
    },
    {
        "slug": "neumaticos-para-las-rutas-que-haces",
        "title": "Neumáticos para las rutas que hacés",
        "excerpt": "Una forma práctica de equilibrar agarre, confianza y duración para usar la moto todos los días.",
        "content": (
            "Es habitual ver construcciones custom equipadas con neumáticos de dibujo antiguo o cubiertas de tacos pesados "
            "pensadas exclusivamente para impactar en fotografías estáticas. Pero cuando el asfalto se humedece con el "
            "rocío matinal o la ruta presenta grietas longitudinales y parches de brea, la elección del caucho define la "
            "línea entre disfrutar el trazado o manejar con tensión innecesaria.\n\n"
            "Para nuestros proyectos de media cilindrada seleccionamos compuestos modernos de carcasa diagonal que respetan "
            "el perfil clásico de época pero incorporan polímeros de sílice de última generación. Este diseño garantiza una "
            "temperatura de trabajo rápida incluso en mañanas frías y evacua el agua con eficacia mediante surcos continuos "
            "que no comprometen la superficie de contacto en inclinación.\n\n"
            "Verificar las presiones de inflado en frío con un manómetro de precisión antes de cada jornada es el hábito "
            "más rentable para la seguridad. Mantener dos libras menos adelante para mejorar la huella en curva y la "
            "presión recomendada atrás para no deformar la carcasa transforma por completo la agilidad del tren delantero "
            "en los cambios de dirección rápidos."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-04-21T12:00:00+00:00",
        "image": "source/builds/build-06.webp",
        "alt": "Primer plano de una rueda y un neumático de motocicleta dentro de un taller.",
    },
    {
        "slug": "mandos-simples-para-manejar-concentrado",
        "title": "Mandos simples para manejar concentrado",
        "excerpt": "Los controles claros hacen que una moto preparada sea más confiable en cada salida.",
        "content": (
            "En una motocicleta clásica de espíritu purista, el manillar debe ser una extensión limpia y directa de las "
            "intenciones del piloto. Las piñas de conmutadores plásticas sobredimensionadas y los manojos de cables "
            "sujetos con precintos desprolijos rompen la pureza de la línea de visión e introducen puntos potenciales "
            "de falso contacto eléctrico.\n\n"
            "Reemplazamos los mandos comerciales por microinterruptores metálicos de pulsador integrados de forma oculta "
            "en el interior de los tubos del semimanillar. Cada cable viaja enfundado hacia una unidad de control compacta "
            "bajo el tanque, reduciendo el puesto de mando a lo estrictamente esencial: un acelerador de tiro rápido de "
            "aluminio mecanizado, manetas forjadas con regulación micrométrica y un único velocímetro analógico central.\n\n"
            "Al eliminar distracciones visuales e instrumentos redundantes, la atención del conductor vuelve a donde "
            "siempre debió estar: en el sonido de las válvulas, la vibración del motor en los estribos y la lectura "
            "continua del asfalto. La simpleza mecánica bien ejecutada transmite una serenidad inigualable cuando la "
            "ruta se abre frente a la rueda delantera."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-04-28T12:00:00+00:00",
        "image": "source/builds/build-07.webp",
        "alt": "Mandos y cables prolijos sobre el manillar de una motocicleta.",
    },
    {
        "slug": "detalles-que-mejoran-con-el-uso",
        "title": "Detalles que mejoran con el uso",
        "excerpt": "Elegí materiales y terminaciones que se vean mejor después de rodar, no solo el primer día.",
        "content": (
            "Existe una diferencia fundamental entre una motocicleta recién pintada para una exposición y una máquina "
            "concebida para sumar miles de kilómetros en el mundo real. Las superficies cromadas en exceso y las "
            "pinturas brillantes inmaculadas sufren con cada impacto de gravilla, mientras que los materiales nobles "
            "adquieren una pátina única y honesta que documenta cada viaje.\n\n"
            "En nuestros ensambles privilegiamos el aluminio cepillado a mano con grano medio, el bronce en casquillos y "
            "tapas de inspección, y el cuero curtido al vegetal sin lacados plásticos. Las partes metálicas pulidas sin "
            "barniz pueden reacondicionarse en diez minutos con una pasta abrasiva suave y un paño de lana, recuperando su "
            "brillo satinado después de una tormenta de lluvia y barro.\n\n"
            "Con el paso de las temporadas, el roce de las botas sobre los laterales del cárter, el oscurecimiento del "
            "cuero donde asientan los guantes y las tonalidades doradas que toma el colector de escape de acero inoxidable "
            "cuentan una historia que ningún catálogo comercial puede replicar. La verdadera belleza mecánica es aquella "
            "que madura junto a su dueño en la carretera."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-05-05T12:00:00+00:00",
        "image": "source/builds/build-08.webp",
        "alt": "Detalle de terminaciones cuidadas en una motocicleta preparada.",
    },
    {
        "slug": "equipaje-liviano-para-una-salida-de-dia",
        "title": "Equipaje liviano para una salida de día",
        "excerpt": "Llevá lo esencial sin convertir una salida corta en un ejercicio de logística.",
        "content": (
            "El encanto primordial de una moto ligera y despojada se arruina en cuanto intentás cargar alforjas voluminosas "
            "o mochilas pesadas que desequilibran el centro de gravedad y fatigan los hombros en las primeras cien millas "
            "de curvas. Aprender a viajar liviano es una disciplina de discernimiento entre lo que realmente necesitás y lo "
            "que llevás por temor infundado.\n\n"
            "Para una jornada completa de ruta basta con un bolso de herramientas cilíndrico sujeto a la horquilla o bajo el "
            "colín, y una bolsa estanca pequeña amarrada firmemente con correas de trinquete sobre el asiento del acompañante. "
            "Adentro: una capa impermeable respirable para imprevistos climáticos, agua fresca, documentación en bolsa sellada "
            "y una multiherramienta de calidad con alicate y puntas intercambiables.\n\n"
            "Al mantener el peso bajo y centrado en la masa de la motocicleta, la suspensión trabaja en su rango óptimo y "
            "la moto conserva su agilidad milimétrica en las transiciones de curva a curva. Menos bultos implican menos "
            "preocupaciones en cada parada y más atención puesta en el disfrute puro del asfalto."
        ),
        "category": CategorySlug.GUIDES,
        "published_at": "2026-05-12T12:00:00+00:00",
        "image": "source/guides/guide-04.webp",
        "alt": "Motocicleta con equipaje liviano estacionada junto a una ruta abierta.",
    },
    {
        "slug": "leer-la-ruta-antes-de-la-curva",
        "title": "Leer la ruta antes de la curva",
        "excerpt": "Un hábito silencioso que mejora ritmo, posición y confianza.",
        "content": (
            "El manejo fluido y seguro sobre dos ruedas no depende de reflejos sobrehumanos ni de maniobras bruscas de "
            "último segundo, sino de la capacidad anticipatoria de la mirada. Donde van tus ojos va la rueda delantera; si te "
            "concentrás en el borde del asfalto o en la piedra que querés esquivar, la física de la moto te llevará directamente "
            "hacia ella.\n\n"
            "Entrená la visión para proyectarse cincuenta o cien metros adelante, buscando el punto de fuga donde la curva parece "
            "cerrarse o abrirse. Leé las pistas que ofrece el entorno: la línea de postes de telégrafo, las copas de los árboles "
            "en el horizonte o el brillo del pavimento anticipan el radio de giro mucho antes de que el cartel vial sea legible.\n\n"
            "Al entrar en la curva con la velocidad adecuada y la marcha engranada que mantenga el motor en su rango de par útil, "
            "podés soltar los frenos con suavidad y acelerar de manera progresiva desde el ápice hacia la salida. La conducción "
            "se convierte en una danza armónica donde cada movimiento se encadena con naturalidad y sin sobresaltos."
        ),
        "category": CategorySlug.GUIDES,
        "published_at": "2026-05-19T12:00:00+00:00",
        "image": "source/guides/guide-05.webp",
        "alt": "Motociclista acercándose a una ruta rural con curvas.",
    },
    {
        "slug": "chequeo-de-cinco-minutos-despues-de-rodar",
        "title": "Chequeo de cinco minutos después de rodar",
        "excerpt": "Detectá detalles pequeños mientras la salida todavía está fresca en la memoria.",
        "content": (
            "Cuando volvés de una jornada de varios cientos de kilómetros y apagás el motor en el garaje, la tentación inmediata "
            "es sacarse el casco, dejar las llaves sobre la mesa y cerrar la puerta hasta el próximo sábado. Sin embargo, los cinco "
            "minutos posteriores a la detención son el momento más valioso para la salud mecánica de tu moto.\n\n"
            "Con el motor aún caliente y las vibraciones frescas en el cuerpo, recorré la máquina con la vista y la punta de los "
            "dedos: revisá si hay sudoraciones de aceite en las juntas de culata o tapas de balancines, verificá que los tornillos "
            "del silenciador de escape sigan firmes y comprobá la temperatura de los discos de freno para descartar pistones "
            "trabados que arrastren fricción.\n\n"
            "Aprovechá que la cadena de transmisión está caliente para aplicar una pasada uniforme de lubricante; el calor del "
            "metal dilata los retenes de goma y permite que el aceite penetre en los rodillos antes de enfriarse. Resolver cualquier "
            "desajuste menor esa misma tarde garantiza que la próxima salida comience con la moto lista para arrancar sin contratiempos."
        ),
        "category": CategorySlug.GUIDES,
        "published_at": "2026-05-26T12:00:00+00:00",
        "image": "source/guides/guide-06.webp",
        "alt": "Persona revisando una motocicleta después de una salida.",
    },
    {
        "slug": "la-salida-que-inicia-la-historia",
        "title": "Reseña: la salida que inicia la historia",
        "excerpt": "Una moto directa y con carácter para cuando la ciudad empieza a quedar atrás.",
        "content": (
            "Hay un instante exacto en cada viaje largo en el que las torres de departamentos y el smog del tráfico periférico "
            "desaparecen del espejo retrovisor y el aire cambia de temperatura y aroma. El motor se estabiliza en su régimen de "
            "crucero armónico, los neumáticos toman calor y el ruido mental del trabajo diario se apaga por completo.\n\n"
            "Esta máquina no persigue cifras extravagantes en una ficha técnica de revista comercial ni pretende competir con "
            "potencias electrónicas de doscientos caballos. Su magia reside en la honestidad de su respuesta mecánica: cada "
            "milímetro que girás el puño derecho se traduce en empuje firme y noble, mientras el chasis tubular transmite con "
            "fidelidad lo que sucede bajo las ruedas sin artificios digitales.\n\n"
            "Cuando el sol se esconde en el horizonte y la ruta te ofrece un desvío de ripio hacia un viejo parador de campo, "
            "sabés que tomaste la decisión correcta. No hay apuro por llegar; la verdadera recompensa es el camino elegido y la "
            "certeza de que, al día siguiente, volverás al garaje a planear la próxima salida por el camino más largo."
        ),
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-06-02T12:00:00+00:00",
        "image": "source/reviews/review-04.webp",
        "alt": "Motociclista recorriendo una ruta abierta durante la hora dorada.",
    },
    {
        "slug": "una-lista-de-trabajo-que-si-terminas",
        "title": "Una lista de trabajo que sí terminás",
        "excerpt": "Dividí un proyecto grande en pasos seguros y visibles para mantener el impulso.",
        "content": (
            "Los talleres y garajes particulares del mundo entero están llenos de proyectos que comenzaron con "
            "desbordante entusiasmo y terminaron abandonados en cajas de cartón cubiertas de polvo. El factor decisivo "
            "entre una moto que vuelve a rodar y una que termina vendida por piezas no es el presupuesto ni la herramienta "
            "más cara, sino la metodología con la que se administra el tiempo de trabajo.\n\n"
            "Nuestro método divide la restauración en tres etapas cerradas y consecutivas: primero la salud motriz y la "
            "seguridad dinámica (frenos, rodamientos, suspensiones y compresión de motor); segundo la ergonomía y la "
            "instalación eléctrica; y solo al final los acabados estéticos, pintura y tapicería. Cada etapa debe concluir "
            "con una prueba de rodaje funcional antes de autorizar la apertura del siguiente paquete de tareas.\n\n"
            "Anotar cada avance en una pizarra visible del taller y marcar las tareas cumplidas genera una inercia positiva "
            "que combate la frustración en los días difíciles. Saber exactamente qué tornillo vas a ajustar antes de apagar "
            "la luz del garaje garantiza que la próxima sesión empiece con determinación y sin vacilaciones."
        ),
        "category": CategorySlug.BUILDS,
        "published_at": "2026-06-09T12:00:00+00:00",
        "image": "source/builds/build-09.webp",
        "alt": "Motocicleta preparada lista para una revisión final de taller.",
    },
)

LEGACY_AUTHOR_EMAILS = ("portfolio-author@example.invalid",)

LEGACY_SLUGS = {
    "review-una-cafe-racer-para-la-ciudad": "una-cafe-racer-para-la-ciudad",
    "review-viajar-liviano-en-dos-ruedas": "viajar-liviano-en-dos-ruedas",
    "review-cuando-un-proyecto-ya-esta-listo": "cuando-un-proyecto-esta-listo",
    "garage-layout-that-keeps-you-moving": "un-taller-que-invita-a-volver",
    "choosing-tires-for-real-roads": "neumaticos-para-las-rutas-que-haces",
    "the-case-for-simple-controls": "mandos-simples-para-manejar-concentrado",
    "finishing-details-that-age-well": "detalles-que-mejoran-con-el-uso",
    "a-build-list-you-can-finish": "una-lista-de-trabajo-que-si-terminas",
    "packing-light-for-a-day-ride": "equipaje-liviano-para-una-salida-de-dia",
    "reading-the-road-before-the-corner": "leer-la-ruta-antes-de-la-curva",
    "a-five-minute-post-ride-check": "chequeo-de-cinco-minutos-despues-de-rodar",
    "review-the-ride-that-starts-the-story": "la-salida-que-inicia-la-historia",
}


def validate_editorial_dataset(assets_dir):
    expected_categories = set(EXPECTED_POST_COUNTS)
    category_counts = Counter()
    seen_slugs = set()
    errors = []

    for item in EDITORIAL_POSTS:
        slug = item.get("slug", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            errors.append(f"Invalid editorial slug: {slug!r}.")
        elif slug in seen_slugs:
            errors.append(f"Duplicate editorial slug: {slug}.")
        seen_slugs.add(slug)

        category = str(item.get("category", ""))
        if category not in expected_categories:
            errors.append(f"Unsupported editorial category for {slug}: {category!r}.")
        else:
            category_counts[category] += 1

        for field in ("title", "excerpt", "content", "alt"):
            try:
                clean_text(item.get(field), field=f"{slug}.{field}")
            except ValidationError as error:
                errors.append(f"Invalid editorial text for {slug}: {error.messages[0]}")

        if parse_datetime(item.get("published_at", "")) is None:
            errors.append(f"Invalid publication datetime for {slug}.")

        image_name = item.get("image", "")
        expected_prefix = f"source/{category}/"
        if not isinstance(image_name, str) or not image_name.startswith(
            expected_prefix
        ):
            errors.append(f"Invalid asset path for {slug}: {image_name!r}.")
            continue
        asset_path = assets_dir / image_name
        if not asset_path.is_file():
            errors.append(f"Missing editorial asset for {slug}: {image_name}.")
            continue
        if asset_path.stat().st_size > MAX_IMAGE_BYTES:
            errors.append(f"Editorial asset is too large for {slug}: {image_name}.")
            continue
        try:
            with Image.open(asset_path) as image:
                image_format = image.format
                image_size = image.size
                image.verify()
        except UnidentifiedImageError, OSError, ValueError:
            errors.append(f"Invalid editorial image for {slug}: {image_name}.")
            continue
        if image_format not in ALLOWED_IMAGE_FORMATS:
            errors.append(
                f"Unsupported editorial image format for {slug}: {image_name}."
            )
        if max(image_size) > MAX_IMAGE_DIMENSION:
            errors.append(
                f"Editorial image exceeds maximum dimensions for {slug}: {image_name}."
            )

    if dict(category_counts) != EXPECTED_POST_COUNTS:
        errors.append(
            "Unexpected editorial category distribution: "
            f"expected {EXPECTED_POST_COUNTS}, got {dict(category_counts)}."
        )
    if errors:
        raise CommandError("\n".join(errors))


def migrate_legacy_slugs(author):
    legacy_authors = User.objects.filter(email__in=LEGACY_AUTHOR_EMAILS)
    if legacy_authors.exists():
        Post.objects.filter(author__in=legacy_authors).update(author=author)

    migrated = 0
    for legacy_slug, current_slug in LEGACY_SLUGS.items():
        if Post.objects.filter(slug=current_slug).exists():
            continue
        legacy_post = Post.objects.filter(slug=legacy_slug, author=author).first()
        if legacy_post is None:
            continue
        legacy_post.slug = current_slug
        legacy_post.save(update_fields=["slug"])
        migrated += 1
    return migrated


class Command(BaseCommand):
    help = "Create the idempotent public editorial dataset and upload its images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate the editorial dataset and assets without writing to the database.",
        )

    def handle(self, *args, **options):
        assets_dir = Path(settings.BASE_DIR) / "assets" / "editorial"
        validate_editorial_dataset(assets_dir)

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Editorial dataset validated: {len(STRUCTURAL_CATEGORIES)} categories and "
                    f"{len(EDITORIAL_POSTS)} posts."
                )
            )
            return

        with transaction.atomic():
            author, _ = User.objects.get_or_create(
                email=EDITORIAL_AUTHOR_EMAIL,
                defaults={
                    "username": EDITORIAL_AUTHOR_USERNAME,
                    "display_name": "Caffeine Lane",
                },
            )
            author.is_staff = False
            author.is_superuser = False
            author.set_unusable_password()
            author.save(update_fields=["is_staff", "is_superuser", "password"])

            migrated_legacy_slugs = migrate_legacy_slugs(author)

            categories = {}
            for category in STRUCTURAL_CATEGORIES:
                categories[category.slug], _ = Category.objects.update_or_create(
                    slug=category.slug,
                    defaults={
                        "name": category.name,
                        "description": category.description,
                    },
                )

            for item in EDITORIAL_POSTS:
                existing_post = (
                    Post.objects.filter(slug=item["slug"])
                    .only("pk", "author_id")
                    .first()
                )
                if existing_post is not None and existing_post.author_id != author.pk:
                    raise CommandError(
                        "Refusing to overwrite a post owned by another author: "
                        f"{item['slug']}."
                    )
                post, _ = Post.objects.update_or_create(
                    slug=item["slug"],
                    defaults={
                        "title": item["title"],
                        "excerpt": item["excerpt"],
                        "content": item["content"],
                        "author": author,
                        "status": Post.Status.PUBLISHED,
                        "published_at": parse_datetime(item["published_at"]),
                        "featured_image_alt": item["alt"],
                    },
                )
                post.categories.set([categories[item["category"]]])
                if not post.featured_image:
                    asset_path = assets_dir / item["image"]
                    post.featured_image.save(
                        item["image"], ContentFile(asset_path.read_bytes()), save=True
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Editorial dataset ready: {len(STRUCTURAL_CATEGORIES)} categories and "
                f"{len(EDITORIAL_POSTS)} posts; {migrated_legacy_slugs} legacy URLs updated."
            )
        )
