#import "@preview/min-manual:0.3.0": *

#show: manual.with(
  title: "Bitácora de Cambios",
  description: "Modificaciones realizadas a la implementación de una herramienta web de visualización de datos, que utilice los resultados del modelo",
  authors: "Laboratorio de Desarrollo Regional",
  package: "",
  license: "",
  logo: image("images/lader.jpg")
)

#set text(lang: "es") // Sets the document language to German

#v(1fr)
#outline()
#v(1.2fr)
#pagebreak()

= Solicitudes

Se listan los cambios realizados a la herramienta web de visualización a solicitud del área correspondiente.

== Separación de decimales con punto, no comas
La configuración de separación de decimales con punto depende de la configuración del idioma del navegador donde se visualiza la aplicación. Se sugiere configurar a idioma español su navegador para que la separación sea con puntos.

== Cambiar a un apartado independiente las estimaciones de los modelos lineales

Se agregó una nueva opción a la barra de navegación donde se agregaron los resultados de los pronósticos de cada modelo lineal así como la contribución de cada variable del modelo al pronóstico. 

== Cambio US\$ por USD
En el apartado de la estimación subnacional, se realizó el cambio de texto de US\$ por USD.

== Tablero subnacional : Cambio al PIB Corriente Nacional
Se indica que el PIB Corriente Nacional corresponde a su valor trimestral. Por caracter informativo, no se sugiere presentar el valor trimestral acumulado.

== Ajuste de color de texto en descripción de variables
Se modificó el color de fuente en la descripción de variables del modelol 5.

== Eliminación de descripción de variable repetida
Se eliminó la descripción de la variable FRED PIB trimestral de EEUU por duplicado.

== Agregar fuente de datos para la estimación subnacional
Se agregaron las fuentes de datos utilizadas en la estimación así como la referencia al artículo *Downscaled gridded global dataset for gross domestic product (GDP) per capita PPP over 1990–2022*

== Bucket de respaldo de información de los pronóstico
Se agregó un Bucket en el almacenamiento de objetos de RustFS para contar con un respaldo de los pronósticos de los modelos. Esto con el objetivo de mantener la integridad de los resultados de los pronósticos en caso de existencia de algún evento de corrupción de información.

Se agregó una DAG la cual restaura la información de los últimos pronóstico calculados al Google Sheets que alimenta el Dashboard de visualización de Looker Studio.

== 