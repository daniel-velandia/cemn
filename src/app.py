from flask import Flask, render_template, request
import re
import numpy as np
from math import sqrt
from math import sin
from math import cos

app = Flask(__name__)

def euler(f, x0, y0, N, xf):
    # Calcular el paso
    h = abs(xf - x0) / N

    # Vector x
    x = np.linspace(x0, xf, N+1)

    # Vector y
    y = np.zeros(N + 1)

    # Primera fila es la condición inicial
    y[0] = y0

    # Resolver la ecuación diferencial
    for i in range(1, N + 1):
        # Verificar si x = 0 para evitar dividir por cero
        if x[i - 1] != 0:
            y[i] = y[i - 1] + h * f(x[i - 1], y[i - 1])
        else:
            # Si x = 0, establecer el término en cero (u otra manipulación según la ecuación)
            y[i] = y[i - 1]  # Podrías establecerlo en otro valor si es más apropiado
    return x, y

def runge_kutta(f, x0, y0, N, xf):
    # Calcular el paso
    h = abs(xf - x0) / N

    # Vector x
    x = np.linspace(x0, xf, N+1)

    # Vector y
    y = np.zeros(N + 1)

    # Primera fila es la condición inicial
    y[0] = y0

    # Resolver la ecuación diferencial utilizando el método de Runge-Kutta de cuarto orden
    for i in range(1, N + 1):
        if x[i - 1] != 0:
            k1 = h * f(x[i - 1], y[i - 1])
            k2 = h * f(x[i - 1] + h / 2, y[i - 1] + k1 / 2)
            k3 = h * f(x[i - 1] + h / 2, y[i - 1] + k2 / 2)
            k4 = h * f(x[i - 1] + h, y[i - 1] + k3)
            y[i] = y[i - 1] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        else:
            # Si x = 0, manejar de manera especial
            y[i] = y[i - 1]  # Podrías establecerlo en otro valor si es más apropiado

    return x, y

def taylor_method(f, x0, y0, N, xf):
    # Calcular el paso (reduciendo a la mitad)
    h = abs(xf - x0) / (2 * N)

    # Vector x
    x = np.linspace(x0, xf, N+1)

    # Vector y
    y = np.zeros(N + 1)

    # Primera fila es la condición inicial
    y[0] = y0

    # Resolver la ecuación diferencial utilizando el método de Taylor
    for i in range(1, N + 1):
        if x[i - 1] != 0:
            y[i] = y[i - 1] + h * f(x[i - 1], y[i - 1])
        else:
            # Si x = 0, manejar de manera especial
            y[i] = y[i - 1]  # Podrías establecerlo en otro valor si es más apropiado

    return x, y

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
    error = None
    results = {
        'euler': None,
        'runge_kutta': None,
        'taylor': None
    }
    if request.method == 'POST':
        if request.form['text'] != "":
            eq_str = request.form['text']
            homogenea = verificar_homogeneidad(eq_str)
            if homogenea:
                text = "Ecuación homogénea."
            else:
                text = "Ecuación no homogénea."

                try:
                    # Convertir la cadena a una función de Python
                    f = eval('lambda x, y: ' + eq_str.replace('^', '**'))
                    
                    # Definir condiciones iniciales y parámetros
                    x0 = 0  # Punto inicial
                    y0 = 1  # Valor inicial de y en x0
                    N = 10  # Número de pasos
                    xf = 1  # Punto final

                    # Resolver la ecuación diferencial utilizando los tres métodos
                    results['euler'] = euler(f, x0, y0, N, xf)
                    results['runge_kutta'] = runge_kutta(f, x0, y0, N, xf)
                    results['taylor'] = taylor_method(f, x0, y0, N, xf)
                except Exception as e:
                    error = f"Error al resolver la ecuación diferencial: {str(e)}"
                    text = None

    return render_template('index.html', text=text, error=error, results=results)


if __name__ == '__main__':
    app.run(debug=True)

# eq1 = "2*sqrt(x^4) + 3*sqrt(y^4) - 5*x*y + y^2/x^2 + sin(x^2) + cos(y^2)"
# eq2 = "sin(x^2) + sqrt(y^3) - 4*x*y + x/y^2 + cos(y^2)"
# eq3 = "x^3/y^2 + sqrt(x^2 + y^2) - 3*x*y + sin(x)/y^3 + cos(y)"
# eq4 = "sqrt(x^2 + y^2) - 2*sin(x) + 3*cos(y) + x^2/y^3 + y/x^2"