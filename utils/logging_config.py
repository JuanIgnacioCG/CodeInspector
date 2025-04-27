import logging

def setup_logging(level=logging.DEBUG):
    """Setup global logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.getLogger('streamlit').setLevel(logging.WARNING)  # Silence noisy logs if you want
