# Composition root modularizado por responsabilidad

## Estado

Aprobado.

## Contexto

`app/bootstrap/applicationFactory.py` habia asumido demasiadas responsabilidades:

* bootstrap de base de datos
* construccion de repositorios
* ensamblado de viewmodels
* construccion de ventana y controlador principal

Eso hacia mas dificil mantener el composition root claro y escalable.

## Decision

Se divide el composition root en fabricas por responsabilidad:

```txt
app/bootstrap/
├─ applicationFactory.py
├─ persistenceFactory.py
├─ presentationFactory.py
└─ serviceRegistry.py
```

Responsabilidades:

* `ApplicationFactory`: orquestador principal del ensamblado
* `PersistenceFactory`: crea sesion, repositorios concretos y bootstrap de persistencia
* `PresentationFactory`: crea ventana principal, controller shell y `DesktopApplication`
* `ServiceRegistry`: agrupa dependencias listas para la capa de presentacion

## Criterios

* `main.py` sigue limitado a cargar settings, configurar logging, bootstrap de base de datos y lanzar la aplicacion
* el cableado de persistencia no vive mezclado con el de UI
* la composicion sigue centralizada en `bootstrap/`, no repartida por capas arbitrarias

## Consecuencias

Ventajas:

* SRP mas claro en el composition root
* menor acoplamiento entre persistencia y presentacion
* mejor punto de extension para futuras fabricas de workers o integraciones

Tradeoff:

* hay mas archivos en `bootstrap/`, pero cada uno tiene una responsabilidad concreta y visible
