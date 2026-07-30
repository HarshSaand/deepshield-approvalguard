from approvalguard.pipeline import ApprovalGuardPipeline


def test_review_escalates_two_high_signals():
    signals = {"voice_ai": {"available": True, "score": 82},
               "visual_ai": {"available": True, "score": 71},
               "lip_sync": {"available": True, "score": 20}}
    result = ApprovalGuardPipeline._decision(signals, {"audio_sufficient": True, "video": {"sufficient": True}})
    assert result["level"] == "ESCALATE"
    assert result["priority_is_probability"] is False


def test_review_keeps_signals_separate():
    signals = {"voice_ai": {"available": True, "score": 40},
               "visual_ai": {"available": True, "score": 30}}
    result = ApprovalGuardPipeline._decision(signals, {"audio_sufficient": True, "video": {"sufficient": True}})
    assert result["level"] == "STANDARD"
    assert result["priority_index"] == 35


def test_empty_signals_abstain():
    result = ApprovalGuardPipeline._decision({"voice_ai": {"available": False}}, {})
    assert result["level"] == "INSUFFICIENT EVIDENCE"
