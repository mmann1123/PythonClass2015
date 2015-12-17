 tool_exec <- function(in_params, out_params)
{
  arc.progress_label("Loading Packages")
  if (!requireNamespace("stringr", quietly = TRUE))
    install.packages("stringr", dependencies = TRUE)
  if (!requireNamespace("RJSONIO", quietly = TRUE))
    install.packages("RJSONIO", dependencies = TRUE)
  if (!requireNamespace("RCurl", quietly = TRUE))
    install.packages("RCurl", dependencies = TRUE)
  if (!requireNamespace("sp", quietly = TRUE))
    install.packages("sp", dependencies = TRUE)
  require("RCurl")
  require("stringr")
  require("RJSONIO")
  require("sp")
  
  env = arc.env()
  wkspath = env$workspace

  arc.progress_label("Loading Dataset")
  #### Get Input Parameters ####
  input_features = in_params[[2]]
  address = in_params[[3]]
  city = in_params[[4]]
  state = in_params[[5]]
  zip = in_params[[6]]

  out_table = out_params[[1]]

  # Opening Data as an Arc object
  d <- arc.open(input_features)
  # Selecting all fields in object and opening as dataframe
  data <- arc.select(d)
  # Creating a dataframe with only address information
  x <- cbind(data[,address], data[,city], data[,state], data[,zip])
  # Adding column to data table with long form address.
  data$inName <- apply(x,1,paste,collapse=" ")

  ###
  # Creating funtions to use for geocoding
  arc.progress_label("Creating Functions")
  # Contructing the geocode URL to use JSON version of google maps geocoding API
  construct.geocode.url <- function(address, return.call = "json", sensor = "false") {
    root <- "https://maps.google.com/maps/api/geocode/"
    u <- paste(root, return.call, "?address=", address, "&sensor=", sensor, sep = "")
    return(URLencode(u))
  }

  # Creating function to send addresses and recieve geocoding results from Google
  GeoCode <- function(address,verbose=FALSE) {
    if(verbose) cat(address,"\n")
    # Using function from above to create the URL
    u <- construct.geocode.url(address )
    # Opening URL page and storing results
    doc <- getURL(u, ssl.verifypeer = FALSE)
    # Parsing JSON from page into dataframe
    x <- fromJSON(doc,simplify = FALSE)
    # Getting lat/long
    lat <- x$results[[1]]$geometry$location$lat
    lng <- x$results[[1]]$geometry$location$lng
    # Getting status of result
    status <- x$status
    # Getting Geographic level
    level <- x$results[[1]]$types
    # Getting address matched to
    namefound <- x$results[[1]]$formatted_address
    multipleXY = "N"
    if (length(lng)>1 ){ multipleXY = "Y" }
    # Returning list object to be parsed below
    return(list(status = status, levels=level, lat= lat[1], lng= lng[1], multipleXY= multipleXY, namefound = namefound)) 
  }


  ######################################################
  ###############GEOCODE ADDRESSES######################
  ######################################################
  arc.progress_label("Geocoding Addresses")
  # Creating a holder for input addresses
   loc_in = c(data$inName)

  # Creating new dataframe with columns to hold geocoding results
  results = data.frame(data, namefound = "NA", status="NA",level="NA",lat=NA,lon=NA, problem=factor("N", levels=c("Y","N")), stringsAsFactors=F)

  # Looping through addresses to perform geocoding
  for (i in 1:length(loc_in)){
    # Safety step, last second cleaning. Pound symbols in URL breaks the tool.
    # Removing pounds from address in case missed before
    loc_in[i] <- gsub("#", "", loc_in[i])
    # Storing list returned from Geocode function
    result = as.data.frame(GeoCode(loc_in[i]))
    # Printing result to progress table
    print(result)
    # Adding result to dataframe
    results[i,] = c(data[i,],as.character(result[,6]),as.character(result[,c(1)]),as.character(result[,c(2)]),result[,c(3,4)],as.character(result[,5]))
    # Holding loop so per second request limit is not exceeded
    Sys.sleep(2)
  }

  coordinates(results) = ~lon + lat
  resultsSp = arc.sp2data(results)

  arc.progress_label("Sending data back to ArcGIS")
  if (!is.null(out_table) && out_table != "NA")
    arc.write(out_table, resultsSp)

  arc.progress_label("Done!")
  return(out_params)

}




