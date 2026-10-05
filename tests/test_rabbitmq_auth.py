import hashlib
import hmac

import pytest

from mythic_container import rabbitmq


def test_signed_message_binds_route_body_and_principal(monkeypatch):
    secret = hashlib.sha256(b"service-secret").digest()
    values = {
        "mythic_container_principal": "alpha",
        "mythic_container_auth_token": secret.hex(),
        "rabbitmq_user": "mythic_user",
    }
    monkeypatch.setattr(rabbitmq.settings, "get", lambda key, default=None: values.get(key, default))
    monkeypatch.setattr(rabbitmq.time, "time", lambda: 1_800_000_000)
    monkeypatch.setattr(rabbitmq.secrets, "token_hex", lambda _: "ab" * 24)
    rabbitmq._request_auth_contexts.clear()
    rabbitmq._request_auth_contexts["operation_id:7"] = (
        "mctx_operation", rabbitmq.time.time() + 3600, False
    )
    body = b'{"operation_id":7}'

    message = rabbitmq._signed_message("route", body, content_type="application/json")

    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"v1\nalpha\nroute\n1800000000\n{'ab' * 24}\n{body_hash}"
    assert message.user_id == "mythic_user"
    assert message.headers[rabbitmq.MYTHIC_CONTAINER_SIGNATURE_HEADER] == hmac.new(
        secret, canonical.encode(), hashlib.sha256
    ).hexdigest()
    assert message.headers[rabbitmq.MYTHIC_AUTH_CONTEXT_HEADER] == "mctx_operation"


def test_signed_message_fails_closed_without_identity(monkeypatch):
    monkeypatch.setattr(rabbitmq.settings, "get", lambda key, default=None: default)
    with pytest.raises(ValueError, match="PRINCIPAL"):
        rabbitmq._signed_message("route", b"{}")


def test_auth_context_correlates_task_request_and_response():
    rabbitmq._request_auth_contexts.clear()
    incoming = type("Incoming", (), {
        "headers": {rabbitmq.MYTHIC_AUTH_CONTEXT_HEADER: "mctx_task"},
        "body": b'{"task":{"id":42},"callback":{"operation_id":7}}',
        "routing_key": "alpha_payload_build",
    })()
    rabbitmq._remember_auth_context(incoming)

    assert rabbitmq._request_auth_contexts["task_id:42"][0] == "mctx_task"


def test_auth_context_cache_rejects_ambiguous_identifiers():
    rabbitmq._request_auth_contexts.clear()
    body = b'{"task":{"id":42}}'
    for token in ("mctx_one", "mctx_two"):
        incoming = type("Incoming", (), {
            "headers": {rabbitmq.MYTHIC_AUTH_CONTEXT_HEADER: token},
            "body": body,
            "routing_key": "alpha_payload_build",
        })()
        rabbitmq._remember_auth_context(incoming)

    with pytest.raises(ValueError, match="ambiguous"):
        rabbitmq._cached_auth_context(b'{"task_id":42}')
