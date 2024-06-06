from django.shortcuts import render
from django.http import HttpResponse
import json

status = "ON"


def get_switch_state():
    return status


def update_switch_state(state):
    global status
    status = state
    data = {
        "status": status,
    }

    json_data = json.dumps(data)
    return json_data


def auto(request):
    if request.method == "POST":
        current_state = get_switch_state()
        if current_state == "ON":
            new_state = "OFF"
        else:
            new_state = "ON"
        json_data = update_switch_state(new_state)

        response = HttpResponse(json_data, content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        return response

    # Envía una respuesta al cliente
    return render(request, "host/index.html", {"switch_state": get_switch_state()})
