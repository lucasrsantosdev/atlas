from atlas.mosaic import (
    CapabilityType,
    IntentType,
    MosaicResult,
)


def test_mosaic_result_contract() -> None:
    result = MosaicResult(
        intent=IntentType.QUESTION,
        domain="atlas",
        is_task=False,
        requires_context=False,
        entities=("Mosaic",),
        required_capabilities=(CapabilityType.FAST,),
    )

    assert result.intent is IntentType.QUESTION
    assert result.domain == "atlas"
    assert result.is_task is False
    assert result.requires_context is False
    assert result.entities == ("Mosaic",)
    assert result.required_capabilities == (CapabilityType.FAST,)
