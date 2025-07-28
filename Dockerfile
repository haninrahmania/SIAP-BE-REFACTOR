FROM python:3.11-slim

# ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false

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

# RUN ln -sf /lib/x86_64-linux-gnu/libicui18n.so.72 /usr/lib/libicui18n.so || true && \
#     ln -sf /lib/x86_64-linux-gnu/libicuuc.so.72 /usr/lib/libicuuc.so || true && \
#     ln -sf /lib/x86_64-linux-gnu/libicudata.so.72 /usr/lib/libicudata.so || true && \
#     ln -sf /lib/x86_64-linux-gnu/libicui18n.so.72 /usr/lib/x86_64-linux-gnu/libicui18n.so || true && \
#     ln -sf /lib/x86_64-linux-gnu/libicuuc.so.72 /usr/lib/x86_64-linux-gnu/libicuuc.so || true && \
#     ln -sf /lib/x86_64-linux-gnu/libicudata.so.72 /usr/lib/x86_64-linux-gnu/libicudata.so || true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
