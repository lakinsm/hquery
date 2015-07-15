pivotReport <- function(inputReport, outputReport){
    
    if(!require(dplyr)){
        print("Attempting to install package dplyr")
        install.packages("dplyr")
        library(dplyr)
    }
    if(!require(tidyr)){
        print("Attempting to install package tidyr")
        install.packages("tidyr")
        library(tidyr)
    }
    if(!require(stringr)){
        print("Attempting to install package stringr")
        install.packages("stringr")
        library(stringr)
    }
    if(!require(openxlsx)){
        print("Attempting to install package openxlsx")
        install.packages("openxlsx")
        library(openxlsx)
    }
    if(!require(xlsx)){
        print("Attempting to install package xlsx")
        install.packages("xlsx")
        library(xlsx)
    }
    
    df <- openxlsx::read.xlsx(inputReport, sheet = 2)

    pivot1 <- df %>% 
        group_by(Concept_Name, Concept_Code, Gene_Nomenclature_Symbol, Gene_Map_Location, Full_Synonym) %>%
        mutate(n=paste("Gene_Chromosome_Location#",str_pad(row_number(), 2, pad="0"), sep="")) %>%
        spread(n, Gene_Chromosome_Location)
    
    pivot2 <- pivot1 %>% 
        group_by(Concept_Name, Concept_Code, Gene_Nomenclature_Symbol, Gene_Map_Location) %>%
        mutate(n=paste("Full_Synonym#",str_pad(row_number(), 2, pad="0"), sep="")) %>%
        spread(n, Full_Synonym)
    
    locations <- names(pivot2)[grepl('Chromosome_Location', names(pivot2))]
    
    synonyms <- names(pivot2)[grepl('Synonym', names(pivot2))]
    
    colOrder <- c('Concept_Name', 'Concept_Code', 'Gene_Nomenclature_Symbol', locations, 'Gene_Map_Location', synonyms)
    
    pivot2 <- as.data.frame(pivot2[,colOrder])
    
    xlsx::write.xlsx(pivot2, outputReport, row.names=FALSE, showNA=FALSE)
    
}
