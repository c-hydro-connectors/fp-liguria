
# script che associa le anagrafiche di sezioni ----------------------------
# di modellazione e delle dighe


  
  library(sp)
  library(geosphere)
  library(dplyr)
  
  dDist <- 2 #  2 m di tolleranza per trovare la corrispondenza sezione modellazione - diga; u.d.m [m]
  
  sPathOut <- '/home/cfmi.arpal.org/idro/FloodScenario/library/tools/anagrafica/'
  sPathScriptComuni <- '/home/cfmi.arpal.org/idro/ScriptComuni/'
  sPathAnag <- paste0(sPathScriptComuni,'anagrafica_combinata_sezioni_idrometri/')
  sPathAnagDRiFt <- paste0(sPathScriptComuni,'anagrafica_sezioni_modellazione/')
  sPathAnagIdr <- paste0(sPathScriptComuni,'anagrafica_idrometri/')
  
  
  source(paste0(sPathAnag,"anagrafica_combinata_sezioni_idrometri.R"))
  AnagSez <- anagrafica_combinata_sezioni_idrometri()
  
  my_data <- AnagSez %>% select(1,24)
  #my_data2 <- my_data[my_data[,2] != "NA",]
#seleziona righe
  my_data2 <- subset(my_data, a1sCodeIdr != "NA")

  fileName <- paste0(sPathOut,"SezioniLiguriaRegistry.csv")
  write.table(AnagSez,fileName,sep=";",quote=FALSE,row.names=FALSE)
  
