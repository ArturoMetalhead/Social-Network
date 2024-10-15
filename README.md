# Social-Network

## Especificaciones

El proyecto consiste en implementar una red social distribuida para la comunicación siguiendo la idea en la cual se basa Twitter. Siguiendo la filosofı́a de funcionamiento de Twitter, el sistema debe brindar una infraestructura para el manejo de usuarios, de manera que puedan publicar sus mensajes, volver a publicar mensajes que consideren interesantes de otros usuarios y escoger quienes van a ser sus amigos. Además, como parte del manejo de usuarios, se debe proporcionar un mecanismo para la autenticación distribuida de manera tal que se logre un modelo que no sea centralizado.

## Integrantes del equipo

- Carlos Arturo Pérez Cabrera
- Diana Laura Pérez Trujillo

## Funcionalidades

Social-Network simula el funcionamiento de una red social, similar a Twitter. Los usuarios, además de tener una cuenta, pueden realizar publicaciones, seguir a otros usuarios.

### Registro e inicio de sesión

Para crear una cuenta en la plataforma, es necesario que el usuario provea un nombre de usuario (nickname), que debe ser único, una contraseña y una dirección de correo electrónico.

Si ya el usuario tiene una cuenta creada, su primer paso para interactuar con la plataforma debe ser iniciar sesión (login), debe proveer para ello nombre de usuario y contraseña. Solo si ambos son correctos, entonces el user puede acceder al resto de las opciones que la plataforma ofrece.

### Post

El usuario puede realizar publicaciones en su perfil. Los mensajes tienen un límite de caracteres (como sucede en redes sociales como Twitter).

### Seguir y Seguidores

El usuario puede seguir a otros usuarios. Cuando un usuario sigue a otro, puede ver las publicaciones que este sube a su perfil.

### Interacción del usuario

La interacción del usuario con la aplicación será mediante una consola interactiva, donde el usuario podrá escoger que acción realizar a continuación.

## Almacenamiento de la información

Para el diseño y manejo de la base de datos se utilizó Sqlite con la librería Peewee de Python.

Con el objetivo de lograr un almacenamiento distribuido, los servidores que contienen datos se dispusieron en forma de anillo y la búsqueda se realiza mediante una Distributed Hash Table (DHT) con el algoritmo Chord. Un detalle a resaltar es que los nombres de usuario deben ser únicos, por lo que se aprovecha esta propiedad, se utiliza una función de hash, para hashear estos nombres de usuario, y de esa manera decidir qué nodo del Anillo Chord se hará responsable de dicho usuario (incluye todo lo referente a él). Esta distribución ayuda a que exista mayor equilibrio en la cantidad de información almacenada en un nodo.

## Arquitectura

La estructura implementada se basa en las siguientes componentes principales: Operadores o Servers Entry, los Chord Server y los Twitter Server.

### Operadores

Son los encargados de atender a los clientes y responder ante sus solicitudes. Es la capa de comunicación principal entre los clientes y al lógica de la información. Al ser puente, no permite que el cliente tenga interacción directa con las otras componentes, protegiendo así la información y evitando que el cliente pueda acceder a la base de datos de manera directa.

### Chord Server

Son la componente fundamental del sistema y se encarga de la distribución de los nodos en el anillo Chord. Maneja la lógica de un nodo en la red Chord, incluyendo la inserción en la red, el mantenimiento de la tabla de dedos (finger table), y la búsqueda de sucesores. El servidor utiliza sockets para la comunicación entre nodos y emplea múltiples hilos para manejar las solicitudes concurrentes. Implementa funcionalidades como la búsqueda de sucesores, la actualización de la tabla de dedos, y la gestión de réplicas. El código también incluye mecanismos para manejar situaciones de fallo y reintentos en las comunicaciones entre nodos. Además, proporciona funciones para registrarse en puntos de entrada y responder a solicitudes externas.

### Twitter Server

Es el encargado de gestionar la base de datos y todos los pedidos del cliente. Utiliza un sistema de almacenamiento distribuido basado en Chord para manejar los datos de usuarios y tweets. El servidor emplea un mecanismo de autenticación basado en tokens y utiliza hashing para la seguridad de las contraseñas. Implementa un sistema de tareas pendientes para manejar la replicación de datos entre nodos y utiliza comunicación mediante sockets para interactuar con otros nodos de la red. Además, incluye funciones para manejar la transferencia de datos entre nodos y la actualización de información en la red distribuida.

## Descubrimiento y Stalking

Se verifica continuamente si una componente esta disponible en la red. En el caso de que un ChordServer se considere muerto por un EntryPoint, implica que cuando otro ChordServer se quiera introducir al anillo del Chord, el EntryPoint NO le recomendará el IP del ChordServer muerto, sino aleatoriamente otros que estén vivos. De esta manera, se evita los fallos producidos cuando una PC sale del Sistema. Pero en contraposición se genera conexiones extras en el red, lo cual podríamos pensar que recargaría esta.

## Réplicas

Cuando un nuevo nodo del tipo Chord-Twitter quiere entrar en el anillo, puede hacerlo de dos formas: como nuevo nodo o como réplica de uno anterior. Si es un nuevo nodo, deben copiarse a el los datos que le corresponden por su hash asignado. En el otro caso, de insertarse como réplica deben copiarse a él todos los datos del nodo original.

El server contendrá su id, sus sucesores y sus hermanos (nodos que forman parte de la misma componente).

Para realizar una transferencia de datos correcta, el orden en que se transfieran las tablas de la base de datos importa, la tabla de ususarios ha de ser la primera en copiarse. De este modo se van transfiriendo bloques de datos entre una computadora y la otra hasta que se hayan enviado toda la base de datos.

Para la transferencia de datos se requiere que el servidor nuevo envíe su chord_id para que así el otro servidor sepa que porción de la base de datos enviar. Los datos se transfieren en bloques de 20 filas de la tabla cada vez.

## Tolerancia a fallas del sistema

En el momento del envío de cierta información, las componentes implicadas contendrán una lista con las IPs de los servers a los que se puede realizar una consult. Se intenta establecer la comunicación con cada una de estas componentes, una a una, de modo que si la primera falla se pudiera intentar con la segunda. De esta manera, se pueden evitar que el cliente lidie con fallas al intentar conectar con una componente que no esta activa, pues se intentaría con alguna otra.

Sin embargo, hay casos donde es realmente necesario establecer comunicación con una componente específica. Para ello se utiliza un envío persistente que, en dependencia de la prioridad de la tarea, se reintenta la operación luego de pasado un determinado tiempo. Por ejemplo, una réplica que deba actualizar un dato, no es una tarea de altísima prioridad y si una réplica está caída, podría tomar un tiempo reincorporarla, así que se espera un tiempo no tan corto al volver a reintentar la operación. Un caso diferente es a la hora de actualizar la DH, en el momento en que entra un nuevo nodo a la red Chord se intenta persistentemente la actualización de la tabla pues de que los datos de sucesores y predecesores estén correctos, depende el funcionamiento del anillo.

Si ocurre un fallo permanente donde una réplica sale del Sistema, pudiera reemplazarse por otra, que al añadirla nuevamente al nodo obtendría toda la información que se había perdido, ya que dentro de un nodo se replica la información. De esta manera note que el usuario no se entera cuándo desapareció una réplica por este causa, y tampoco cuándo se incorpora una nueva.

## Otras implementaciones

### Tareas pendientes

Consiste en disponer de una lista de acciones que la componente actual debe realizar con otra componente, y debido a algún motivo no pudo hacerla en un comienzo pero tiene la necesidad de hacerla en algún momento.
