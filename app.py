from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Необходимо для работы сессий


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('users.db')  # Соединение с базой данных
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def login():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def authenticate():
    login = request.form['Login']
    password = request.form['Password']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password)).fetchone()
    conn.close()

    if user:
        # Сохраняем информацию о пользователе в сессии
        session['user_id'] = user['id']
        session['login'] = user['login']
        session['first_name'] = user['firstname']
        session['last_name'] = user['lastname']
        session['mail'] = user['login']  # Предполагается, что поле 'email' есть в базе данных

        # Если пользователь найден, перенаправляем на страницу home
        return redirect(url_for('home'))
    else:
        # Если пользователь не найден, отображаем ошибку
        return render_template('index.html', error_message="Введен неверный логин или пароль!")


@app.route("/reg", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        # Извлечение данных из формы
        login = request.form['Mail']
        password = request.form['Password']
        first_name = request.form['First Name']
        last_name = request.form['Last Name']

        # Проверка на пустые поля
        if login != "" and password != "" and first_name != "" and last_name != "":
            conn = get_db_connection()
            conn.execute('INSERT INTO users (login, password, firstname, lastname) VALUES (?, ?, ?, ?)',
                         (login, password, first_name, last_name))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))  # Перенаправление на страницу логина
        else:
            return render_template('reg.html', error_message="Все поля обязательны для заполнения")

    return render_template('reg.html')  # Для GET-запроса отобразим форму регистрации


@app.route("/home", methods=["GET", "POST"])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу логина

    # Извлекаем информацию о пользователе из сессии
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    mail = session.get('mail')

    # Обработка данных VIN
    vin = request.form.get('vin')
    if vin:
        asbuild_data = get_asbuild_data(vin)  # Получаем данные по VIN (это должно быть реализовано)
        return render_template("home.html", first_name=first_name, last_name=last_name, email=mail,
                               asbuild_data=asbuild_data)

    return render_template("home.html", first_name=first_name, last_name=last_name, email=mail)


@app.route('/logout')
def logout():
    session.clear()  # Очищаем сессию
    return redirect(url_for('login'))  # Перенаправляем на страницу логина


# Функция для получения данных по VIN
def get_asbuild_data(vin):
    # Пока что фейковые данные для примера
    asbuild_data = {
        "vin": vin,
        "model": "Ford Focus",
        "year": "2020",
        "engine": "1.5L EcoBoost",
        "transmission": "Automatic",
        "color": "Red"
    }
    return asbuild_data


# Реализация API для получения данных о VIN
@app.route('/api/vin/<vin>', methods=['GET'])
def api_get_vin_data(vin):
    # Получаем данные по VIN
    asbuild_data = get_asbuild_data(vin)  # Здесь можно подключить реальное API
    return jsonify(asbuild_data)  # Отправляем данные в формате JSON


if __name__ == '__main__':
    app.run(debug=True)
