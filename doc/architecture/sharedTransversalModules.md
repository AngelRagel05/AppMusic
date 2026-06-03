# Shared transversal fuera de UI

## Estado

Aprobado.

## Contexto

El proyecto ya tenia piezas tecnicas reutilizables que no pertenecian ni a dominio ni a UI, pero estaban dispersas o embebidas en modulos concretos.

Necesitabamos un espacio transversal explicito para:

* helpers genericos no visuales
* excepciones compartidas
* constantes reutilizables entre capas

sin convertir `shared/` en un cajon de sastre.

## Decision

Se introduce `app/shared/` con esta estructura minima:

```txt
app/shared/
├─ utils/
├─ exceptions/
└─ constants/
```

Cambios aplicados:

* `configure_logging(...)` pasa de `app/utils/logging.py` a `app/shared/utils/logging.py`
* se crea `ValidationError` en `app/shared/exceptions/`
* las constantes compartidas de YouTube y opciones de ignored terms pasan a `app/shared/constants/`

## Criterios

Puede entrar en `shared/`:

* helpers tecnicos genericos sin dependencia de UI ni dominio
* excepciones transversales reutilizables
* constantes que tengan sentido fuera de un unico modulo

No debe entrar en `shared/`:

* reglas de negocio
* entidades o contratos de dominio
* logica visual
* servicios de infraestructura concretos

## Consecuencias

Ventajas:

* las dependencias transversales quedan en un punto explicito
* se reduce la duplicacion de constantes
* la validacion compartida usa una excepcion coherente y reutilizable

Tradeoff:

* `shared/` debe mantenerse pequeño y vigilado para no convertirse en una carpeta comodin
