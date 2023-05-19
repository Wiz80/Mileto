# Mileto

El pronóstico de demanda de energía a corto plazo es necesario debido a la necesidad por parte del mercado de energía mayorista en el caso de Colombia XM de recibir estimaciones esperadas fiables de parte de los operadores de red. Esto debido a que si no se hace de esta forma se tienen que incurrir en costosos mecanismos de respaldo para suplir la diferencia de generación y demanda. 

Este es un proyecto de grado de la Universidad Industrial de Santander con el objetivo de que se puedan entrenar, testear y comparar modelos de machine learning desde una interfaz amigable e intuitiva 

Este proyecto de Django utiliza una base de datos de postgresql para guardar los datos estructurados de demanda de energía eléctrica y se conecta a una instancia de Google Drive a través de Google Cloud para guardar los modelos y los datos con los que se entrenaron. Se utiliza docker-compose para realizar el despliegue de la aplicación usando un servicio web (django), uno de postgreSQL y uno de nginx como servidor para la redicrección de peticiones http. 

Se puede ingresar desde las instalaciones de la universidad a mileto.com.co para ver la documentación y realizar las respectivas pruebas sobre el proyecto, esto debido a que se cuenta con unas restricciones para el despliegue a nivel general

Para más información contactame: harrihoyos2680@gmail.com
