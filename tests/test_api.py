import io

from api import create_app


class FakePipeline:
    def analyze(self, path, context=None):
        return {
            "signals": {}, "quality": {}, "review": {"level": "STANDARD"},
            "media": {"duration_s": 5}, "case_context": context or {},
        }


def client():
    app = create_app(FakePipeline())
    app.config.update(TESTING=True)
    return app.test_client()


def test_home_and_health():
    web = client()
    assert web.get("/").status_code == 200
    assert web.get("/api/health").json["service"] == "DeepShield ApprovalGuard"


def test_scenarios_are_directly_runnable():
    web = client()
    scenarios = web.get("/api/scenarios").json
    assert len(scenarios) == 4
    response = web.post(f"/api/scenarios/{scenarios[0]['sample_id']}/analyze")
    assert response.status_code == 200
    assert response.json["scenario"]["benchmark_eligible"] == "no"


def test_upload_contract_and_context_boundary():
    web = client()
    response = web.post("/api/analyze", data={
        "file": (io.BytesIO(b"fixture"), "approval.mp4"),
        "context": '{"workflow":"supplier_payment"}',
    })
    assert response.status_code == 200
    assert response.json["case_context"]["workflow"] == "supplier_payment"


def test_upload_rejects_invalid_extension():
    response = client().post("/api/analyze", data={"file": (io.BytesIO(b"x"), "notes.txt")})
    assert response.status_code == 415
