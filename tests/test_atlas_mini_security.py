import json
from atlas.security.policy import PolicyEngine, Permission, AuditLog


def test_approval_wrong_scope_does_not_destroy_valid_token():
    policy = PolicyEngine([Permission.HARDWARE_WRITE])
    token = policy.issue_approval(Permission.HARDWARE_WRITE, scope="servo:head")
    assert not policy.consume_approval(token, Permission.HARDWARE_WRITE, scope="servo:arm")
    assert policy.consume_approval(token, Permission.HARDWARE_WRITE, scope="servo:head")
    assert not policy.consume_approval(token, Permission.HARDWARE_WRITE, scope="servo:head")


def test_audit_file_detects_tampering(tmp_path):
    path = tmp_path / "audit.jsonl"
    audit = AuditLog(path)
    audit.record(event="example", allowed=False)
    assert audit.verify_file()
    events = [json.loads(x) for x in path.read_text().splitlines()]
    events[0]["allowed"] = True
    path.write_text(json.dumps(events[0]) + "\n")
    assert not audit.verify_file()
