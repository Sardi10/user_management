# --------- BUILD STAGE ---------
    FROM python:3.12-bookworm AS base

    # environment
    ENV PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        PIP_NO_CACHE_DIR=true \
        PIP_DEFAULT_TIMEOUT=100 \
        PIP_DISABLE_PIP_VERSION_CHECK=on \
        QR_CODE_DIR=/myapp/qr_codes
    
    WORKDIR /myapp
    
    # install system deps + patched libc-bin in one go
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
          --allow-downgrades \
          gcc \
          libpq-dev \
          libc-bin=2.36-9+deb12u7 && \
        rm -rf /var/lib/apt/lists/*
    
    # create venv and install Python deps
    COPY requirements.txt .
    RUN python -m venv /.venv && \
        /.venv/bin/pip install --upgrade pip && \
        /.venv/bin/pip install -r requirements.txt
    
    # --------- RUNTIME STAGE ---------
    FROM python:3.12-slim-bookworm AS final
    
    # apply same libc-bin patch
    RUN apt-get update && \
        apt-get install -y --allow-downgrades libc-bin=2.36-9+deb12u7 && \
        rm -rf /var/lib/apt/lists/*
    
    # copy in the virtualenv
    COPY --from=base /.venv /.venv
    
    # ensure venv is on PATH
    ENV PATH="/.venv/bin:$PATH" \
        PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        QR_CODE_DIR=/myapp/qr_codes
    
    WORKDIR /myapp
    
    # drop to non-root
    RUN useradd -m myuser
    USER myuser
    
    # copy application code
    COPY --chown=myuser:myuser . .
    
    EXPOSE 8000
    
    ENTRYPOINT ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    