# main.py
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
from supabase import create_client, Client
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- INICIALIZA EL CLIENTE DE SUPABASE ---
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

# --- PEGA AQUÍ TODA TU LÓGICA DE CÁLCULO DE PYTHON ---
VALOR_UIT = 5350
PREGUNTAS_EXENTAS_MYPE = ['q36', 'q37', 'q38', 'q39', 'q41']
data_micro = {
    '1': [240.75, 588.50, 1230.50], '2': [267.50, 749.00, 1337.50], '3': [374.50, 856.00, 1551.50], '4': [428.00, 963.00, 1712.00], '5': [481.50, 1070.00, 1926.00], '6': [588.50, 1337.50, 2193.50], '7': [749.00, 1551.50, 2514.50], '8': [856.00, 1819.00, 2889.00], '9': [963.00, 2033.00, 3263.50], '10 y más': [1230.50, 2407.50, 3638.00]
}
TABLA_MULTAS_MICRO = pd.DataFrame(data_micro, index=['Leves', 'Grave', 'Muy Grave'])
data_pequena = {
    '1 a 5': [481.50, 2407.50, 4440.50], '6 a 10': [749.00, 3156.50, 6742.00], '11 a 20': [963.00, 4120.50, 8827.50], '21 a 30': [1230.50, 5189.50, 11449.00], '31 a 40': [1712.00, 6742.00, 14817.50], '41 a 50': [2407.50, 8078.50, 17912.50], '51 a 60': [3263.50, 10700.00, 23754.00], '61 a 70': [4440.50, 13321.50, 29634.00], '71 a 99': [5403.50, 16328.50, 35310.00], '100 y más': [12037.50, 24167.50, 61840.50]
}
TABLA_MULTAS_PEQUENA = pd.DataFrame(data_pequena, index=['Leves', 'Grave', 'Muy Grave'])
TABLA_MULTAS_GENERAL_UIT = {
    '1-10': {'Leve': 0.13, 'Grave': 0.45, 'Muy Grave': 0.94}, '11-25': {'Leve': 0.38, 'Grave': 1.58, 'Muy Grave': 3.16}, '26-50': {'Leve': 0.61, 'Grave': 6.46, 'Muy Grave': 10.61}, '51-100': {'Leve': 1.04, 'Grave': 10.70, 'Muy Grave': 21.22}, '101-200': {'Leve': 1.58, 'Grave': 14.94, 'Muy Grave': 31.83}, '201-300': {'Leve': 2.01, 'Grave': 18.06, 'Muy Grave': 42.44}, '301-400': {'Leve': 2.44, 'Grave': 21.18, 'Muy Grave': 53.04}, '401-500': {'Leve': 2.87, 'Grave': 24.29, 'Muy Grave': 63.64}, '501-600': {'Leve': 3.29, 'Grave': 28.53, 'Muy Grave': 74.25}, '601-700': {'Leve': 3.72, 'Grave': 32.77, 'Muy Grave': 84.85}, '701-800': {'Leve': 4.15, 'Grave': 37.01, 'Muy Grave': 95.45}, '801-900': {'Leve': 4.58, 'Grave': 41.25, 'Muy Grave': 106.05}, '901-a-mas': {'Leve': 5.02, 'Grave': 45.49, 'Muy Grave': 116.65}
}
TABLA_MULTAS_GENERAL = pd.DataFrame(TABLA_MULTAS_GENERAL_UIT).T * VALOR_UIT
BASE_DE_DATOS_INFRACCIONES = {
    'q1': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No contar con una política de seguridad y salud en el trabajo.'},'q2': {'severidad': 'Leves', 'articulo': 'Art. 26.5', 'descripcion': 'Incumplimiento formal o documental, como no difundir la política de SST.'},'q3': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No demostrar el liderazgo del empleador, como la falta de asignación de recursos para el SGSST.'},'q4': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No contar con un Reglamento Interno de Seguridad y Salud en el Trabajo (RISST) para empresas con 20 o más trabajadores.'},'q5': {'severidad': 'Leves', 'articulo': 'Art. 26.5', 'descripcion': 'Incumplimiento documental, como no poder acreditar la entrega del RISST a cada trabajador.'},'q6': {'severidad': 'Grave', 'articulo': 'Art. 27.12', 'descripcion': 'No constituir o no designar a un supervisor o Comité de Seguridad y Salud en el Trabajo.'},'q7': {'severidad': 'Leves', 'articulo': 'Art. 26.5', 'descripcion': 'Incumplimiento formal en el proceso de elección de los representantes de los trabajadores.'},'q8': {'severidad': 'Grave', 'articulo': 'Art. 27.10', 'descripcion': 'No proporcionar la formación e información suficiente y adecuada sobre los riesgos del puesto de trabajo.'},'q9': {'severidad': 'Grave', 'articulo': 'Art. 27.12', 'descripcion': 'No asegurar el correcto funcionamiento del Comité de SST (reuniones, libro de actas).'},'q10': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No realizar la evaluación inicial o estudio de línea base del SGSST.'},'q11': {'severidad': 'Muy Grave', 'articulo': 'Art. 28.10', 'descripcion': 'No contar con el Estudio de Identificación de Peligros y Evaluación de Riesgos (IPERC).'},'q12': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No actualizar la evaluación de riesgos según lo establecido por la normativa.'},'q13': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No garantizar la participación efectiva de los trabajadores en el SGSST, incluyendo la elaboración del IPERC.'},'q14': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No elaborar y/o no exhibir el Mapa de Riesgos en un lugar visible.'},'q15': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No contar con un plan y programa anual de seguridad y salud en el trabajo.'},'q16': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No contar con un programa anual de capacitaciones.'},'q17': {'severidad': 'Grave', 'articulo': 'Art. 27.10', 'descripcion': 'No impartir la formación e información mínima obligatoria (4 al año) sobre los riesgos del puesto.'},'q18': {'severidad': 'Grave', 'articulo': 'Art. 27.10', 'descripcion': 'No proporcionar la formación e información específica en la contratación (inducción).'},'q19': {'severidad': 'Leves', 'articulo': 'Art. 26.5', 'descripcion': 'Incumplimiento formal, como la falta de registros que acrediten las capacitaciones impartidas.'},'q20': {'severidad': 'Muy Grave', 'articulo': 'Art. 28.10', 'descripcion': 'No implementar las medidas de prevención y protección aplicando la jerarquía de controles.'},'q21': {'severidad': 'Grave', 'articulo': 'Art. 27.6', 'descripcion': 'No proporcionar a los trabajadores los equipos de protección personal (EPP) adecuados.'},'q22': {'severidad': 'Leves', 'articulo': 'Art. 26.5', 'descripcion': 'Incumplimiento documental, como no mantener un registro de entrega de EPP.'},'q23': {'severidad': 'Grave', 'articulo': 'Art. 27.10', 'descripcion': 'No formar o informar a los trabajadores sobre el uso correcto de los EPP.'},'q24': {'severidad': 'Muy Grave', 'articulo': 'Art. 28.10', 'descripcion': 'No establecer los medios y precauciones adecuadas para trabajos de alto riesgo (ej. PETS).'},'q25': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No contar con planes y preparativos para la respuesta ante emergencias.'},'q26': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No designar y capacitar a las brigadas de emergencia.'},'q27': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No organizar y ejecutar simulacros de emergencia periódicamente.'},'q28': {'severidad': 'Muy Grave', 'articulo': 'Art. 28.13', 'descripcion': 'No cumplir con realizar los exámenes médicos ocupacionales y/o la vigilancia de la salud de los trabajadores.'},'q29': {'severidad': 'Grave', 'articulo': 'Art. 27.6', 'descripcion': 'No realizar las mediciones de agentes físicos, químicos, biológicos, etc., que entrañen riesgo.'},'q30': {'severidad': 'Grave', 'articulo': 'Art. 27.1', 'descripcion': 'Incumplir las obligaciones de coordinación en materia de prevención con empresas contratistas.'},'q31': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No realizar el seguimiento a los objetivos y metas del plan anual de SST.'},'q32': {'severidad': 'Grave', 'articulo': 'Art. 27.7', 'descripcion': 'No investigar los accidentes de trabajo, enfermedades ocupacionales o incidentes peligrosos.'},'q33': {'severidad': 'Grave', 'articulo': 'Art. 27.11', 'descripcion': 'No realizar las auditorías del Sistema de Gestión de SST exigidas por la normativa.'},'q34': {'severidad': 'Grave', 'articulo': 'Art. 27.8', 'descripcion': 'No llevar el registro de accidentes de trabajo, enfermedades ocupacionales e incidentes peligrosos.'},'q35': {'severidad': 'Grave', 'articulo': 'Art. 27.8', 'descripcion': 'No llevar el registro de exámenes médicos ocupacionales.'},'q36': {'severidad': 'Grave', 'articulo': 'Art. 27.8', 'descripcion': 'No llevar el registro del monitoreo de agentes (físicos, químicos, etc.).'},'q37': {'severidad': 'Grave', 'articulo': 'Art. 27.8', 'descripcion': 'No llevar el registro de inspecciones internas de seguridad y salud en el trabajo.'},'q38': {'severidad': 'Leves', 'articulo': 'Art. 26.6', 'descripcion': 'No llevar el registro de estadísticas de seguridad y salud.'},'q39': {'severidad': 'Leves', 'articulo': 'Art. 26.6', 'descripcion': 'No llevar el registro de equipos de seguridad o emergencia.'},'q40': {'severidad': 'Grave', 'articulo': 'Art. 27.8', 'descripcion': 'No llevar el registro de inducción, capacitación, entrenamiento y simulacros de emergencia.'},'q41': {'severidad': 'Grave', 'articulo': 'Art. 27.8', 'descripcion': 'No llevar el registro de auditorías.'},
}
def calcular_multa_sunafil(datos_formulario):
    tipo_empresa = datos_formulario.get("tipo_empresa", "no_mype")
    numero_trabajadores = int(datos_formulario.get("numero_trabajadores", 0))
    respuestas = datos_formulario.get("respuestas", {})
    hallazgos = {'Leves': 0, 'Grave': 0, 'Muy Grave': 0}
    lista_hallazgos_detallada = []
    for pregunta_id, respuesta in respuestas.items():
        if respuesta.lower() == 'no':
            if (tipo_empresa in ['micro', 'pequena']) and pregunta_id in PREGUNTAS_EXENTAS_MYPE:
                continue
            infraccion = BASE_DE_DATOS_INFRACCIONES.get(pregunta_id)
            if infraccion:
                hallazgos[infraccion['severidad']] += 1
                lista_hallazgos_detallada.append(infraccion)
    severidad_maxima = 'Ninguna'
    if hallazgos['Muy Grave'] > 0: severidad_maxima = 'Muy Grave'
    elif hallazgos['Grave'] > 0: severidad_maxima = 'Grave'
    elif hallazgos['Leves'] > 0: severidad_maxima = 'Leves'
    monto_multa = 0
    if severidad_maxima != 'Ninguna' and numero_trabajadores > 0:
        if tipo_empresa == 'micro':
            if numero_trabajadores <= 9: columna = str(numero_trabajadores)
            else: columna = '10 y más'
            monto_multa = TABLA_MULTAS_MICRO.loc[severidad_maxima, columna]
        elif tipo_empresa == 'pequena':
            if numero_trabajadores <= 5: columna = '1 a 5'
            elif numero_trabajadores <= 10: columna = '6 a 10'
            elif numero_trabajadores <= 20: columna = '11 a 20'
            elif numero_trabajadores <= 30: columna = '21 a 30'
            elif numero_trabajadores <= 40: columna = '31 a 40'
            elif numero_trabajadores <= 50: columna = '41 a 50'
            elif numero_trabajadores <= 60: columna = '51 a 60'
            elif numero_trabajadores <= 70: columna = '61 a 70'
            elif numero_trabajadores <= 99: columna = '71 a 99'
            else: columna = '100 y más'
            monto_multa = TABLA_MULTAS_PEQUENA.loc[severidad_maxima, columna]
        else: # No MYPE
            if numero_trabajadores <= 10: rango = '1-10'
            elif numero_trabajadores <= 25: rango = '11-25'
            elif numero_trabajadores <= 50: rango = '26-50'
            elif numero_trabajadores <= 100: rango = '51-100'
            elif numero_trabajadores <= 200: rango = '101-200'
            elif numero_trabajadores <= 300: rango = '201-300'
            elif numero_trabajadores <= 400: rango = '301-400'
            elif numero_trabajadores <= 500: rango = '401-500'
            elif numero_trabajadores <= 600: rango = '501-600'
            elif numero_trabajadores <= 700: rango = '601-700'
            elif numero_trabajadores <= 800: rango = '701-800'
            elif numero_trabajadores <= 900: rango = '801-900'
            else: rango = '901-a-mas'
            monto_multa = TABLA_MULTAS_GENERAL.loc[rango, severidad_maxima]
    return {
        "lead": {"nombre": datos_formulario.get("nombre"), "empresa": datos_formulario.get("empresa"), "cargo": datos_formulario.get("cargo"), "numero_trabajadores": numero_trabajadores, "tipo_empresa": tipo_empresa.replace('_', ' ').title()},
        "diagnostico": {"severidad_maxima": severidad_maxima, "total_incumplimientos": sum(hallazgos.values()), "resumen_hallazgos": hallazgos, "detalle_hallazgos": lista_hallazgos_detallada},
        "multa": {"monto_final_soles": float(monto_multa)}
    }
# --- FIN DE TU LÓGICA ---

app = FastAPI()

# Permitir la comunicación con tu app de React (CORS)
origins = [ "http://localhost:8080", "http://localhost:8081", "http://localhost:5173" ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatosFormulario(BaseModel):
    nombre: str
    email: str
    telefono: str
    empresa: str
    cargo: str
    numero_trabajadores: int
    tipo_empresa: str
    respuestas: Dict[str, str]

# REEMPLAZA TU FUNCIÓN ANTERIOR CON ESTA:

@app.post("/api/diagnostico")
async def ejecutar_diagnostico(request: Request):
    try:
        # Primero, intentamos leer y validar los datos que llegan
        json_data = await request.json()
        datos = DatosFormulario.model_validate(json_data)

    except ValidationError as e:
        # ¡AQUÍ ESTÁ LA TRAMPA! Si la validación falla, entramos aquí.
        print("="*50)
        print("¡ERROR DE VALIDACIÓN DETECTADO! El problema es el siguiente:")
        # Esta línea imprimirá el error exacto de una forma muy clara
        print(e.json())
        print("="*50)
        # Devolvemos el error para que el frontend sepa que algo falló
        return JSONResponse(status_code=422, content={"detail": e.errors()})

    # Si la validación fue exitosa, el resto del código se ejecuta normal
    datos_dict = datos.model_dump()
    resultado = calcular_multa_sunafil(datos_dict)

    try:
        data_to_insert = {
            'nombre_lead': resultado['lead']['nombre'],
            'empresa': resultado['lead']['empresa'],
            'cargo_lead': resultado['lead']['cargo'],
            'numero_trabajadores': resultado['lead']['numero_trabajadores'],
            'tipo_empresa': resultado['lead']['tipo_empresa'],
            'severidad_maxima': resultado['diagnostico']['severidad_maxima'],
            'monto_multa_soles': resultado['multa']['monto_final_soles'],
            'total_incumplimientos': resultado['diagnostico']['total_incumplimientos'],
            'resultado_completo_json': resultado,
            'email_lead': datos.email,
            'telefono_lead': datos.telefono
        }
        api_response = supabase.table('diagnosticos').insert(data_to_insert).execute()
        if api_response.error:
            raise Exception(api_response.error.message)
    except Exception as e:
        print(f"Error al guardar en Supabase: {e}")

    return {"status": "success", "message": "Diagnóstico recibido y procesado."}