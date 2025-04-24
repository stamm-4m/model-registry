# =============================================================================
# R Script for Machine Learning Model API
# Author: David Camilo Corrales
# Email: David-Camilo.Corrales-Munoz@inrae.fr
# Date: 2025-03-18
# =============================================================================

required_packages <- c("plumber", "RWeka", "Cubist", "rJava", "ranger", "yaml", "jsonlite")

install_if_missing <- function(package) {
  if (!require(package, character.only = TRUE)) {
    install.packages(package)
  }
}

sapply(required_packages, install_if_missing)