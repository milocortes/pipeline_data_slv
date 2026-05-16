## Instala paquete remotes para poder instalar una versión específica de las dependencias
install.packages("remotes")
library(remotes)

install_version("xlsx", "0.6.5") 
install_version("zoo", "1.8.15") 
install_version("BGVAR", "2.5.9") 
install_version("bpvars", "1.0") 


