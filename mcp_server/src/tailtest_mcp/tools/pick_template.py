"""tailtest_pick_template tool.

Returns the full framework R2 template for a given source file: language
baseline scenarios, framework-specific scenarios, framework-specific
Scenario rules text (from the rule layer), and test file path conventions.

Distinct from scenario_plan: scenario_plan returns lightweight scaffolding
suitable for a single SCENARIO PLAN; pick_template returns the full R2
contract text for cases where the agent wants the verbatim framework rule
guidance (e.g., NestJS Test.createTestingModule patterns, Spring @WebMvcTest
patterns, Flask test_client / app.app_context patterns).

Used by the slash workflow `/tailtest-test` and by `tailtest_setup` when
seeding the .clinerules/ pack.
"""

from __future__ import annotations

import os
import sys
from typing import Any

# vendored lib path
_LIB_PATH = os.path.join(os.path.dirname(__file__), "..", "lib")
if _LIB_PATH not in sys.path:
    sys.path.insert(0, _LIB_PATH)

from filter import detect_language  # noqa: E402


# Full framework templates: structured Scenario rules text per framework.
# These mirror the Scenario rules section of clinerules/01-tailtest-baseline.md
# (which itself mirrors tailtest-cursor/rules/tailtest.mdc).

FRAMEWORK_TEMPLATES: dict[str, dict[str, Any]] = {
    "flask": {
        "language": "python",
        "baseline_scenarios": [
            "Route returns 200 on valid path",
            "404 on unknown route",
            "Blueprint registration binds the correct prefix",
            "test_client fixture used within app context",
            "Validation rejects bad input",
        ],
        "test_pattern": (
            "Use Flask's test_client() context manager: "
            "`with app.test_client() as client: response = client.get('/orders')`. "
            "Always create the app via your application factory within a test fixture. "
            "Activate the app context with `with app.app_context():` when touching db/config/extensions. "
            "When pytest-flask is in deps, prefer its `client` and `app` fixtures."
        ),
        "test_file_path": "tests/test_{basename}.py",
    },
    "fastapi": {
        "language": "python",
        "baseline_scenarios": [
            "Valid request body returns expected response",
            "Missing required field returns 422",
            "Wrong field type returns 422",
            "Dependency override works in test (app.dependency_overrides)",
        ],
        "test_pattern": (
            "Use TestClient from starlette.testclient. "
            "Instantiate with the app object: `client = TestClient(app)`. "
            "Override Depends() injections via `app.dependency_overrides[original_dep] = lambda: mock_dep` "
            "to keep tests off the live database / external services."
        ),
        "test_file_path": "tests/test_{basename}.py",
    },
    "django": {
        "language": "python",
        "baseline_scenarios": [
            "Request with valid auth",
            "Request without auth (expect 403/redirect)",
            "Model field validation rejects invalid data",
            "URL routes to the correct view",
        ],
        "test_pattern": (
            "Use Django's TestCase with the test client. "
            "Tests should hit views via `client.get(reverse('view_name'))`. "
            "Model validation errors surface via `full_clean()`."
        ),
        "test_file_path": "tests/test_{basename}.py",
    },
    "nestjs": {
        "language": "typescript",
        "baseline_scenarios": [
            "Valid DTO passes class-validator",
            "Invalid DTO returns 400",
            "Guard rejects unauthenticated request",
            "Service replaced via Test.createTestingModule override",
            "Controller-style (HTTP via supertest) or microservice-style (ClientProxy) test harness as appropriate",
        ],
        "test_pattern": (
            "Use Test.createTestingModule to wire providers, guards, interceptors. "
            "Override providers via `.overrideProvider(Token).useValue(mock)`. "
            "For e2e/controller tests, compile with createNestApplication() and exercise via supertest. "
            "For microservice transports use ClientProxy + ClientsModule.register(...)."
        ),
        "test_file_path": "__tests__/{basename}.test.ts",
    },
    "spring": {
        "language": "java",
        "baseline_scenarios": [
            "Valid request returns 200",
            "Missing required field returns 400",
            "Unauthenticated request returns 401",
            "Controller slice test with @WebMvcTest",
            "Service dependency overridden via @MockBean",
        ],
        "test_pattern": (
            "Use @SpringBootTest for integration tests, @WebMvcTest for controller slice tests. "
            "Use MockMvc for controller tests, @MockBean for service dependencies."
        ),
        "test_file_path": "src/test/java/{basename}Test.java",
    },
    "kotlin": {
        "language": "kotlin",
        "baseline_scenarios": [
            "null input scenarios on nullable parameters",
            "Empty collection",
            "zero, negative",
            "Result.failure",
        ],
        "test_pattern": (
            "Tests live in src/test/kotlin/. Prefer kotlin.test assertions. "
            "Use JUnit 5 for lifecycle. For coroutines wrap in runTest { } from kotlinx-coroutines-test "
            "(never runBlocking). For sealed class hierarchies, use when expression with else -> error()."
        ),
        "test_file_path": "src/test/kotlin/{basename}Test.kt",
    },
    "csharp": {
        "language": "csharp",
        "baseline_scenarios": [
            "null input",
            "default(T)",
            "empty IEnumerable<T>",
            "ArgumentNullException on invalid input",
            "zero / negative numeric",
        ],
        "test_pattern": (
            "Tests go in a sibling *.Tests project. "
            "Detect framework from .csproj <PackageReference> elements: xunit / NUnit / MSTest. "
            "Use Moq for mocking. "
            "Never mock DbContext directly; use UseInMemoryDatabase or SQLite in-memory. "
            "For ASP.NET Core integration tests use WebApplicationFactory<Program>."
        ),
        "test_file_path": "tests/{basename}Tests.cs",
    },
}


# Language baselines (R1 from rule layer)
LANGUAGE_BASELINES: dict[str, list[str]] = {
    "python": ["None input", "empty list/dict", "zero", "negative number", "wrong type passed"],
    "typescript": ["undefined", "null", "NaN", "wrong type", "empty string"],
    "javascript": ["undefined", "null", "NaN", "wrong type", "empty string"],
    "go": ["zero value", "empty struct", "nil pointer"],
    "ruby": ["nil", "empty array", "zero"],
    "java": ["null", "empty collection", "zero", "negative"],
    "kotlin": ["null", "empty collection", "zero", "negative", "Result.failure"],
    "csharp": [
        "null",
        "default(T)",
        "empty IEnumerable<T>",
        "ArgumentNullException on invalid input",
        "zero / negative numeric",
    ],
    "php": ["null", "empty array", "zero", "empty string"],
    "rust": ["empty input", "boundary values (0, u32::MAX or equivalent)"],
}


def _detect_framework(language: str, project_root: str) -> str | None:
    """Detect framework from project files. V14.2 lightweight version."""
    if language == "python":
        for f in ("requirements.txt", "pyproject.toml", "setup.py"):
            path = os.path.join(project_root, f)
            if os.path.exists(path):
                try:
                    with open(path) as fh:
                        text = fh.read().lower()
                    if "fastapi" in text:
                        return "fastapi"
                    if "flask" in text:
                        return "flask"
                    if "django" in text:
                        return "django"
                except OSError:
                    pass
    elif language == "typescript":
        pkg = os.path.join(project_root, "package.json")
        if os.path.exists(pkg):
            try:
                with open(pkg) as fh:
                    text = fh.read().lower()
                if "@nestjs/" in text:
                    return "nestjs"
            except OSError:
                pass
    elif language == "java":
        pom = os.path.join(project_root, "pom.xml")
        gradle = os.path.join(project_root, "build.gradle")
        for path in (pom, gradle):
            if os.path.exists(path):
                try:
                    with open(path) as fh:
                        text = fh.read().lower()
                    if "spring-boot" in text or "springframework" in text:
                        return "spring"
                except OSError:
                    pass
    elif language == "kotlin":
        gradle = os.path.join(project_root, "build.gradle.kts")
        if os.path.exists(gradle):
            return "kotlin"
    elif language == "csharp":
        # Any .csproj triggers the C# template
        for f in os.listdir(project_root) if os.path.isdir(project_root) else []:
            if f.endswith(".csproj"):
                return "csharp"
    return None


def pick_template(file_path: str, project_root: str | None = None) -> dict[str, Any]:
    """Return the full framework R2 template for the given source file.

    Args:
        file_path: relative or absolute path to the source file.
        project_root: project root for framework detection. Defaults to cwd.

    Returns:
        Dict with: language, framework (or None), language_baseline,
        framework_template (or None), test_file_path_pattern, instructions.

    If no framework matches, returns just the language baseline.
    """
    project_root = project_root or os.getcwd()

    language = detect_language(file_path) or "unknown"
    framework = _detect_framework(language, project_root)

    language_baseline = LANGUAGE_BASELINES.get(language, [])
    framework_template = FRAMEWORK_TEMPLATES.get(framework) if framework else None

    instructions = (
        f"Use the language baseline scenarios for {language}: "
        f"{', '.join(language_baseline) or 'none specified'}. "
    )
    if framework_template:
        instructions += (
            f"Add framework-specific scenarios for {framework} on top: "
            f"{'; '.join(framework_template['baseline_scenarios'])}. "
            f"Follow the test pattern: {framework_template['test_pattern']} "
        )
    else:
        instructions += "No framework template matched; use language baseline only. "

    return {
        "file_path": file_path,
        "language": language,
        "framework": framework,
        "language_baseline": language_baseline,
        "framework_template": framework_template,
        "test_file_path_pattern": (
            framework_template["test_file_path"] if framework_template else None
        ),
        "instructions": instructions,
    }
