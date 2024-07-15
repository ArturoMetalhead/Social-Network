# Social-Network

## Especificaciones

El proyecto consiste en implementar una red social distribuida para la comunicación siguiendo la idea en la cual se basa Twitter. Siguiendo la filosofı́a de funcionamiento de Twitter, el sistema debe brindar una infraestructura para el manejo de usuarios, de manera que puedan publicar sus mensajes, volver a publicar mensajes que consideren interesantes de otros usuarios y escoger quienes van a ser sus amigos. Además, como parte del manejo de usuarios, se debe proporcionar un mecanismo para la autenticación distribuida de manera tal que se logre un modelo que no sea centralizado.

## Integrantes del equipo

- Carlos Arturo Pérez Cabrera
- Diana Laura Pérez Trujillo

## Funcionalidades

Social-Network simula el funcionamiento de una red social, similar a Twitter. Los usuarios, además de tener una cuenta, pueden realizar publicaciones, seguir a otros usuarios, e incluso publicar publicaciones que hayan publicado otros usuarios.

### Registro e inicio de sesión

Para crear una cuenta en la plataforma, es necesario que el usuario provea un nombre de usuario (nickname), que debe ser único, una contraseña y una dirección de correo electrónico.

Si ya el usuario tiene una cuenta creada, su primer paso para interactuar con la plataforma debe ser iniciar sesión (login), debe proveer para ello nombre de usuario y contraseña. Solo si ambos son correctos, entonces el user puede acceder al resto de las opciones que la plataforma ofrece.

### Post y Repost

El usuario puede realizar publicaciones en su perfil. Los mensajes tienen un límite de 160 caracteres (como sucede en redes sociales como Twitter). Además, el usuario puede compartir publicaciones de otros usuarios, esto se conoce como Repost. Las publicaciones se pueden visualizar en el perfil del usuario que las creó o reposteó.

### Seguir y Seguidores

El usuario puede seguir a otros usuarios. Cuando un usuario sigue a otro, puede ver las publicaciones que este sube a su perfil.

### Interacción del usuario

La interacción del usuario con la aplicación será mediante una consola interactiva, donde el usuario podrá escoger que acción realizar a continuación.

## Almacenamiento de la información

Para el diseño y manejo de la base de datos se utilizó Sqlite con la librería Peewee de Python.

Con el objetivo de lograr un almacenamiento distribuido, los servidores que contienen datos se dispusieron en forma de anillo y la búsqueda se realiza mediante una Distributed Hash Table (DHT) con el algoritmo Chord. Un detalle a resaltar es que los nombres de usuario deben ser únicos, por lo que se aprovecha esta propiedad, se utiliza una función de hash, para hashear estos nombres de usuario, y de esa manera decidir qué nodo del Anillo Chord se hará responsable de dicho usuario (incluye todo lo referente a él). Esta distribución ayuda a que exista mayor equilibrio en la cantidad de información almacenada en un nodo.

## Arquitectura