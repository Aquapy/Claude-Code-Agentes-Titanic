# Informe de limpieza: Titanic

- Entrada (no modificada, MD5 verificado antes y despues): `titanic.csv`
- Salida: `outputs/titanic_clean.csv`
- Objetivo posterior: analizar los factores de supervivencia (`Survived`).

## 1. Shape antes y despues

| Paso | Filas | Columnas |
|---|---|---|
| Carga del original | 891 | 12 |
| Limpieza de espacios | 891 | 12 |
| Imputacion de `Embarked` | 891 | 12 |
| Imputacion de `Age` + indicador `Age_imputada` | 891 | 13 |
| Derivadas de `Cabin` (`tiene_Cabin`, `Deck`) | 891 | 15 |
| Conversion de tipos | 891 | 15 |
| **Final** | **891** | **15** |

No se elimino ninguna fila. Las 3 columnas nuevas son derivadas explicitas de columnas existentes.

## 2. Nulos antes y despues

| Columna | Nulos antes | % antes | Nulos despues | Tratamiento |
|---|---|---|---|---|
| Age | 177 | 19,87 % | 0 | Imputada con mediana por grupo |
| Cabin | 687 | 77,10 % | 687 (se mantienen) | No imputada; indicador `tiene_Cabin` y `Deck` |
| Embarked | 2 | 0,22 % | 0 | Imputada con la moda (`S`) |
| Resto (10 columnas) | 0 | 0 % | 0 | Sin cambios |

## 3. Decisiones por columna

- **Age (177 nulos, 19,87 %)**
  - Imputacion con la **mediana por grupo (Pclass x Sex)**, porque la edad varia mucho entre clases y sexos.
  - Medianas usadas: 1a mujer 35,0; 1a hombre 40,0; 2a mujer 28,0; 2a hombre 30,0; 3a mujer 21,5; 3a hombre 25,0.
  - Se anade `Age_imputada` (1 = edad imputada) para poder excluir o controlar esas filas en el analisis.
  - Efecto: media 29,70 a 29,11; mediana 28,0 a 26,0; desviacion tipica 14,53 a 13,30 (la imputacion comprime la varianza).
  - Valores no enteros: 25 edades (18 del tipo x,5 que son estimaciones, y 7 bebes con Age < 1). Son validos y se conservan.
- **Cabin (687 nulos, 77,10 %)**
  - Supera el 50 %, asi que **no se imputa**; la columna original queda con sus 687 nulos y se considera poco fiable.
  - `tiene_Cabin` (0/1): 204 con cabina, 687 sin ella.
  - `Deck`: primera letra de la cabina (A, B, C, D, E, F, G, T) o `Desconocido` (687). Los nulos no son aleatorios: tienen cabina asignada 176 de 216 pasajeros de 1a clase, frente a solo 12 de 491 de 3a.
  - Supervivencia observada: 66,7 % con cabina registrada y 30,0 % sin ella. Esto esta muy confundido con la clase, asi que hay que interpretarlo con cuidado.
- **Embarked (2 nulos, 0,22 %)**
  - Imputacion con la moda `S` (644 de 889 valores conocidos).
  - Los nulos son PassengerId 62 y 830, ambos con ticket 113572 y cabina B28, es decir viajaban juntos. La imputacion con la moda es una suposicion; el impacto es minimo (2 filas).
- **Name**: se eliminaron espacios sobrantes al final en 2 filas (PassengerId 16 y 858). Sin espacios dobles.
- **Sex, Ticket, Cabin, Embarked**: sin espacios sobrantes ni variantes de mayusculas.
- **Fare**: sin nulos ni valores negativos.

### Tipos de datos

| Columna | Tipo final |
|---|---|
| PassengerId | texto (identificador, no numerico) |
| Survived, Pclass, Sex, Embarked, Deck | category |
| Age, Fare | float |
| SibSp, Parch, Age_imputada, tiene_Cabin | int |
| Name, Ticket, Cabin | texto |

El CSV no conserva el tipo `category`. Al leerlo hay que declararlo: usar `dtype={'PassengerId': str}` y convertir a `category` lo necesario. Ojo: `Survived` como `category` no admite `.mean()`; para tasas de supervivencia conviene mantenerla numerica (0/1).

## 4. Duplicados

- Filas completas duplicadas: **0**.
- `PassengerId` duplicados: **0** (891 unicos).
- `Name` duplicados: **0**.
- `Ticket` repetido: 134 tickets compartidos por 344 pasajeros (familias o grupos). Es **legitimo**, no un error. Se conserva.
- No se elimino ninguna fila.

## 5. Consistencia y outliers (reportados, no eliminados)

- Edades imposibles (negativas): 0. Rango 0,42 a 80.
- Outliers de `Age` por IQR: 11 filas; solo 2 a mas de 3 desviaciones. Plausibles.
- `Fare` = 0: **15 pasajeros** (PassengerId 180, 264, 272, 278, 303, 414, 467, 482, 598, 634, 675, 733, 807, 816, 823). Todos embarcaron en S; su tasa de supervivencia es 6,7 % (1 de 15). Pueden ser tripulacion o invitados, o datos faltantes codificados como 0. Se conservan sin cambios.
- `Fare` alto: 116 filas quedan por encima del limite IQR (65,63). Hay 3 pasajeros con 512,33 (PassengerId 259, 680, 738), todos de 1a clase y con el mismo ticket PC 17755. La distribucion esta muy sesgada a la derecha. Se conservan.
- `SibSp` >= 5: 12 filas; `Parch` >= 5: 6 filas. Son familias numerosas, plausibles.

## 6. Validacion final

- Sin nulos en `Age`, `Embarked`, `Fare` ni `Deck`; `Cabin` mantiene sus 687 nulos a proposito.
- 891 filas, 15 columnas, `PassengerId` unico.
- El CSV releido tiene el mismo shape (891, 15).
- `titanic.csv` sin modificar (MD5 `61fdd54abdbf6a85b778e937122e1194` identico antes y despues).

## 7. Advertencias para el analisis

1. Las edades imputadas (19,87 %) reducen la varianza. Conviene un analisis de sensibilidad con `Age_imputada == 0`. Su supervivencia (29,4 %) es menor que la de las edades reales (40,6 %), sobre todo por la composicion de clases: la 3a clase concentra los nulos.
2. `tiene_Cabin` y `Deck` estan fuertemente ligados a `Pclass`; no interpretar como efecto independiente sin controlar la clase.
3. Los `Fare` de tickets compartidos podrian ser el importe total del grupo y no el de cada persona. No se ha verificado ni corregido.
4. Los 15 casos con `Fare` = 0 pueden ser datos faltantes; decidir en el analisis si se excluyen.
5. `Embarked` de PassengerId 62 y 830 es una suposicion (moda).
