# Base image
FROM rocker/r-ver:4.3.3

ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# System dependencies
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
    openjdk-11-jdk \
    wget \
    unzip \
    libx11-dev \
    pkg-config \
    libbz2-dev \
    liblzma-dev \
 && rm -rf /var/lib/apt/lists/*

# Install rJava first
RUN R -e "install.packages('rJava', repos='https://cloud.r-project.org', dependencies=TRUE, INSTALL_opts='--no-test-load')"

# Then install remaining packages
RUN R -e "install.packages(c('RWeka','plumber','yaml','jsonlite','ranger','Cubist'), repos='https://cloud.r-project.org', dependencies=TRUE, INSTALL_opts='--no-test-load')"

# Copy API
WORKDIR /app
COPY core/services/r/app.R /app/app.R

EXPOSE 8081

CMD ["Rscript", "-e", "pr <- plumber::plumb('app.R'); pr$run(host='0.0.0.0', port=8081)"]
