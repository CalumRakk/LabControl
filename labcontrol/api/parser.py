def parse_set_cookies(set_cookie_headers):
    """Parsea Set-Cookie en un diccionario de cookies."""
    parts = [p.strip() for p in set_cookie_headers.split(",")]

    if not parts:
        return {}

    cookies = {}
    current_cookie = None
    
    for part in parts:
        segments = [s.strip() for s in part.split(";")]   

        # Si el primer segmento contiene '=', es una nueva cookie
        if "=" in segments[0]:
            name, value = segments[0].split("=", 1)
            current_cookie = name
            cookies[current_cookie] = {
                "value": value,
                "attributes": {}
            }
            attr_segments = segments[1:]
        else:
            # Es un atributo de la cookie anterior
            attr_segments = segments

        for attr in attr_segments:
            if "=" in attr:
                k, v = attr.split("=", 1)
                cookies[current_cookie]["attributes"][k.lower()] = v
            else:
                cookies[current_cookie]["attributes"][attr.lower()] = True
    return cookies