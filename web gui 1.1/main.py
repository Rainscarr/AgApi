from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  

token = None

@app.route("/", methods=["GET", "POST"])
def login():
    global token

    if request.method == "POST":
        user_login = request.form.get("username")
        user_password = request.form.get("password")

        if not user_login or not user_password:
            flash("Введите логин и пароль!", "danger")
            return redirect(url_for("login"))

        auth_url = "https://srv2.tk-map.ru/ServiceJSON/Login"
        auth_params = {
            "UserName": user_login,
            "Password": user_password,
            "UTCOffset": 180
        }

        auth_response = requests.get(auth_url, params=auth_params)

        if auth_response.status_code == 200 and auth_response.text:
            token = auth_response.text.strip('"')
            flash("Авторизация прошла успешно!", "success")
            return redirect(url_for("menu"))
        elif auth_response.status_code == 401:
            flash("Неверный логин или пароль.", "danger")
            return redirect(url_for("login"))
        else:
            flash(f"Ошибка: {auth_response.status_code}, {auth_response.text}", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/menu")
def menu():
    global token
    if not token:
        flash("Вы не авторизованы!", "danger")
        return redirect(url_for("login"))

    return render_template("menu.html")


@app.route("/get_schemas")
def get_schemas():
    global token
    if not token:
        flash("Вы не авторизованы!", "danger")
        return redirect(url_for("login"))

    schemas_url = "https://srv2.tk-map.ru/ServiceJSON/EnumSchemas"
    schemas_params = {"session": token}

    schemas_response = requests.get(schemas_url, params=schemas_params)

    if schemas_response.status_code != 200:
        flash(f"Ошибка запроса схем: {schemas_response.status_code}", "danger")
        return redirect(url_for("menu"))

    try:
        schemas = schemas_response.json()
    except Exception as e:
        flash(f"Ошибка при обработке JSON для схем: {e}", "danger")
        return redirect(url_for("menu"))

    result = "Список схем:<br>"
    for schema in schemas:
        result += f"ID: {schema['ID']}, Name: {schema['Name']}<br>"

    return render_template("result.html", title="Список схем", content=result)


@app.route("/get_devices")
def get_devices():
    global token
    if not token:
        flash("Вы не авторизованы!", "danger")
        return redirect(url_for("login"))

    schemas_url = "https://srv2.tk-map.ru/ServiceJSON/EnumSchemas"
    schemas_params = {"session": token}

    schemas_response = requests.get(schemas_url, params=schemas_params)

    if schemas_response.status_code != 200:
        flash(f"Ошибка запроса схем: {schemas_response.status_code}", "danger")
        return redirect(url_for("menu"))

    try:
        schemas = schemas_response.json()
    except Exception as e:
        flash(f"Ошибка при обработке JSON для схем: {e}", "danger")
        return redirect(url_for("menu"))

    devices_url = "https://srv2.tk-map.ru/ServiceJSON/EnumDevices"
    result = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        h2 {
            border-top: 2px solid #000;
            padding-top: 10px;
            margin-top: 20px;
        }
    </style>
    <h1>Список техники</h1>
    """

    for schema in schemas:
        schema_id = schema["ID"]
        schema_name = schema["Name"]

        devices_params = {"session": token, "schemaID": schema_id}
        devices_response = requests.get(devices_url, params=devices_params)

        if devices_response.status_code == 200:
            devices_data = devices_response.json()
            items = devices_data.get("Items", [])
            if items:
                result += f'<h2>Схема: "{schema_name}"</h2>'
                result += '<table>'
                result += '<tr><th>№</th><th>Имя объекта</th><th>Серийный номер</th></tr>'
                for idx, item in enumerate(items, start=1):
                    name = item.get("Name", "Не указано")
                    serial = item.get("Serial", "Не указан")
                    result += f"<tr><td>{idx}</td><td>{name}</td><td>{serial}</td></tr>"
                result += "</table>"

    return render_template("result.html", title="Список техники", content=result)




@app.route("/send_commands")
def send_commands():
    flash("Функционал пока недоступен!", "info")
    return redirect(url_for("menu"))


@app.route("/add_object")
def add_object():
    flash("Функционал пока недоступен!", "info")
    return redirect(url_for("menu"))


@app.route("/delete_object")
def delete_object():
    flash("Функционал пока недоступен!", "info")
    return redirect(url_for("menu"))


if __name__ == "__main__":
    app.run(debug=True)
