FROM python:3.11-slim

# ✅ Pastikan .NET Globalization tidak diset invarian
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false

# ✅ Install dependencies: ICU, ASP.NET, LibreOffice, dll
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    ca-certificates \
    libicu-dev \
    icu-devtools \
    libc6-dev \
    libreoffice \
    && curl https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -o packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y aspnetcore-runtime-7.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Symlink ICU libraries agar .NET runtime bisa menemukannya di lokasi yang dicari
RUN ln -sf /lib/x86_64-linux-gnu/libicui18n.so.72 /usr/lib/libicui18n.so || true && \
    ln -sf /lib/x86_64-linux-gnu/libicuuc.so.72 /usr/lib/libicuuc.so || true && \
    ln -sf /lib/x86_64-linux-gnu/libicudata.so.72 /usr/lib/libicudata.so || true && \
    ln -sf /lib/x86_64-linux-gnu/libicui18n.so.72 /usr/lib/x86_64-linux-gnu/libicui18n.so || true && \
    ln -sf /lib/x86_64-linux-gnu/libicuuc.so.72 /usr/lib/x86_64-linux-gnu/libicuuc.so || true && \
    ln -sf /lib/x86_64-linux-gnu/libicudata.so.72 /usr/lib/x86_64-linux-gnu/libicudata.so || true


# Set working directory
WORKDIR /app

# Copy dan install Python dependencies terlebih dahulu (agar cache optimal)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua source code ke dalam container
COPY . .

# Jalankan aplikasi Django dengan Gunicorn
CMD gunicorn project_django.wsgi:application --bind 0.0.0.0:8000