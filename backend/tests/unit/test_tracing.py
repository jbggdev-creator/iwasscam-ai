import sys
from unittest.mock import MagicMock, patch


class TestConfigureSentry:
    def test_returns_early_when_sentry_dsn_not_set(self):
        mock_settings = MagicMock()
        mock_settings.sentry_dsn = ""
        with patch("app.core.config.get_settings", return_value=mock_settings):
            from app.core.tracing import configure_sentry
            configure_sentry()

    def test_initializes_sentry_when_dsn_is_set(self):
        mock_settings = MagicMock()
        mock_settings.sentry_dsn = "https://fake@sentry.io/1"
        mock_settings.environment = "test"

        mock_sentry = MagicMock()
        mock_fastapi_integration = MagicMock()
        mock_sqlalchemy_integration = MagicMock()

        mock_sentry_integrations_fastapi = MagicMock()
        mock_sentry_integrations_fastapi.FastApiIntegration = mock_fastapi_integration
        mock_sentry_integrations_sqlalchemy = MagicMock()
        mock_sentry_integrations_sqlalchemy.SqlalchemyIntegration = mock_sqlalchemy_integration

        with patch("app.core.config.get_settings", return_value=mock_settings):
            with patch.dict(
                sys.modules,
                {
                    "sentry_sdk": mock_sentry,
                    "sentry_sdk.integrations": MagicMock(),
                    "sentry_sdk.integrations.fastapi": mock_sentry_integrations_fastapi,
                    "sentry_sdk.integrations.sqlalchemy": mock_sentry_integrations_sqlalchemy,
                },
            ):
                from app.core import tracing
                import importlib
                importlib.reload(tracing)
                tracing.configure_sentry()

        mock_sentry.init.assert_called_once()

    def test_handles_sentry_import_error_gracefully(self):
        mock_settings = MagicMock()
        mock_settings.sentry_dsn = "https://fake@sentry.io/1"

        with patch("app.core.config.get_settings", return_value=mock_settings):
            with patch.dict(sys.modules, {"sentry_sdk": None}):
                from app.core.tracing import configure_sentry
                configure_sentry()


class TestConfigureTracing:
    def test_returns_early_when_otel_disabled(self):
        mock_settings = MagicMock()
        mock_settings.otel_enabled = False
        with patch("app.core.config.get_settings", return_value=mock_settings):
            from app.core.tracing import configure_tracing
            configure_tracing()
        mock_settings  # no opentelemetry calls expected

    def test_initializes_otel_when_enabled_with_endpoint(self):
        mock_settings = MagicMock()
        mock_settings.otel_enabled = True
        mock_settings.otel_endpoint = "http://localhost:4318/v1/traces"

        mock_trace = MagicMock()
        mock_provider = MagicMock()
        mock_tracer_provider_cls = MagicMock(return_value=mock_provider)
        mock_exporter_cls = MagicMock()
        mock_processor_cls = MagicMock()
        mock_instrumentor = MagicMock()

        mock_otel = MagicMock()
        mock_otel.trace = mock_trace

        mock_otel_sdk_trace = MagicMock()
        mock_otel_sdk_trace.TracerProvider = mock_tracer_provider_cls

        mock_otel_sdk_trace_export = MagicMock()
        mock_otel_sdk_trace_export.BatchSpanProcessor = mock_processor_cls

        mock_exporter_mod = MagicMock()
        mock_exporter_mod.OTLPSpanExporter = mock_exporter_cls

        mock_fastapi_instr = MagicMock()
        mock_fastapi_instr.FastAPIInstrumentor = mock_instrumentor

        with patch("app.core.config.get_settings", return_value=mock_settings):
            with patch.dict(
                sys.modules,
                {
                    "opentelemetry": mock_otel,
                    "opentelemetry.trace": mock_trace,
                    "opentelemetry.sdk": MagicMock(),
                    "opentelemetry.sdk.trace": mock_otel_sdk_trace,
                    "opentelemetry.sdk.trace.export": mock_otel_sdk_trace_export,
                    "opentelemetry.exporter": MagicMock(),
                    "opentelemetry.exporter.otlp": MagicMock(),
                    "opentelemetry.exporter.otlp.proto": MagicMock(),
                    "opentelemetry.exporter.otlp.proto.http": MagicMock(),
                    "opentelemetry.exporter.otlp.proto.http.trace_exporter": mock_exporter_mod,
                    "opentelemetry.instrumentation": MagicMock(),
                    "opentelemetry.instrumentation.fastapi": mock_fastapi_instr,
                },
            ):
                from app.core import tracing
                import importlib
                importlib.reload(tracing)
                tracing.configure_tracing()

        mock_tracer_provider_cls.assert_called_once()

    def test_handles_otel_import_error_gracefully(self):
        mock_settings = MagicMock()
        mock_settings.otel_enabled = True
        mock_settings.otel_endpoint = ""

        with patch("app.core.config.get_settings", return_value=mock_settings):
            with patch.dict(sys.modules, {"opentelemetry": None}):
                from app.core.tracing import configure_tracing
                configure_tracing()
