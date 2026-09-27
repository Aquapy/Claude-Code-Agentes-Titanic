# Índice de gráficos (outputs/figures/)

Todos se generan con `scripts/03_graficos.py` (lee solo `outputs/titanic_clean.csv` y `outputs/tables/*.csv`; no modifica datos). PNG a 150 dpi. Las barras de tasa usan siempre el eje y de 0 a 100 %; cada barra muestra su n, y las de n < 20 se marcan con † (relleno tenue y borde discontinuo). Todo son asociaciones observadas, no causalidad.

| Archivo | Qué muestra | Conclusión que apoya |
|---|---|---|
| `supervivencia_por_sexo.png` | Tasa de supervivencia por sexo, con n y línea de la tasa global (38,4 %). | Mujeres 74,2 % (n=314) frente a hombres 18,9 % (n=577): el sexo es el factor más asociado. |
| `supervivencia_por_clase_y_sexo.png` | Dos paneles: tasa por clase, y por clase x sexo (n en cada barra). | Gradación por clase (63,0 / 47,3 / 24,2 %); el sexo domina en toda clase y las mujeres de 3ª caen a 50,0 %. |
| `supervivencia_por_grupo_edad.png` | Tasa por grupo de edad, con dos series: todos frente a solo edades reales (excluye las 177 imputadas). | Los niños 0-12 (58,0 %, n=69) sobreviven más; la imputación apenas altera el resultado. |
| `supervivencia_edad_x_sexo.png` | Tasa por edad y sexo, solo edades reales (n=714). | Niños de ambos sexos ~58 %; varones de 13-18 solo 8,8 %. Mujeres 51+ con n=17 (marcado †). |
| `distribucion_edad_por_supervivencia.png` | Histograma de Age por supervivencia (% dentro de cada grupo), solo edades reales, con medianas. | Las distribuciones se solapan y las medianas coinciden (28,0); la edad continua por sí sola separa poco (más niños <5 entre supervivientes). |
| `supervivencia_por_tamano_familia.png` | Tasa por tamaño del grupo familiar (1 a 7 o más), con n. | Máximo con 4 personas (72,4 %) y caída desde 5; el efecto se mezcla con la clase (grupos grandes casi todos de 3ª). |
| `tarifa_cuartiles_y_boxplot_por_clase.png` | Tasa por cuartil de Fare y boxplot de Fare por clase (escala log simétrica, incluye Fare=0). Nota sobre ticket compartido no verificado y los 15 con Fare=0. | La tarifa se asocia a la supervivencia (19,7 % a 58,1 %) pero refleja sobre todo la clase. |
| `supervivencia_clase_x_cabina.png` | Tasa con y sin cabina dentro de cada clase, con % de pasajeros con cabina por clase. Nota: n=16 y n=12 con cabina en 2ª y 3ª. | La cabina no es independiente de la clase; en 2ª y 3ª las muestras con cabina son demasiado pequeñas para concluir. |
| `supervivencia_clase_x_embarque.png` | Tasa por puerto (C, Q, S) dentro de cada clase, con n. | La ventaja de Cherburgo se debe a la composición por clase; la diferencia por puerto solo se mantiene en 3ª. Q en 1ª/2ª (n=2, 3) no interpretable. |
| `forest_plot_odds_ratios.png` | Odds ratio ajustados (modelo `completo`, n=891) con IC 95 %, eje log. Edad por 10 años. | Sexo (OR 15,7) y clase (3ª frente a 1ª OR 0,08) dominan; edad (0,64 por 10 años) y tamaño familiar (0,80 por persona) pesan menos. |
| `correlacion_spearman.png` | Mapa de calor (triángulo inferior) de correlaciones de Spearman; recuadro sobre Supervivencia. | Sexo (+0,54) y clase (-0,34) son las más ligadas a la supervivencia; Fare, cabina y clase están entrelazadas (-0,69 y -0,68). |
