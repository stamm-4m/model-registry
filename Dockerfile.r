# Base image
FROM rocker/r-ver:4.3.3

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (including Java)
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libgit2-dev \
    libsodium-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    libcairo2-dev \
    libtiff5-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    default-jdk \
    wget \
    unzip \
    libx11-dev \
    pkg-config \
    libbz2-dev \
    liblzma-dev \
 && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME dynamically
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Configure Java for R
RUN R CMD javareconf

# Install rJava first
RUN R -e "install.packages('rJava', repos='https://cloud.r-project.org')"

# Install remaining packages
RUN R -e "install.packages(c('RWeka','plumber','yaml','jsonlite','ranger','Cubist'), repos='https://cloud.r-project.org')"

# Copy API
WORKDIR /app
COPY model_registry/api/services/r/app.R /app/app.R

# IMPORTANT: must match docker-compose
EXPOSE 8501

CMD ["Rscript", "-e", "pr <- plumber::plumb('app.R'); pr$run(host='0.0.0.0', port=8501)"]
