# ADR: Composition Root en `app/bootstrap/`

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La version actual de `app/main.py` hacia composicion manual de dependencias:

* inicializaba base de datos
* creaba la sesion
* instanciaba repositorios
* instanciaba use cases
* instanciaba viewmodels
* construia ventana y controlador principal

Ese enfoque funciona en una aplicacion pequena, pero mezcla arranque con cableado interno y hace que `main.py` crezca demasiado rapido.

## Decision

Se introduce `app/bootstrap/` como composition root oficial de la aplicacion.

Estructura inicial:

```txt
app/bootstrap/
├─ __init__.py
├─ applicationFactory.py
└─ serviceRegistry.py
```

### Responsabilidades

* `applicationFactory.py`
  centraliza el cableado de infraestructura, viewmodels y ventana principal
* `serviceRegistry.py`
  expone un contenedor simple con dependencias ya construidas para la aplicacion de escritorio
* `app/main.py`
  queda limitado a iniciar configuracion, logging y ejecucion de la ventana principal

## Consecuencias

Ventajas:

* `main.py` queda pequeno y estable
* el cableado de dependencias queda en un punto explicito
* la evolucion futura hacia `shell + shared + features` resulta mas sencilla
* se reduce el acoplamiento entre arranque y detalles de implementacion

Costes:

* aparece una capa adicional de bootstrap
* la composicion de dependencias sigue siendo manual, aunque ya encapsulada

## Notas

Esta decision no introduce un contenedor IoC complejo.

Se mantiene un enfoque pragmatico:

* composition root explicito
* pocas clases
* sin sobreingenieria
