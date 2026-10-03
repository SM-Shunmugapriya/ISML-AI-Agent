from services.model_router import ModelRouter


def test_simple_task_uses_cheap_model():
    router = ModelRouter()

    route = router.route("Find Python learning resources")

    assert route.provider == "gemini"
    assert route.model == "gemini-3.6-flash"


def test_complex_task_uses_capable_model():
    router = ModelRouter()

    route = router.route(
        "Analyze and compare the architecture of two systems"
    )

    assert route.provider == "deepseek"
    assert route.model == "deepseek-chat"


def test_debug_task_uses_capable_model():
    router = ModelRouter()

    route = router.route(
        "Debug this complex Python workflow"
    )

    assert route.provider == "deepseek"
    assert route.model == "deepseek-chat"


def test_normal_task_defaults_to_simple_model():
    router = ModelRouter()

    route = router.route("Give me Python vocabulary")

    assert route.provider == "gemini"
    assert route.model == "gemini-3.6-flash"
