import logging

logger = logging.getLogger(__name__)


def configure_sentry() -> None:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        )
        logger.info("Sentry initialized for environment: %s", settings.environment)
    except ImportError:
        logger.warning("sentry-sdk not installed; Sentry disabled")


def configure_tracing() -> None:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.otel_enabled:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider()
        if settings.otel_endpoint:
            exporter = OTLPSpanExporter(endpoint=settings.otel_endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument()
        logger.info("OpenTelemetry tracing enabled; endpoint=%s", settings.otel_endpoint)
    except ImportError:
        logger.warning("opentelemetry packages not installed; tracing disabled")
