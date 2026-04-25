from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Memoria del servidor
estado_led = False
contador_total = 0
ultima_actualizacion = "Sin registros" # <--- Para guardar fecha y hora

HTML_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel IoT AslanNova</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; background-color: #f0f4f8; margin-top: 40px; }
        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); text-align: center; width: 500px; }
        
        /* Contenedor para mostrar datos a los costados */
        .grid-datos { display: flex; justify-content: space-around; align-items: center; margin: 30px 0; border-top: 1px solid #eee; border-bottom: 1px solid #eee; padding: 20px 0; }
        
        .dato-box { flex: 1; }
        .label { font-size: 14px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }
        .valor { font-size: 32px; font-weight: bold; color: #2c3e50; }
        .timestamp { font-size: 18px; color: #34495e; font-weight: 500; }
        
        button { padding: 15px; width: 100%; font-size: 16px; cursor: pointer; border-radius: 12px; border: none; color: white; font-weight: 600; transition: 0.3s; }
        .on { background-color: #27ae60; }
        .off { background-color: #e74c3c; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Control de Dispositivo - SPRINT 2026</h2>
        
        <div class="grid-datos">
            <div class="dato-box" style="border-right: 1px solid #eee;">
                <div class="label">Pulsos</div>
                <div id="conteo" class="valor">0</div>
            </div>
            <div class="dato-box">
                <div class="label">Última Recepción</div>
                <div id="fecha_hora" class="timestamp">Esperando datos...</div>
            </div>
        </div>

        <button id="btnLed" class="off" onclick="toggleLed()">ENCENDER LED EXTERNO</button>
    </div>
    
    <script>
        let ledLocal = false;

        async function toggleLed() {
            ledLocal = !ledLocal;
            actualizarBoton(ledLocal);
            await fetch('/api/led', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ estado: ledLocal })
            });
        }

        function actualizarBoton(estado) {
            const btn = document.getElementById('btnLed');
            btn.className = estado ? 'on' : 'off';
            btn.innerText = estado ? 'APAGAR LED EXTERNO' : 'ENCENDER LED EXTERNO';
        }

        async function sincronizar() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('conteo').innerText = data.contador;
                document.getElementById('fecha_hora').innerText = data.timestamp;
                
                if(data.led !== ledLocal) {
                    ledLocal = data.led;
                    actualizarBoton(ledLocal);
                }
            } catch (e) { console.error("Error de sincronización"); }
        }

        setInterval(sincronizar, 800);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    global contador_total, ultima_actualizacion
    datos = request.json
    contador_total = datos.get('contador', contador_total)
    ultima_actualizacion = datos.get('timestamp', 'Error de tiempo')
    
    print(f"\n[REGISTRO] Pulso #{contador_total} recibido a las {ultima_actualizacion}")
    return jsonify({"status": "ok"}), 200

@app.route('/api/status', methods=['GET'])
def obtener_status():
    return jsonify({
        "contador": contador_total,
        "timestamp": ultima_actualizacion,
        "led": estado_led
    }), 200

@app.route('/api/led', methods=['POST', 'GET'])
def manejar_led():
    global estado_led
    if request.method == 'POST':
        estado_led = request.json.get('estado', False)
        return jsonify({"status": "ok"}), 200
    return jsonify({"estado": estado_led}), 200

#if __name__ == '__main__':
 #   app.run(host='0.0.0.0', port=5000)