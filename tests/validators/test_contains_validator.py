from opyapi import build_validator_for


def test_pass_validate_minimum() -> None:
    # given
    validator = build_validator_for(
        {
            "contains": {
                "minimum": 5,
            }
        }
    )

    # then
    assert validator([1, 2, 5, 4])
