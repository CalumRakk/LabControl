import libtmux
from libtmux.pane import Pane
import time
import re
import time


class Server:
    @property
    def pane(self) -> Pane:
        if hasattr(self, "_pane") is False:
            pane = self._create_or_get_pane()
            setattr(self, "_pane", pane)
        return getattr(self, "_pane")

    @property
    def is_online(self) -> bool:
        return self.pane.capture_pane()[-1] == ">"

    @property
    def is_connect_ssh(self) -> bool:
        # Si is_online es True, se da por hecho que ya se conectó a ssh
        if self.is_online:
            return True

        self.pane.send_keys("env")
        envs = {}
        for line in self.pane.capture_pane():
            try:
                key, value = line.split("=")
                envs.update({key: value})
            except ValueError:
                pass
        return bool(envs.get("SSH_CONNECTION"))

    def _create_or_get_pane(self) -> Pane:
        server = libtmux.Server()
        if server.has_session(SESSION_NAME):
            session = server.sessions.filter(session_name=SESSION_NAME)[0]
        else:
            session = server.new_session(SESSION_NAME)

        session = server.sessions[0]
        if len(session.windows) > 0:
            window = session.select_window(0)
        else:
            window = session.new_window(attach=False, window_name="test")

        pane = session.active_pane or window.split(attach=False)
        return pane

    def _conect_to_ssh(self):
        self.pane.send_keys(SSH_COMMAND)
        sleep_time = 0
        while self.is_connect_ssh is False:
            time.sleep(0.5)
            sleep_time += 0.5
            if sleep_time > 10:
                raise Exception("No se pudo conectar al servidor SSH.")

    def start(self) -> Pane:
        if self.is_connect_ssh is False:
            self._conect_to_ssh()

        if self.is_online is False:
            self.pane.send_keys(f"cd {FOLDER_SERVER}")
            self.pane.send_keys(f"bash run.sh")

            time_sleep = 0
            while True:
                if self.is_online:
                    self.pane.send_keys("setidletimeout 5")
                    break
                time.sleep(0.5)
                time_sleep += 0.5
                if time_sleep > 20:
                    raise Exception("No se pudo iniciar el servidor de Minecraft.")

    def get_player_count(self) -> int:
        if self.is_online:
            self.pane.send_keys("list")
            time.sleep(0.1)
            for line in self.pane.capture_pane()[::-1]:
                match = regex_player_count.search(line)
                if match:
                    return int(match.group(1))
        else:
            raise Exception(
                "No se pudo obtener el conteo de jugadores porque el servidor no está online."
            )

    def stop(self):
        if self.is_connect_ssh is False:
            self._conect_to_ssh()

        if self.is_online:
            self.pane.send_keys("stop")
        else:
            raise Exception("No se pudo detener el servidor de Minecraft.")
