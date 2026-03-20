# =============================================================================
# R Script for Machine Learning Model API
# Author: David Camilo Corrales and Carlos Suarez
# Update: 2026-02-19
# =============================================================================
required_packages <- c("plumber", "RWeka", "Cubist", "rJava", "ranger", "yaml", "jsonlite")

# Force user library
user_lib <- Sys.getenv("R_LIBS_USER")
dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(user_lib)

install_if_missing <- function(package) {
  if (!require(package, character.only = TRUE, quietly = TRUE)) {
    install.packages(package, repos = "https://cloud.r-project.org")
  }
}

invisible(sapply(required_packages, install_if_missing))
