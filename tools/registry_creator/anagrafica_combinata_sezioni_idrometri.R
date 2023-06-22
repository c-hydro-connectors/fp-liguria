
# script che associa le anagrafiche di sezioni ----------------------------
# di modellazione e delle dighe

anagrafica_combinata_sezioni_idrometri <- function(){
  
  library(sp)
  library(geosphere)
  
  
  dDist <- 2 #  2 m di tolleranza per trovare la corrispondenza sezione modellazione - diga; u.d.m [m]
  
  sPathScriptComuni <- '/home/cfmi.arpal.org/idro/ScriptComuni/'
  sPathAnag <- paste0(sPathScriptComuni,'anagrafica_combinata_sezioni_idrometri/')
  sPathAnagDRiFt <- paste0(sPathScriptComuni,'anagrafica_sezioni_modellazione/')
  sPathAnagIdr <- paste0(sPathScriptComuni,'anagrafica_idrometri/')
  
  
  # carico anagrafica sezioni di modellazione -------------------------------
  
  sNameFileAnagDRiFt <- paste0(sPathAnagDRiFt,'AnagraficaSezioniModellazioneDRiFt.txt')
  source(paste0(sPathAnagDRiFt,"carica_anagrafica_sezioniDRiFt.R"))
  AnagSez <- carica_anagrafica_sezioniDRiFt(sNameFileAnagDRiFt)[[2]]
  nSez <- dim(AnagSez$a1sCodeSect)[1]
  

# carico anagrafica idrometri ---------------------------------------------

  sNameFileAnagIdr <- paste0(sPathAnagIdr,'AnagraficaIdrometri.txt')
  source(paste0(sPathAnagIdr,"carica_anagrafica_idrometri.R"))
  AnagIdr <- carica_anagrafica_idrometri(sNameFileAnagIdr)[[2]]
  
# determino corrispondenza sezione modellazione - idrometro ---------------

  SpaSez <- data.frame(AnagSez[,c('a1sCodeSect','a1dLon','a1dLat')], stringsAsFactors = F)
  coordinates(SpaSez) <- ~a1dLon+a1dLat
  
  SpaIdr <- data.frame(AnagIdr[,c('a1sCodeIdr','a1dLonIdr','a1dLatIdr')], stringsAsFactors = F)
  coordinates(SpaIdr) <- ~a1dLonIdr+a1dLatIdr
  
  dDistDiff <- distm(SpaIdr,SpaSez)
  
  colnames(dDistDiff) <- SpaSez$a1sCodeSect
  rownames(dDistDiff) <- SpaIdr$a1sCodeIdr
  
  list_code_par <- which(dDistDiff<=dDist, arr.ind = T)
  
  AnagSez[,c("a1sCodeIdr",
             "a1dLatIdr",
             "a1dLonIdr",
             "a1dHZeroIdr",
             "a1dYpresogl",
             "a1dYguard",
             "a1dYesond",
             "a1dDt")] <-NA
  
  AnagSez[list_code_par[,"col"],c("a1sCodeIdr",
             "a1dLatIdr",
             "a1dLonIdr",
             "a1dHZeroIdr",
             "a1dYpresogl",
             "a1dYguard",
             "a1dYesond",
             "a1dDt")] <- AnagIdr[list_code_par[,"row"],c("a1sCodeIdr",
                                                          "a1dLatIdr",
                                                          "a1dLonIdr",
                                                          "a1dHZeroIdr",
                                                          "a1dYpresogl",
                                                          "a1dYguard",
                                                          "a1dYesond",
                                                          "a1dDt")]
  
  
  
  return(AnagSez)
  
}