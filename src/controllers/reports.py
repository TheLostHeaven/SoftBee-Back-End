from src.models.monitoreo import MonitoreoModel
import json

class ReportsController:
    def __init__(self, db):
        self.db = db
        self.monitoreo_model = MonitoreoModel

    def get_monitoring_reports(self, user_id):
        """Obtiene y procesa todos los monitoreos para un usuario."""
        try:
            raw_reports = self.monitoreo_model.get_all_with_details(self.db, user_id)
            processed_reports = self._process_reports(raw_reports)
            return processed_reports
        except Exception as e:
            print(f"Error en ReportsController: {e}")
            raise

    def _process_reports(self, reports):
        """Procesa los reportes crudos para añadir scores y análisis."""
        
        # Diccionarios de puntuación para respuestas categóricas
        scoring_dict = {
            "estado_general": {"excelente": 4, "bueno": 3, "regular": 2, "malo": 1},
            "poblacion": {"alta": 3, "media": 2, "baja": 1},
            "comportamiento": {"dócil": 3, "nervioso": 2, "agresivo": 1},
            "presencia_reina": {"sí": 2, "no": 1},
            "celdas_reales": {"no": 2, "sí": 1},
            "necesita_alimentacion": {"no": 2, "sí": 1},
            "espacio_disponible": {"no": 2, "sí": 1},
        }

        processed = []
        for report in reports:
            # Scores para cada categoría
            scores = {
                "estado_colmena": [],
                "produccion": [],
                "salud": [],
            }
            
            # Procesar cada respuesta
            for respuesta in report.get("respuestas", []):
                pregunta_id = respuesta.get("pregunta_id", "").lower()
                answer = str(respuesta.get("respuesta", "")).lower()

                if pregunta_id in scoring_dict:
                    score = scoring_dict[pregunta_id].get(answer, 0)
                    
                    # Asignar a la categoría correcta
                    if pregunta_id in ["estado_general", "poblacion", "comportamiento"]:
                        scores["estado_colmena"].append(score)
                    elif pregunta_id in ["presencia_reina", "celdas_reales"]:
                        scores["salud"].append(score)
                    elif pregunta_id in ["necesita_alimentacion", "espacio_disponible"]:
                        # Podría ser otra categoría, pero lo dejamos en estado general por ahora
                        scores["estado_colmena"].append(score)

                # Procesar respuestas numéricas
                elif respuesta.get("tipo_respuesta") == "numero":
                    try:
                        value = float(answer)
                        # Normalizar el score a una escala de 0-100 (ejemplo)
                        # Esto necesita los valores min/max de la pregunta, que no están aquí.
                        # Por ahora, usamos un valor fijo.
                        max_val = 20 
                        normalized_score = (value / max_val) * 100
                        
                        if pregunta_id in ["cantidad_cria", "cantidad_miel"]:
                            scores["produccion"].append(normalized_score)
                    except (ValueError, TypeError):
                        continue

            # Calcular promedios para cada categoría (y evitar división por cero)
            avg_scores = {
                "estado_colmena_avg": sum(scores["estado_colmena"]) / len(scores["estado_colmena"]) if scores["estado_colmena"] else 0,
                "produccion_avg": sum(scores["produccion"]) / len(scores["produccion"]) if scores["produccion"] else 0,
                "salud_avg": sum(scores["salud"]) / len(scores["salud"]) if scores["salud"] else 0,
            }

            # Calcular score general ponderado
            overall_score = (
                (avg_scores["estado_colmena_avg"] * 0.4) +  # 40%
                (avg_scores["produccion_avg"] / 100 * 4 * 0.3) + # Normalizado y 30%
                (avg_scores["salud_avg"] * 0.3)  # 30%
            )
            
            # Normalizar a 100
            final_score = min(100, (overall_score / 3.4) * 100) # 3.4 es el max score posible (4*0.4 + 4*0.3 + 2*0.3)

            # Añadir datos procesados al reporte
            report["processed_data"] = {
                "scores": avg_scores,
                "overall_score": round(final_score),
                "status": "Bueno" if final_score > 70 else ("Regular" if final_score > 40 else "Alerta")
            }
            processed.append(report)
            
        return processed
