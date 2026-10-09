import json
import threading
import urllib.error
import urllib.request

import pytest

from tutorial.gui import crt_iat_gui


def test_gui_server_health_endpoint_and_graceful_shutdown():
    server = crt_iat_gui.create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/health"

    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            payload = json.load(response)
        assert payload["status"] == "ok"
        assert payload["port"] == server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert not thread.is_alive()
    with pytest.raises(urllib.error.URLError):
        urllib.request.urlopen(url, timeout=1)


def test_gui_port_can_be_selected_without_changing_default(monkeypatch):
    monkeypatch.delenv("ACCERT_GUI_PORT", raising=False)
    assert crt_iat_gui.resolve_gui_port() == crt_iat_gui.PORT

    monkeypatch.setenv("ACCERT_GUI_PORT", "9876")
    assert crt_iat_gui.resolve_gui_port() == 9876
