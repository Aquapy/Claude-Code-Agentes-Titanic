# Informe de análisis exploratorio: factores de supervivencia en el Titanic

- Entrada (solo lectura): `outputs/titanic_clean.csv` (891 filas x 15 columnas). No se ha modificado ningún dataset.
- Tablas generadas: `outputs/tables/*.csv` (18 archivos, listados en la sección 11).
- `Survived` se usa como numérica 0/1; toda "tasa" es la media de `Survived` (% de supervivientes del grupo).
- Convenciones: `n` = tamaño del grupo. Chi-cuadrado con `scipy.stats.chi2_contingency` (corrección de Yates por defecto en tablas 2x2). Mann-Whitney para numéricas asimétricas. V = V de Cramér. Todos los resultados son asociaciones observadas, no causalidad.

## 1. Resumen general

- 891 pasajeros; 342 sobreviven (**38,4 %**) y 549 mueren (61,6 %).
- Composición: 577 hombres (64,8 %) y 314 mujeres; 491 en 3ª clase (55,1 %), 216 en 1ª y 184 en 2ª; embarque S 646, C 168, Q 77.
- Age: media 29,1 y mediana 26,0 (177 imputadas). Fare: mediana 14,45, media 32,20, máx. 512,33 (muy asimétrica). 608 pasajeros con SibSp=0 y 678 con Parch=0.
- Cabina registrada: 204 (22,9 %); 687 sin dato.

## 2. Métricas clave (tasa de supervivencia por variable, sin controlar por otras)

| Variable | Grupo | n | Supervivientes | Tasa | Prueba |
|---|---|---|---|---|---|
| Sexo | Mujer | 314 | 233 | **74,2 %** | chi2=260,7; gl=1; p=1,2e-58; V=0,54 |
| Sexo | Hombre | 577 | 109 | **18,9 %** | |
| Clase | 1ª | 216 | 136 | **63,0 %** | chi2=102,9; gl=2; p=4,6e-23; V=0,34 |
| Clase | 2ª | 184 | 87 | 47,3 % | |
| Clase | 3ª | 491 | 119 | 24,2 % | |
| Embarque | C | 168 | 93 | 55,4 % | chi2=26,0; gl=2; p=2,3e-06; V=0,17 |
| Embarque | Q | 77 | 30 | 39,0 % | |
| Embarque | S | 646 | 219 | 33,9 % | |
| Acompañantes (SibSp+Parch+1) | Solo (1) | 537 | 163 | 30,4 % | chi2=74,5; gl=2; p=6,5e-17 |
| | 2 a 4 personas | 292 | 169 | **57,9 %** | |
| | 5 o más | 62 | 10 | **16,1 %** | |

`Embarked=S` incluye los pasajeros 62 y 830 (imputados con la moda, ambos supervivientes). Sin ellos S = 33,7 % (n=644), un cambio irrelevante.

Correlaciones de Spearman con `Survived` (`tables/correlaciones_spearman.csv`): Sex_female +0,54; Pclass -0,34; Fare +0,32; tiene_Cabin +0,32; Familia +0,17; Age -0,04. Fare, tiene_Cabin y Pclass están muy correlacionadas entre sí (Fare-Pclass -0,69; tiene_Cabin-Pclass -0,68).

## 3. Comparativas

### 3.1 Sexo x Clase (`tables/tasa_clase_x_sexo.csv`)

| Clase | Mujeres: n / tasa | Hombres: n / tasa | chi2 del sexo dentro de la clase |
|---|---|---|---|
| 1ª | 94 / **96,8 %** | 122 / 36,9 % | 79,2; p=5,6e-19 |
| 2ª | 76 / **92,1 %** | 108 / 15,7 % | 101,3; p=7,8e-24 |
| 3ª | 144 / 50,0 % | 347 / **13,5 %** | 71,7; p=2,5e-17 |

El efecto del sexo persiste en las tres clases (brecha de 60 puntos en 1ª, 76 en 2ª y 36 en 3ª). El efecto de la clase también persiste dentro de cada sexo (mujeres: chi2=81,9, p=1,7e-18; hombres: chi2=33,0, p=7,0e-08). En 3ª las mujeres pierden la ventaja casi total (50,0 %).

### 3.2 Modelo conjunto (regresión logística, `tables/regresion_logistica_OR.csv`)

`Survived ~ Pclass + Sexo + Age + Tamaño de familia`, n=891, pseudo-R2=0,34:

| Variable | OR | IC 95 % | p |
|---|---|---|---|
| Mujer (frente a hombre) | 15,7 | 10,7 a 23,2 | <1e-40 |
| 2ª clase (frente a 1ª) | 0,28 | 0,16 a 0,46 | 1,3e-06 |
| 3ª clase (frente a 1ª) | 0,08 | 0,05 a 0,13 | 7,8e-23 |
| Edad (por 10 años) | 0,64 | 0,55 a 0,75 | 5,6e-08 |
| Tamaño de familia (por persona) | 0,80 | 0,70 a 0,90 | 4,5e-04 |

Con solo edades reales (n=714) los resultados son casi idénticos: mujer OR 14,4; 3ª clase OR 0,07; edad por 10 años OR 0,65 (p=1,3e-07). La edad aparece asociada (más edad, menos supervivencia) al controlar clase y sexo, aunque marginalmente no lo parezca (sección 4). Es condicional, no causal.

## 4. Edad y análisis de sensibilidad

Hay 177 edades imputadas: 136 de 3ª clase, 30 de 1ª y 11 de 2ª. Los pasajeros con edad imputada sobreviven menos (29,4 % frente a 40,6 %; chi2=7,1; p=0,0077), pero es por composición de clases. Dentro de cada clase, con edad imputada frente a real:
- 1ª: 46,7 % (n=30) frente a 65,6 % (n=186); p=0,074.
- 2ª: 36,4 % (n=11) frente a 48,0 % (n=173).
- 3ª: 25,0 % (n=136) frente a 23,9 % (n=355); p=0,90.

### 4.1 Tasa por grupo de edad: análisis completo frente a solo edades reales (`Age_imputada == 0`)

| Grupo de edad | Completo: n / tasa | Solo reales: n / tasa |
|---|---|---|
| 0-12 | 69 / **58,0 %** | 69 / **58,0 %** |
| 13-18 | 70 / 42,9 % | 70 / 42,9 % |
| 19-35 | 514 / 35,8 % | 358 / 38,3 % |
| 36-50 | 174 / 37,9 % | 153 / 39,9 % |
| 51+ | 64 / 34,4 % | 64 / 34,4 % |
| Chi2 (gl=4) | 13,7; p=0,008 | 10,7; p=0,031 |
| Niños (0-12) frente a resto | 58,0 % frente a 36,7 % (p=0,0008) | 58,0 % frente a 38,8 % (p=0,003) |
| Mediana de edad, superv. frente a no superv. | 27,0 (n=342) frente a 25,0 (n=549); Mann-Whitney p=0,25 | 28,0 (n=290) frente a 28,0 (n=424); Mann-Whitney p=0,16 |
| Media de edad, superv. frente a no superv. | 28,1 frente a 29,7; Welch p=0,082 | 28,3 frente a 30,6; Welch p=0,041 |

Conclusiones de la sensibilidad:
- **El resultado de los niños es robusto**: los 69 pasajeros de 0 a 12 años tienen edad real (las medianas imputadas van de 21,5 a 40), así que su tasa es idéntica en ambos análisis.
- Las imputadas se concentran en 19-35 y 36-50; excluirlas sube esas tasas unos 2 puntos, sin cambiar ninguna conclusión cualitativa.
- **La diferencia de edad media entre supervivientes y no supervivientes es débil y frágil**: solo significativa al 5 % en Welch con edades reales (p=0,041), no con todos los datos (p=0,082) ni con Mann-Whitney (p=0,25 y 0,16). No presentarla como hallazgo firme.
- Con edades reales y por grupo clase x sexo, solo son significativas las diferencias de edad entre hombres de 1ª (mediana 36,0 superv. frente a 45,5 no superv.; n=40 frente a 61; p=0,007) y de 2ª (3,0 frente a 30,5; n=15 frente a 84; p=0,001). En 2ª la mediana de 3,0 refleja que se salvaron los niños varones.

### 4.2 Edad x Sexo (`tables/tasa_sexo_x_edad_*.csv`, solo edades reales)

| Grupo | Mujeres: n / tasa | Hombres: n / tasa |
|---|---|---|
| 0-12 | 32 / 59,4 % | 37 / 56,8 % |
| 13-18 | 36 / 75,0 % | 34 / **8,8 %** |
| 19-35 | 120 / 78,3 % | 238 / 18,1 % |
| 36-50 | 56 / 73,2 % | 97 / 20,6 % |
| 51+ | 17 / 94,1 % | 47 / 12,8 % |

Los niños de ambos sexos tienen tasa similar (59,4 % y 56,8 %); desde los 13 años la ventaja femenina se dispara. Precaución con mujeres de 51+ (n=17) y niños de 1ª (n=4). Entre los 0-12 la clase pesa mucho: 1ª 75,0 % (n=4), 2ª 100 % (17 de 17), 3ª 41,7 % (n=48).

## 5. Tarifa (Fare)

Cuartiles de Fare (`tables/tasa_por_cuartil_tarifa.csv`), chi2=80,2; gl=3; p=2,8e-17:

| Cuartil | Rango Fare | n | Tasa |
|---|---|---|---|
| Q1 | 0 a 7,90 | 223 | 19,7 % |
| Q2 | 7,93 a 14,45 | 224 | 30,4 % |
| Q3 | 14,46 a 31,00 | 222 | 45,5 % |
| Q4 | 31,28 a 512,33 | 222 | 58,1 % |

Fare mediana: 26,0 en supervivientes (n=342) frente a 10,5 en no supervivientes (n=549); Mann-Whitney p=4,6e-22. Pero Fare sustituye en gran medida a la clase (mediana 60,3 en 1ª, 14,3 en 2ª, 8,1 en 3ª). Dentro de la clase:
- 1ª: mediana 78,0 frente a 44,8 (n=136 frente a 80; p=7e-05).
- 2ª: 21,0 frente a 13,0 (n=87 frente a 97; p=0,004).
- 3ª: 8,5 frente a 8,1 (n=119 frente a 372; p=0,20, sin efecto).

**Advertencia sobre tickets compartidos (no verificada):** 344 pasajeros comparten 134 tickets; si `Fare` fuese el total del grupo, sería un sustituto del tamaño del grupo. Comprobación exploratoria dividiendo Fare por el número de pasajeros con el mismo ticket en el dataset: la correlación de Spearman con Survived apenas cambia en global (0,32 frente a 0,31), pero **dentro de cada clase se desvanece**:
- 1ª: 0,27 (p<0,001) pasa a 0,11 (p=0,11).
- 2ª: 0,21 (p=0,003) pasa a 0,07 (p=0,34).
- 3ª: 0,06 pasa a 0,00.

Es compatible con que el "efecto Fare" dentro de la clase sea en parte efecto del tamaño del grupo, pero es una hipótesis sin verificar.

**Fare = 0 (15 pasajeros, limitación):** todos hombres y de S; 1 de 15 sobrevive (6,7 %); 5 son de 1ª, 6 de 2ª y 4 de 3ª. Frente al resto de hombres (108 de 562, 19,2 %), Fisher exacto p=0,32: no concluyente con n=15. Excluirlos cambia poco las tasas por clase (1ª de 63,0 % a 64,5 %; 2ª de 47,3 % a 48,9 %; 3ª sin cambios, 24,2 %). Se mantienen en todos los análisis.

## 6. Cabina y Deck: confusión con la clase

Tasa bruta: con cabina 66,7 % (n=204), sin cabina 30,0 % (n=687); chi2=87,9; p=6,7e-21. **No es un efecto independiente**: tiene cabina el 81,5 % de 1ª, el 8,7 % de 2ª y el 2,4 % de 3ª. Cruzando por clase (`tables/tasa_clase_x_cabina.csv`):

| Clase | Sin cabina: n / tasa | Con cabina: n / tasa | Diferencia | Prueba |
|---|---|---|---|---|
| 1ª | 40 / 47,5 % | 176 / 66,5 % | 19 puntos | chi2 p=0,039; Fisher p=0,030 |
| 2ª | 168 / 44,0 % | 16 / 81,2 % | 37 puntos | chi2 p=0,0097; Fisher p=0,007 |
| 3ª | 479 / 23,6 % | 12 / 50,0 % | 26 puntos | chi2 p=0,077; Fisher p=0,080 |

Persiste una diferencia dentro de cada clase, pero las muestras con cabina en 2ª y 3ª son minúsculas (n=16 y 12). Además está confundida con el sexo: en 1ª, 81 de 94 mujeres tienen cabina (96,3 % de supervivencia con cabina frente a 100 %, n=13, sin ella). Solo entre hombres de 1ª: con cabina 41,1 % (n=95) frente a sin cabina 22,2 % (n=27); Fisher p=0,11, **no significativo**. En el modelo logístico ampliado (clase, sexo, edad, familia, embarque y cabina; n=891) `tiene_Cabin` mantiene OR=2,59 (IC 95 % 1,35 a 4,99; p=0,004), pero con posible sesgo de registro (el dato de cabina pudo consignarse más para quienes sobrevivieron). En ese modelo la 2ª clase deja de ser significativa frente a 1ª (p=0,25) porque cabina absorbe parte del efecto de clase.

Deck (solo los 204 con cabina; `tables/tasa_clase_x_deck.csv`): B 74,5 % (n=47), D 75,8 % (n=33), E 75,0 % (n=32), C 59,3 % (n=59), F 61,5 % (n=13), A 46,7 % (n=15), G 50,0 % (n=4), T 0 % (n=1). En 2ª y 3ª hay solo 3 a 8 pasajeros por cubierta: no hay base para interpretar diferencias entre decks más allá de "1ª clase con cabina".

## 7. Embarque y familia (controlando)

- **Embarque**: la ventaja de C (55,4 %) se explica en buena parte por la composición: 85 de 168 pasajeros de C son de 1ª clase (50,6 %) frente a 129 de 646 en S (20,0 %). Dentro de 1ª (chi2=2,6; p=0,28) y 2ª (p=0,69) no hay diferencia por puerto; en 3ª sí (C 37,9 %, n=66; Q 37,5 %, n=72; S 19,0 %, n=353; chi2=18,9; p=7,9e-05). En el modelo ampliado S frente a C: OR=0,61 (p=0,038). Q en 1ª (n=2) y 2ª (n=3) no es interpretable.
- **Tamaño de la familia/acompañantes** (`tables/tasa_por_tamano_familia.csv`): la tasa sube de 30,4 % (solo, n=537) a 72,4 % con 4 personas (n=29) y cae a 20,0 % con 5 (n=15), 13,6 % con 6 (n=22), 0 % con 8 (n=6) y 0 % con 11 (n=7). Persiste dentro de cada clase (1ª p=0,011; 2ª p=0,0003; 3ª p=1,7e-06); en 3ª: 2 a 4 personas 40,7 % (n=113), solo 21,3 % (n=324), 5 o más 7,4 % (n=54). También dentro de cada sexo: mujeres solas 78,6 % (n=126), 2-4 80,6 % (n=155), 5+ 27,3 % (n=33); hombres solos 15,6 % (n=411), 2-4 32,1 % (n=137), 5+ 3,4 % (n=29). En hombres, viajar con 1 a 3 familiares duplica la tasa; en mujeres solo importa el grupo grande. De 49 pasajeros en tickets de 5 o más, 44 son de 3ª.

## 8. Hallazgos principales (ordenados por importancia)

1. **El sexo es el factor más fuerte**: mujeres 74,2 % (n=314) frente a hombres 18,9 % (n=577); OR ajustado 15,7; V=0,54. Las mujeres son el 68,1 % de los supervivientes (233 de 342). Persiste en las tres clases.
2. **La clase social marca una gradación clara**: 63,0 % (1ª, n=216), 47,3 % (2ª, n=184), 24,2 % (3ª, n=491); OR ajustado 3ª frente a 1ª 0,08. Persiste dentro de cada sexo.
3. **Interacción sexo x clase**: las mujeres de 1ª y 2ª sobreviven 96,8 % (n=94) y 92,1 % (n=76); las de 3ª, 50,0 % (n=144), superan aun así a los hombres de 1ª (36,9 %, n=122). Los peores grupos son hombres de 3ª (13,5 %, n=347) y de 2ª (15,7 %, n=108).
4. **Los niños (0-12) tienen ventaja**: 58,0 % (n=69) frente a 36,7 % del resto (p=0,0008); robusto a la sensibilidad (edades todas reales). Entre ellos, 2ª clase 17 de 17 y 3ª 41,7 % (n=48). Los varones de 13-18 años solo 8,8 % (n=34). La edad continua es débil marginalmente (Mann-Whitney p=0,25) y solo aparece al controlar clase y sexo (OR 0,64 por 10 años).
5. **Tamaño del grupo**: efecto no lineal; 2-4 personas 57,9 % (n=292), solo 30,4 % (n=537), 5 o más 16,1 % (n=62); persiste controlando clase y sexo.
6. **Tarifa y cabina son en gran parte reflejo de la clase**: Fare Q4 58,1 % frente a Q1 19,7 %; cabina 66,7 % frente a 30,0 %. Dentro de cada clase el efecto se atenúa (Fare sin efecto en 3ª, p=0,20; cabina en hombres de 1ª, p=0,11). Queda una diferencia moderada por cabina tras ajustar (OR 2,59), con posible sesgo de registro.
7. **Embarque**: C 55,4 % (n=168) frente a S 33,9 % (n=646), explicado sobre todo por la clase; solo hay diferencia clara en 3ª (C 37,9 % frente a S 19,0 %).
8. **Fare = 0**: 1 de 15 sobrevive (6,7 %), todos hombres; no concluyente (Fisher p=0,32).

## 9. Limitaciones

- **Observacional**: todo son asociaciones. Sexo y clase reflejan las normas de evacuación y la ubicación en el barco, no separables de la disponibilidad de botes.
- **Edad imputada (19,9 %)**: la mediana por Pclass x Sex comprime la varianza y sitúa a 136 pasajeros de 3ª en 21,5 a 25 años. Se contrastó con `Age_imputada == 0` (sección 4): lo de los niños es inmune a la imputación; lo de edad continua no es robusto.
- **Cabina/Deck**: 77,1 % de nulos no aleatorios (81,5 % de 1ª con dato frente a 2,4 % de 3ª); posible sesgo de registro; muestras minúsculas en 2ª y 3ª con cabina (16 y 12) y en varios decks (G n=4, T n=1).
- **Fare**: asimétrica; posible total de grupo en tickets compartidos, no verificado (la comprobación por persona es exploratoria y solo cuenta pasajeros presentes en el dataset). 15 casos con Fare=0 conservados; pueden ser datos faltantes codificados como 0.
- **Embarked** de los pasajeros 62 y 830 es una suposición (moda S): impacto nulo (S 33,9 % frente a 33,7 % sin ellos).
- **Tickets compartidos** (344 pasajeros en 134 tickets): las observaciones no son independientes, lo que sobreestima la significación de los p-valores.
- **Muestras pequeñas** señaladas en el texto: niños de 1ª (n=4), mujeres 51+ (n=17), familias de 8 y 11 (n=6 y 7), Q en 1ª/2ª (n=2 y 3).
- **Múltiples pruebas sin corrección**: los p muy pequeños (<1e-5) son robustos; los cercanos a 0,05 (edad Welch 0,041; cabina en 1ª 0,039; embarque OR 0,038) son solo indicativos.
- Los datos no distinguen tripulación de pasajeros y `Name` (títulos) no se ha explotado.

## 10. Gráficos recomendados para el visualizer

Guardar en `outputs/figures/`, títulos en español. Usar `Survived` numérica (media = tasa) y mostrar `n` en las etiquetas.

1. **Barras de tasa por sexo** (x=Sexo, y=% supervivencia, n anotado, línea en 38,4 % global). Mensaje: mujeres 74,2 % frente a hombres 18,9 %.
2. **Barras agrupadas clase x sexo** (x=Pclass, color=Sexo, y=%, n en cada barra). Mensaje: el sexo domina en toda clase; las mujeres de 3ª (50,0 %) pierden la ventaja.
3. **Barras por clase** (x=Pclass; 63,0 / 47,3 / 24,2 %). Puede ir en panel con la 2.
4. **Barras por grupo de edad** (x=0-12, 13-18, 19-35, 36-50, 51+; y=%) con **dos series**, completo y solo edades reales (`tables/tasa_por_edad_*.csv`), n anotado. Mensaje: los niños tienen 58,0 % y la imputación apenas altera el resultado.
5. **Barras edad x sexo** (color por sexo; `tables/tasa_sexo_x_edad_solo_reales.csv`). Mensaje: niños de ambos sexos ~58 %; varones de 13-18 solo 8,8 %.
6. **Histograma o densidad de Age por Survived** (solo `Age_imputada == 0`, indicando que se excluyen 177 imputadas). Mensaje: las distribuciones se solapan casi totalmente; la edad sola no separa.
7. **Barras por tamaño de grupo familiar** (x=Familia 1, 2, 3, 4, 5, 6, 7+; y=%, n anotado). Mensaje: máximo con 4 personas (72,4 %) y caída desde 5.
8. **Barras por cuartil de Fare** (19,7 % a 58,1 %) junto a un **boxplot de Fare por clase** (escala log). Mensaje: Fare refleja la clase. Anotar la limitación de Fare de grupo y los 15 casos con Fare=0.
9. **Barras clase x cabina** (x=Pclass, color=tiene_Cabin, n en cada barra; `tables/tasa_clase_x_cabina.csv`). Mensaje: la cabina no es independiente de la clase; en 2ª y 3ª las muestras con cabina son muy pequeñas (n=16 y 12).
10. **Barras clase x embarque** (color=Embarked; `tables/tasa_clase_x_embarque.csv`). Mensaje: la diferencia por puerto solo se mantiene en 3ª.
11. **Forest plot de odds ratios** (`tables/regresion_logistica_OR.csv`, modelo `completo`, eje log). Mensaje: sexo y clase dominan; edad y familia pesan menos.
12. **Mapa de calor de correlación de Spearman** (`tables/correlaciones_spearman.csv`). Mensaje: sexo y clase correlacionan más con la supervivencia; Fare, cabina y clase están entrelazadas.

## 11. Tablas generadas (`outputs/tables/`, todas `.csv`)

`tasa_por_sexo`, `tasa_por_clase`, `tasa_por_embarque`, `tasa_por_tamano_familia`, `tasa_por_grupo_familia`, `tasa_clase_x_sexo`, `tasa_por_edad_completo`, `tasa_por_edad_solo_reales`, `tasa_sexo_x_edad_completo`, `tasa_sexo_x_edad_solo_reales`, `tasa_por_cuartil_tarifa`, `tasa_clase_x_cabina`, `tasa_clase_x_deck`, `tasa_clase_sexo_cabina`, `tasa_clase_x_embarque`, `tasa_clase_x_grupo_familia`, `correlaciones_spearman`, `regresion_logistica_OR`. Las tablas de tasas incluyen `n`, `supervivientes` y `tasa_pct`.
