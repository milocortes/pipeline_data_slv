library(zoo)
library(xlsx)
library("bpvars")
library("BGVAR")

## Cargamos datos longitudinales
pdata_slv_gdp <- excel_to_list(file = "panel_data_subnacional.xlsx", first_column_as_time=TRUE, skipsheet=NULL)
pdata_slv_gdp_forecast <- excel_to_list(file = "panel_data_subnacional_forecast.xlsx", first_column_as_time=TRUE, skipsheet=NULL)

exogenous_values <- excel_to_list(file = "panel_data_subnacional_exo.xlsx", first_column_as_time=TRUE, skipsheet=NULL)
exogenous_forecast_values <- excel_to_list(file = "panel_data_subnacional_exo_forecast.xlsx", first_column_as_time=TRUE, skipsheet=NULL)

for (i in seq_along(pdata_slv_gdp)) {
  pdata_slv_gdp[[i]] <-ts(data  = pdata_slv_gdp[[i]], start = 2012, frequency = 4)  
}

for (i in seq_along(exogenous_values)) {
  exogenous_values[[i]] <-ts(data  = exogenous_values[[i]], start = 2012, frequency = 4)  
}

for (i in seq_along(pdata_slv_gdp_forecast)) {
  pdata_slv_gdp_forecast[[i]] <-ts(data  = pdata_slv_gdp_forecast[[i]], start = 2023, frequency = 4)  
}

for (i in seq_along(exogenous_forecast_values)) {
  exogenous_forecast_values[[i]] <-ts(data  = exogenous_forecast_values[[i]], start = 2023, frequency = 4)  
}


spec = specify_bvarPANEL$new(                           # specify the model
    pdata_slv_gdp,                                    # data
    stationary = c(FALSE, FALSE, FALSE, FALSE),            # stationarity (determines prior mean)
    exogenous = exogenous_values,
    type = c("real", "real", "real", "real")              # variable types
)

burn = estimate(spec, S = 500, show_progress = TRUE) # run the burn-in
post = estimate(burn, S = 500, show_progress = TRUE) 

fore = forecast(                                 # forecast the model 
  post,
  exogenous_forecast = exogenous_forecast_values,  
  conditional_forecast = pdata_slv_gdp_forecast,    # estimation output
  horizon = 11                                      # forecast horizon
)

#plot(fore, "SLV_1", main = "Forecasts for Colombia")

#summary(fore, "SLV_1")

resultados = data.frame()
### Guardamos resultados
for (i in seq(1:14)) {

  departamento = paste("SLV", i, sep = "_")

  ## Construye datos pronosticados
  datos = as.data.frame(summary(fore, departamento)$variable1)
  datos$departamento = departamento
  datos$datetime = as.Date(pdata_slv_gdp_forecast[[departamento]])

  ## Construye datos historicos
  datetime = as.data.frame(as.Date(pdata_slv_gdp[[departamento]]))
  mean = as.data.frame(pdata_slv_gdp[[departamento]])$gdp
  sd = 0
  lower_quantile = as.data.frame(pdata_slv_gdp[[departamento]])$gdp 
  upper_quantile = as.data.frame(pdata_slv_gdp[[departamento]])$gdp 

  gdp_historico = data.frame(
    datetime,
    mean, 
    sd,
    lower_quantile, 
    upper_quantile
  )

  gdp_historico$departamento = departamento

  names(gdp_historico) = c("datetime", "mean", "sd", "5% quantile", "95% quantile", "departamento")

  datos = rbind.data.frame(gdp_historico, datos)


  resultados = rbind.data.frame(resultados, datos)

}

write.csv(resultados, file = "pronostico_subnacional_departamentos.csv", row.names = FALSE )