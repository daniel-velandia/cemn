from flask import Flask, render_template, request
import re

app = Flask(__name__)

def resolver_raices(ecuacion):
    patron = r"sqrt\(([xy])\)"

    raices = re.findall(patron, ecuacion)

    for raiz in raices:
        ecuacion = ecuacion.replace(f"sqrt({raiz})", f"{raiz}^(1/2)")

    return ecuacion

def resolver_trigonometricas(ecuacion):
    patron = r"(sin|cos|tan)\(([xy])\)"

    funciones_trig = re.findall(patron, ecuacion)

    for funcion, variable in funciones_trig:
        if funcion == 'sin':
            ecuacion = ecuacion.replace(f"sin({variable})", f"{variable}")
        elif funcion == 'cos':
            ecuacion = ecuacion.replace(f"cos({variable})", f"{variable}")
        elif funcion == 'tan':
            ecuacion = ecuacion.replace(f"tan({variable})", f"{variable}")

    return ecuacion

def verificar_homogeneidad(ecuacion):
    ecuacion_resuelta = resolver_raices(ecuacion)
    ecuacion_resuelta = resolver_trigonometricas(ecuacion_resuelta)

    patron = r"([+-]?\d*)(?:\*?([xy])(?:\^(-?\d+))?)?"

    matches = re.findall(patron, ecuacion_resuelta)

    exponentes_x = 0
    exponentes_y = 0

    for match in matches:
        coeficiente, variable, exponente = match
        if exponente:
            exponente = eval(exponente)
        else:
            exponente = 1
        if variable == 'x':
            exponentes_x += exponente
        elif variable == 'y':
            exponentes_y += exponente

    if exponentes_x == exponentes_y:
        return True
    else:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    text = None
    if request.method == 'POST':
        if request.form['text'] != "":
            homogenea = verificar_homogeneidad(request.form['text'])
            if homogenea:
                text = "Ecuación homogénea."
            else:
                text = "Ecuación no homogénea."

    return render_template('index.html', text=text)

if __name__ == '__main__':
    app.run(debug=True)
